import time
from config import settings
from common.search import Search
from common.module_status import ModuleRunStatus

class ShodanAPI(Search):
    def __init__(self, domain):
        Search.__init__(self)
        self.domain = domain
        self.module = 'Search'
        self.source = 'ShodanAPISearch'
        self.key = settings.shodan_api_key
        self.status = ModuleRunStatus.SKIPPED

    def search(self):
        """
        发送搜索请求并做子域匹配
        """
        if not self.key:
            self.status = ModuleRunStatus.AUTH_FAILED
            return
            
        self.header = self.get_header()
        self.proxy = self.get_proxy(self.source)
        url = f'https://api.shodan.io/dns/domain/{self.domain}?key={self.key}'
        
        resp = self.get(url, check=False, ignore=True)
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
            data = resp.json()
        except Exception:
            self.status = ModuleRunStatus.PARSE_ERROR
            return
            
        names = data.get('subdomains', [])
        if not names:
            self.status = ModuleRunStatus.EMPTY
            return
            
        subdomain_str = str(set(map(lambda name: f'{name}.{self.domain}', names)))
        self.subdomains = self.collect_subdomains(subdomain_str)
        if self.subdomains:
            self.status = ModuleRunStatus.SUCCESS
        else:
            self.status = ModuleRunStatus.EMPTY

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
    search = ShodanAPI(domain)
    search.run()

if __name__ == '__main__':
    run('freebuf.com')
