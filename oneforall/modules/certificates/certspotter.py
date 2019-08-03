# coding=utf-8
import queue
import time

from common import utils
from common.query import Query


class CertSpotter(Query):
    def __init__(self, domain):
        Query.__init__(self)
        self.domain = domain
        self.module = 'Certificate'
        self.source = 'CertSpotterQuery'
        self.addr = 'https://api.certspotter.com/v1/issuances'

    def query(self):
        """
        向接口查询子域并做子域匹配
        """
        time.sleep(self.delay)
        self.header = self.get_header()
        self.proxy = self.get_proxy(self.source)
        params = {'domain': self.domain, 'include_subdomains': 'true', 'expand': 'dns_names'}
        resp = self.get(self.addr, params)
        if not resp:
            return
        subdomains_find = utils.match_subdomain(self.domain, str(resp.json()))
        self.subdomains = self.subdomains.union(subdomains_find)  # 合并搜索子域名搜索结果

    def run(self, rx_queue):
        """
        类执行入口
        """
        self.begin()
        self.query()
        self.save_json()
        self.gen_result()
        self.save_db()
        rx_queue.put(self.results)
        self.finish()


def do(domain, rx_queue):  # 统一入口名字 方便多线程调用
    """
    类统一调用入口

    :param str domain: 域名
    :param rx_queue: 结果集队列
    """
    query = CertSpotter(domain)
    query.run(rx_queue)


if __name__ == '__main__':
    result_queue = queue.Queue()
    do('example.com', result_queue)
