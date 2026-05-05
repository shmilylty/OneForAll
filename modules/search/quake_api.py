import time

from config import settings
from common.search import Search
from common.module_status import ModuleRunStatus

class Quake(Search):
    def __init__(self, domain):
        Search.__init__(self)
        self.domain = domain
        self.module = 'Quake'
        self.source = "QuakeAPISearch"
        self.addr = 'https://quake.360.net/api/v3/search/quake_service'
        self.delay = 1
        self.key = settings.quake_api_key
        self.status = ModuleRunStatus.SKIPPED

    def search(self):
        """
        发送搜索请求并做子域匹配
        """
        if not self.key:
            self.status = ModuleRunStatus.AUTH_FAILED
            return
            
        self.per_page_num = 100
        self.page_num = 0
        while True:
            time.sleep(self.delay)
            self.header = self.get_header()
            self.header.update({'Content-Type': 'application/json'})
            self.header.update({'X-QuakeToken': self.key})
            self.proxy = self.get_proxy(self.source)

            query = {'query': 'domain:"' + self.domain + '"',
                     'start': self.page_num * self.per_page_num,
                     'size': self.per_page_num,
                     'include': [
                         "ip", "port", "transport", "service.name", 
                         "service.http.host", "service.http.title", 
                         "service.http.server", "service.http.status_code", 
                         "service.http.favicon.hash", "service.tls.cert.subject.cn", 
                         "service.tls.cert.subject.alt_names"
                     ]}
                     
            resp = self.post(self.addr, json=query, check=False, ignore=True)
            if not resp:
                self.status = ModuleRunStatus.NETWORK_ERROR
                return
                
            if resp.status_code in [401, 403]:
                self.status = ModuleRunStatus.AUTH_FAILED
                return
            elif resp.status_code == 402:
                self.status = ModuleRunStatus.QUOTA_EXCEEDED
                return
            elif resp.status_code == 429:
                self.status = ModuleRunStatus.RATE_LIMITED
                return
                
            try:
                resp_json = resp.json()
            except Exception:
                self.status = ModuleRunStatus.PARSE_ERROR
                return

            if resp_json.get('code') != 0:
                msg = resp_json.get('message', '')
                if 'token无效' in msg or '没有token' in msg:
                    self.status = ModuleRunStatus.AUTH_FAILED
                elif '额度不足' in msg:
                    self.status = ModuleRunStatus.QUOTA_EXCEEDED
                else:
                    self.status = ModuleRunStatus.FAILED
                return

            data = resp_json.get('data', [])
            if not data:
                if not self.subdomains:
                    self.status = ModuleRunStatus.EMPTY
                else:
                    self.status = ModuleRunStatus.SUCCESS
                break

            for item in data:
                service = item.get('service', {})
                http = service.get('http', {})
                host = http.get('host', '')
                if host and host.endswith(self.domain):
                    self.subdomains.add(host.lstrip('*.'))
                
                tls = service.get('tls', {})
                cert = tls.get('cert', {})
                subject = cert.get('subject', {})
                
                cn = subject.get('cn', '')
                if cn and cn.endswith(self.domain):
                    self.subdomains.add(cn.lstrip('*.'))
                    
                alt_names = subject.get('alt_names', [])
                if not alt_names:
                    alt_names = cert.get('subject_alt_names', [])
                    
                for san in alt_names:
                    if san and san.endswith(self.domain):
                        self.subdomains.add(san.lstrip('*.'))

            self.status = ModuleRunStatus.SUCCESS
            meta = resp_json.get('meta', {})
            pagination = meta.get('pagination', {})
            total = pagination.get('total', 0)
            self.page_num += 1
            if self.page_num * self.per_page_num >= int(total):
                break

    def run(self):
        """
        类执行入口
        """
        if not self.have_api(self.key):
            self.status = ModuleRunStatus.SKIPPED
            return
        self.begin()
        self.search()
        self.finish()
        self.save_json()
        self.gen_result()
        self.save_db()

def run(domain):
    """
    类统一调用入口

    :param str domain: 域名
    """
    query = Quake(domain)
    query.run()

if __name__ == '__main__':
    run('nosugartech.com')
