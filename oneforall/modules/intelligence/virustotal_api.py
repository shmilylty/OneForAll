# coding=utf-8
import queue

import config
from common.query import Query
from config import logger


class VirusTotalAPI(Query):
    def __init__(self, domain):
        Query.__init__(self)
        self.domain = self.register(domain)
        self.module = 'Intelligence'
        self.source = 'VirusTotalAPIQuery'
        self.addr = 'https://www.virustotal.com/vtapi/v2/domain/report'
        self.key = config.virustotal_api_key

    def query(self, domain):
        """
        向接口查询子域并做子域匹配
        """
        self.header = self.get_header()
        self.proxy = self.get_proxy(self.source)
        params = {'apikey': self.key, 'domain': domain}
        resp = self.get(self.addr, params)
        if not resp:
            return
        resp_json = resp.json()
        subdomain_find = set(resp_json.get('subdomains'))
        self.subdomains = self.subdomains.union(subdomain_find)

    def run(self, rx_queue):
        """
        类执行入口
        """
        if not self.key:
            logger.log('ERROR', f'{self.source}模块API配置错误')
            logger.log('ALERT', f'不执行{self.source}模块')
            return
        self.begin()
        self.query(self.domain)
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
    query = VirusTotalAPI(domain)
    query.run(rx_queue)


if __name__ == '__main__':
    result_queue = queue.Queue()
    do('example.com', result_queue)
