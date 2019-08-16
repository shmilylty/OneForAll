import time
import config
from common.query import Query


class BinaryEdgeAPI(Query):
    def __init__(self, domain):
        Query.__init__(self)
        self.domain = self.register(domain)
        self.module = 'Dataset'
        self.source = 'BinaryEdgeAPIQuery'
        self.addr = 'https://api.binaryedge.io/v2/query/domains/subdomain/'
        self.api = config.binaryedge_api

    def query(self):
        """
        向接口查询子域并做子域匹配
        """
        time.sleep(self.delay)
        self.header = self.get_header()
        self.header.update({'X-Key': self.api})
        self.proxy = self.get_proxy(self.source)
        url = self.addr + self.domain
        resp = self.get(url)
        if not resp:
            return
        subdomains = self.match(self.domain, str(resp.json()))
        self.subdomains = self.subdomains.union(subdomains)

    def run(self):
        """
        类执行入口
        """
        if not self.check(self.api):
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
    query = BinaryEdgeAPI(domain)
    query.run()


if __name__ == '__main__':
    do('example.com')
