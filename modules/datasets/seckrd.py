from common.query import Query


class Seckrd(Query):
    def __init__(self, domain):
        Query.__init__(self)
        self.domain = domain
        self.module = 'Query'
        self.source = 'Seckrd'

    def query(self):
        """
        向接口查询子域并做子域匹配
        """
        self.header = self.get_header()
        self.proxy = self.get_proxy(self.source)

        data = {'domain': self.domain,
                'submit': ''}
        url = f'https://seckrd.com/subdomain-finder.php'
        resp = self.post(url, data)
        subdomains = self.match_subdomains(resp)
        self.subdomains.update(subdomains)

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
    query = Seckrd(domain)
    query.run()


if __name__ == '__main__':
    run('jd.com')
