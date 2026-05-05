import base64
import time
import urllib.parse

from config import settings
from common.search import Search
from common.module_status import ModuleRunStatus

class FoFa(Search):
    def __init__(self, domain):
        Search.__init__(self)
        self.domain = domain
        self.module = 'Search'
        self.source = 'FoFaAPISearch'
        self.addr = 'https://fofa.info/api/v1/search/all'
        self.delay = 1
        self.email = settings.fofa_api_email
        self.key = settings.fofa_api_key
        self.status = ModuleRunStatus.SKIPPED

    def search(self):
        """
        发送搜索请求并做子域匹配
        """
        if not self.email or not self.key:
            self.status = ModuleRunStatus.AUTH_FAILED
            return

        self.page_num = 1
        subdomain_encode = f'domain="{self.domain}"'.encode('utf-8')
        query_data = base64.b64encode(subdomain_encode).decode('utf-8')
        
        while True:
            time.sleep(self.delay)
            self.header = self.get_header()
            self.proxy = self.get_proxy(self.source)
            query = {'email': self.email,
                     'key': self.key,
                     'qbase64': query_data,
                     'page': self.page_num,
                     'full': 'true',
                     'size': 1000,
                     'fields': 'host,ip,port,protocol,domain,title,server,country,city'}
            
            resp = self.get(self.addr, query, check=False, ignore=True)
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
            elif resp.status_code != 200:
                self.status = ModuleRunStatus.FAILED
                return
                
            try:
                resp_json = resp.json()
            except Exception:
                self.status = ModuleRunStatus.PARSE_ERROR
                return

            if resp_json.get('error'):
                self.status = ModuleRunStatus.FAILED
                return

            results = resp_json.get('results', [])
            if not results:
                if not self.subdomains:
                    self.status = ModuleRunStatus.EMPTY
                else:
                    self.status = ModuleRunStatus.SUCCESS
                break

            for item in results:
                host = item[0]
                if host.startswith('http'):
                    parsed = urllib.parse.urlparse(host)
                    host = parsed.hostname
                if host and host.endswith(self.domain):
                    self.subdomains.add(host)

            self.status = ModuleRunStatus.SUCCESS
            size = resp_json.get('size', 0)
            if self.page_num * 1000 >= size:
                break
            self.page_num += 1

    def run(self):
        """
        类执行入口
        """
        if not self.have_api(self.email, self.key):
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
    search = FoFa(domain)
    search.run()

if __name__ == '__main__':
    run('example.com')
