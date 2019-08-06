import config
from common.query import Query


class RiskIQ(Query):
    def __init__(self, domain):
        Query.__init__(self)
        self.domain = self.register(domain)
        self.module = 'Intelligence'
        self.source = 'RiskIQQuery'
        self.addr = 'https://api.passivetotal.org/v2/enrichment/subdomains'
        self.user = config.riskiq_api_username
        self.key = config.riskiq_api_key

    def query(self):
        """
        向接口查询子域并做子域匹配
        """
        self.header = self.get_header()
        self.proxy = self.get_proxy(self.source)
        params = {'query': self.domain}
        resp = self.get(url=self.addr, params=params, auth=(self.user, self.key))
        if not resp:
            return
        resp_json = resp.json()
        subdomains_find = resp_json.get('subdomains')
        if subdomains_find:
            self.subdomains = set(map(lambda x: x + '.' + self.domain, subdomains_find))

    def run(self):
        """
        类执行入口
        """
        if not self.check(self.user, self.key):
            return
        self.begin()
        self.query()
        self.save_json()
        self.gen_result()
        self.save_db()
        self.finish()


def do(domain):  # 统一入口名字 方便多线程调用
    """
    类统一调用入口

    :param str domain: 域名
    """
    query = RiskIQ(domain)
    query.run()


if __name__ == '__main__':
    do('example.com')
