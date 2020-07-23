from common.lookup import Lookup


class QuerySPF(Lookup):
    def __init__(self, domain):
        Lookup.__init__(self)
        self.domain = self.get_maindomain(domain)
        self.module = 'dnsquery'
        self.source = "QuerySPF"
        self.type = 'SPF'  # 利用的DNS记录的SPF记录收集子域

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
    brute = QuerySPF(domain)
    brute.run()


if __name__ == '__main__':
    do('qq.com')