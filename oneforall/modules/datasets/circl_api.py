import time
import config
from common.query import Query


class CirclAPI(Query):
    def __init__(self, domain):
        Query.__init__(self)
        self.domain = self.register(domain)
        self.module = 'Dataset'
        self.source = 'CirclAPIQuery'
        self.addr = 'https://www.circl.lu/pdns/query/'
        self.user = config.circl_api_username
        self.pwd = config.circl_api_password

    def query(self):
        """
        向接口查询子域并做子域匹配
        """
        time.sleep(self.delay)
        self.header = self.get_header()
        self.proxy = self.get_proxy(self.source)
        resp = self.get(self.addr + self.domain, auth=(self.user, self.pwd))
        if not resp:
            return
        subdomains = self.match(self.domain, str(resp.json()))
        # 合并搜索子域名搜索结果
        self.subdomains = self.subdomains.union(subdomains)

    def run(self):
        """
        类执行入口
        """
        if not self.check(self.user, self.pwd):
            return
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
    query = CirclAPI(domain)
    query.run()


if __name__ == '__main__':
    do('example.com')
