from common.lookup import Lookup


class QueryTXT(Lookup):
    def __init__(self, domain):
        Lookup.__init__(self)
        self.domain = domain
        self.module = 'dnsquery'
        self.source = "QueryTXT"
        self.qtype = 'TXT'  # 利用的DNS记录的TXT记录收集子域

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
    query = QueryTXT(domain)
    query.run()


if __name__ == '__main__':
    run('cuit.edu.cn')
