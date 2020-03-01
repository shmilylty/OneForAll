from common.lookup import Lookup


class QuerySOA(Lookup):
    def __init__(self, domain):
        Lookup.__init__(self)
        self.domain = self.register(domain)
        self.module = 'dnsquery'
        self.source = "QuerySOA"
        self.type = 'SOA'  # 利用的DNS记录的SOA记录收集子域

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
    brute = QuerySOA(domain)
    brute.run()


if __name__ == '__main__':
    do('cuit.edu.cn')
