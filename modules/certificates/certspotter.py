from common.query import Query
from common.module_status import ModuleRunStatus

class CertSpotter(Query):
    def __init__(self, domain):
        Query.__init__(self)
        self.domain = domain
        self.module = 'Certificate'
        self.source = 'CertSpotterQuery'
        self.addr = 'https://api.certspotter.com/v1/issuances'
        self.status = ModuleRunStatus.SKIPPED

    def query(self):
        """
        向接口查询子域并做子域匹配
        """
        self.header = self.get_header()
        self.proxy = self.get_proxy(self.source)
        params = {'domain': self.domain,
                  'include_subdomains': 'true',
                  'expand': 'dns_names'}
        resp = self.get(self.addr, params, check=False, ignore=True)
        if not resp:
            self.status = ModuleRunStatus.NETWORK_ERROR
            return
            
        if resp.status_code == 429:
            self.status = ModuleRunStatus.RATE_LIMITED
            return
        elif resp.status_code == 401 or resp.status_code == 403:
            self.status = ModuleRunStatus.AUTH_FAILED
            return
        elif resp.status_code != 200:
            self.status = ModuleRunStatus.FAILED
            return
            
        try:
            jsonData = resp.json()
        except Exception:
            self.status = ModuleRunStatus.PARSE_ERROR
            return
            
        if not jsonData:
            self.status = ModuleRunStatus.EMPTY
            return
            
        for item in jsonData:
            dns_names = item.get('dns_names', [])
            for name in dns_names:
                name = name.lstrip('*.')
                if name and name.endswith(self.domain):
                    self.subdomains.add(name)

        if self.subdomains:
            self.status = ModuleRunStatus.SUCCESS
        else:
            self.status = ModuleRunStatus.EMPTY

    def run(self):
        """
        类执行入口
        """
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
    query = CertSpotter(domain)
    query.run()

if __name__ == '__main__':
    run('example.com')
