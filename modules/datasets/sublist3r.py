from common.query import Query


class Sublist3r(Query):
    def __init__(self, domain):
        Query.__init__(self)
        self.domain = self.get_maindomain(domain)
        self.module = 'Dataset'
        self.source = 'Sublist3rQuery'

    def query(self):
        """
        向接口查询子域并做子域匹配
        """
        self.header = self.get_header()
        self.proxy = self.get_proxy(self.source)
        addr = 'https://api.sublist3r.com/search.php'
        param = {'domain': self.domain}
        resp = self.get(addr, param)
        if not resp:
            return
        subdomains = self.match_subdomains(resp.text)
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
    query = Sublist3r(domain)
    query.run()


if __name__ == '__main__':
    do('example.com')
