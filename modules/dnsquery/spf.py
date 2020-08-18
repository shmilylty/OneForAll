from common.lookup import Lookup


class QuerySPF(Lookup):
    def __init__(self, domain):
        Lookup.__init__(self)
        self.domain = domain
        self.module = 'dnsquery'
        self.source = "QuerySPF"
        self.qtype = 'SPF'  # 利用的DNS记录的SPF记录收集子域

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
    brute = QuerySPF(domain)
    brute.run()


if __name__ == '__main__':
    run('qq.com')
