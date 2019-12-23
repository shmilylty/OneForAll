from common.query import Query


class AlienVault(Query):
    def __init__(self, domain):
        Query.__init__(self)
        self.domain = self.register(domain)
        self.module = 'Intelligence'
        self.source = 'AlienVaultQuery'

    def query(self):
        """
        向接口查询子域并做子域匹配
        """
        self.header = self.get_header()
        self.proxy = self.get_proxy(self.source)

        base = 'https://otx.alienvault.com/api/v1/indicators/domain'
        dns = f'{base}/{self.domain}/passive_dns'
        resp = self.get(dns)
        if not resp:
            return
        json = resp.json()
        subdomains = self.match(self.domain, str(json))
        self.subdomains = self.subdomains.union(subdomains)

        url = f'{base}/{self.domain}/url_list'
        resp = self.get(url)
        if not resp:
            return
        json = resp.json()
        subdomains = self.match(self.domain, str(json))
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
    query = AlienVault(domain)
    query.run()


if __name__ == '__main__':
    do('example.com')
