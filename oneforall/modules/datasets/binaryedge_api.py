# coding=utf-8
import time
import queue
import config
from common.query import Query
from config import logger


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
        subdomains_find = self.match(self.domain, str(resp.json()))
        self.subdomains = self.subdomains.union(subdomains_find)

    def run(self, rx_queue):
        """
        类执行入口
        """
        if not self.api:
            logger.log('ERROR', f'{self.source}模块API配置错误')
            logger.log('ALERT', f'不执行{self.source}模块')
            return
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
    query = BinaryEdgeAPI(domain)
    query.run(rx_queue)


if __name__ == '__main__':
    result_queue = queue.Queue()
    do('example.com', result_queue)
