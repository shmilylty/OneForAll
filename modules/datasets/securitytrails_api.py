from config import settings
from common.query import Query


class SecurityTrailsAPI(Query):
    def __init__(self, domain):
        Query.__init__(self)
        self.domain = domain
        self.module = 'Dataset'
        self.source = 'SecurityTrailsAPIQuery'
        self.addr = 'https://api.securitytrails.com/v1/domain/'
        self.api = settings.securitytrails_api
        self.delay = 2  # SecurityTrails查询时延至少2秒

    def query(self):
        """
        向接口查询子域并做子域匹配
        """
        self.header = self.get_header()
        self.proxy = self.get_proxy(self.source)
        params = {'apikey': self.api}
        url = f'{self.addr}{self.domain}/subdomains'
        resp = self.get(url, params)
        if not resp:
            return
        prefixs = resp.json()['subdomains']
        subdomains = [f'{prefix}.{self.domain}' for prefix in prefixs]
        if subdomains:
            self.subdomains.update(subdomains)

    def run(self):
        """
        类执行入口
        """
        if not self.have_api(self.api):
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
