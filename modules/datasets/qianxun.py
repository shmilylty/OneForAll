from common.query import Query


class QianXun(Query):
    def __init__(self, domain):
        Query.__init__(self)
        self.domain = domain
        self.module = 'Query'
        self.source = 'QianXunQuery'

    def query(self):
        """
        向接口查询子域并做子域匹配
        """
        self.header = self.get_header()
        self.proxy = self.get_proxy(self.source)

        num = 1
        while True:
            data = {'ecmsfrom': '',
                    'show': '',
                    'num': '',
                    'classid': '0',
                    'keywords': self.domain}
            url = f'https://www.dnsscan.cn/dns.html?' \
                  f'keywords={self.domain}&page={num}'
            resp = self.post(url, data)
            if not resp:
                break
            subdomains = self.match(self.domain, resp.text)
            self.subdomains = self.subdomains.union(subdomains)
            if '<div id="page" class="pagelist">' not in resp.text:
                break
            if '<li class="disabled"><span>&raquo;</span></li>' in resp.text:
                break
            num += 1

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
    query = QianXun(domain)
    query.run()


if __name__ == '__main__':
    do('example.com')
