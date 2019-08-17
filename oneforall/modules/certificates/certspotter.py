import time
from common import utils
from common.query import Query


class CertSpotter(Query):
    def __init__(self, domain):
        Query.__init__(self)
        self.domain = domain
        self.module = 'Certificate'
        self.source = 'CertSpotterQuery'
        self.addr = 'https://api.certspotter.com/v1/issuances'

    def query(self):
        """
        向接口查询子域并做子域匹配
        """
        time.sleep(self.delay)
        self.header = self.get_header()
        self.proxy = self.get_proxy(self.source)
        params = {'domain': self.domain,
                  'include_subdomains': 'true',
                  'expand': 'dns_names'}
        resp = self.get(self.addr, params)
        if not resp:
            return
        subdomains = utils.match_subdomain(self.domain, str(resp.json()))
        # 合并搜索子域名搜索结果
        self.subdomains = self.subdomains.union(subdomains)

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


def do(domain):  # 统一入口名字 方便多线程调用
    """
    类统一调用入口

    :param str domain: 域名

    """
    query = CertSpotter(domain)
    query.run()


if __name__ == '__main__':
    do('example.com')
