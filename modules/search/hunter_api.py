import base64
import time
import urllib.parse

from config import settings
from common.search import Search
from common.module_status import ModuleRunStatus

class Hunter(Search):
    def __init__(self, domain):
        Search.__init__(self)
        self.domain = domain
        self.module = 'Search'
        self.source = 'HunterAPISearch'
        self.addr = 'https://hunter.qianxin.com/openApi/search'
        self.delay = 1
        self.key = settings.hunter_api_key
        self.status = ModuleRunStatus.SKIPPED

    def search(self):
        """
        发送搜索请求并做子域匹配
        """
        if not self.key:
            self.status = ModuleRunStatus.AUTH_FAILED
            return
            
        self.page_num = 1
        subdomain_encode = f'domain_suffix="{self.domain}"'.encode('utf-8')
        query_data = base64.urlsafe_b64encode(subdomain_encode).decode('utf-8')
        
        while True:
            time.sleep(self.delay)
            self.header = self.get_header()
            self.proxy = self.get_proxy(self.source)
            query = {'api-key': self.key,
                     'search': query_data,
                     'page': self.page_num,
                     'page_size': 100,
                     'is_web': 1}
                     
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
                
            try:
                resp_json = resp.json()
            except Exception:
                self.status = ModuleRunStatus.PARSE_ERROR
                return

            if resp_json.get('code') != 200:
                msg = resp_json.get('message', '')
                if '积分不足' in msg:
                    self.status = ModuleRunStatus.QUOTA_EXCEEDED
                else:
                    self.status = ModuleRunStatus.FAILED
                return

            data = resp_json.get('data')
            if not data or not data.get('arr'):
                if not self.subdomains:
                    self.status = ModuleRunStatus.EMPTY
                else:
                    self.status = ModuleRunStatus.SUCCESS
                break

            arr = data.get('arr', [])
            for item in arr:
                url = item.get('url', '')
                domain = item.get('domain', '')
                
                if domain and domain.endswith(self.domain):
                    self.subdomains.add(domain)
                
                if url:
                    if url.startswith('http'):
                        parsed = urllib.parse.urlparse(url)
                        hostname = parsed.hostname
                    else:
                        hostname = url.split(':')[0]
                    if hostname and hostname.endswith(self.domain):
                        self.subdomains.add(hostname)

            self.status = ModuleRunStatus.SUCCESS
            total = data.get('total', 0)
            if self.page_num * 100 >= int(total):
                break
            self.page_num += 1

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
    search = Hunter(domain)
    search.run()

if __name__ == '__main__':
    run('freebuf.com')
