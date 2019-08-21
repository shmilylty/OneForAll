import time
import config
from common.query import Query


class PassiveDnsAPI(Query):
    def __init__(self, domain):
        Query.__init__(self)
        self.domain = self.register(domain)
        self.module = 'Dataset'
        self.source = 'PassiveDnsQuery'
        self.addr = config.passivedns_api_addr or 'http://api.passivedns.cn'
        self.token = config.passivedns_api_token

    def query(self):
        """
        向接口查询子域并做子域匹配
        """
        time.sleep(self.delay)
        self.header = self.get_header()
        self.header.update({'X-AuthToken': self.token})
        self.proxy = self.get_proxy(self.source)
        url = self.addr + '/flint/rrset/*.' + self.domain
        resp = self.get(url)
        if not resp:
            return
        subdomains = self.match(self.domain, str(resp.json()))
        # 合并搜索子域名搜索结果
        self.subdomains = self.subdomains.union(subdomains)

    def run(self):
        """
        类执行入口
        """
        if not self.check(self.addr):
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
    query = PassiveDnsAPI(domain)
    query.run()


if __name__ == '__main__':
    do('example.com')
