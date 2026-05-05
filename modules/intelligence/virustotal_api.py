import time
from config import settings
from common.query import Query
from common.module_status import ModuleRunStatus

class VirusTotalAPI(Query):
    def __init__(self, domain):
        Query.__init__(self)
        self.domain = domain
        self.module = 'Intelligence'
        self.source = 'VirusTotalAPIQuery'
        self.key = settings.virustotal_api_key
        self.status = ModuleRunStatus.SKIPPED

    def query(self):
        """
        向接口查询子域并做子域匹配
        """
        if not self.key:
            self.status = ModuleRunStatus.AUTH_FAILED
            return
            
        next_cursor = ''
        while True:
            self.header = self.get_header()
            self.header.update({'x-apikey': self.key})
            self.proxy = self.get_proxy(self.source)
            params = {'limit': '40', 'cursor': next_cursor} if next_cursor else {'limit': '40'}
            addr = f'https://www.virustotal.com/api/v3/domains/{self.domain}/subdomains'
            
            resp = self.get(url=addr, params=params, check=False, ignore=True)
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
                
            subdomains = self.match_subdomains(resp.text)
            if subdomains:
                self.subdomains.update(subdomains)
            
            next_cursor = data.get('meta', {}).get('cursor')
            if not next_cursor:
                if not self.subdomains:
                    self.status = ModuleRunStatus.EMPTY
                else:
                    self.status = ModuleRunStatus.SUCCESS
                break

    def run(self):
        """
        类执行入口
        """
        if not self.have_api(self.key):
            self.status = ModuleRunStatus.SKIPPED
            return
        self.begin()
        self.query()
        self.finish()
        self.save_json()
        self.gen_result()
        self.save_db()

def run(domain):
    """
    类统一调用入口

    :param str domain: 域名
    """
    query = VirusTotalAPI(domain)
    query.run()

if __name__ == '__main__':
    run('mi.com')
