import time
from config import settings
from common.query import Query
from common.module_status import ModuleRunStatus

class SecurityTrailsAPI(Query):
    def __init__(self, domain):
        Query.__init__(self)
        self.domain = domain
        self.module = 'Dataset'
        self.source = 'SecurityTrailsAPIQuery'
        self.addr = 'https://api.securitytrails.com/v1/domain/'
        self.api = settings.securitytrails_api
        self.delay = 2  # SecurityTrails查询时延至少2秒
        self.status = ModuleRunStatus.SKIPPED

    def query(self):
        """
        向接口查询子域并做子域匹配
        """
        if not self.api:
            self.status = ModuleRunStatus.AUTH_FAILED
            return
            
        time.sleep(self.delay)
        self.header = self.get_header()
        self.proxy = self.get_proxy(self.source)
        params = {'apikey': self.api}
        url = f'{self.addr}{self.domain}/subdomains'
        
        resp = self.get(url, params, check=False, ignore=True)
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
            
        prefixs = resp_json.get('subdomains', [])
        if not prefixs:
            self.status = ModuleRunStatus.EMPTY
            return
            
        subdomains = [f'{prefix}.{self.domain}' for prefix in prefixs]
        if subdomains:
            self.subdomains.update(subdomains)
            self.status = ModuleRunStatus.SUCCESS
        else:
            self.status = ModuleRunStatus.EMPTY

    def run(self):
        """
        类执行入口
        """
        if not self.have_api(self.api):
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
    query = SecurityTrailsAPI(domain)
    query.run()

if __name__ == '__main__':
    run('example.com')
