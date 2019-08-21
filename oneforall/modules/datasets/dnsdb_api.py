import time
import config
from common import utils
from common.query import Query


class DNSdbAPI(Query):
    def __init__(self, domain):
        Query.__init__(self)
        self.domain = self.register(domain)
        self.module = 'Dataset'
        self.source = 'DNSdbAPIQuery'
        self.addr = 'https://api.dnsdb.info/lookup/rrset/name/'
        self.api = config.dnsdb_api_key

    def query(self):
        """
        向接口查询子域并做子域匹配
        """
        time.sleep(self.delay)
        self.header = self.get_header()
        self.header.update({'X-API-Key': self.api})
        self.proxy = self.get_proxy(self.source)
        url = f'{self.addr}*.{self.domain}'
        resp = self.get(url)
        if not resp:
            return
        subdomains = utils.match_subdomain(self.domain, resp.text)
        # 合并搜索子域名搜索结果
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
    query = DNSdbAPI(domain)
    query.run()


if __name__ == '__main__':
    do('example.com')
