# coding=utf-8
import time
import queue
import config
from common.query import Query
from config import logger


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
        subdomains_find = self.match(self.domain, str(resp.json()))
        self.subdomains = self.subdomains.union(subdomains_find)  # 合并搜索子域名搜索结果

    def run(self, rx_queue):
        """
        类执行入口
        """
        logger.log('DEBUG', f'开始执行{self.source}模块查询{self.domain}的子域')
        if self.user and self.pwd:
            start = time.time()
            self.query()
            end = time.time()
            self.elapsed = round(end - start, 1)
            self.save_json()
            self.gen_result()
            self.save_db()
            rx_queue.put(self.results)
        logger.log('DEBUG', f'结束执行{self.source}模块查询{self.domain}的子域')


def do(domain, rx_queue):  # 统一入口名字 方便多线程调用
    """
    类统一调用入口

    :param str domain: 域名
    :param rx_queue: 结果集队列
    """
    query = CirclAPI(domain)
    query.run(rx_queue)
    logger.log('INFOR', f'{query.source}模块耗时{query.elapsed}秒发现{query.domain}的子域{len(query.subdomains)}个')
    logger.log('DEBUG', f'{query.source}模块发现{query.domain}的子域 {query.subdomains}')


if __name__ == '__main__':
    result_queue = queue.Queue()
    do('owasp.org', result_queue)
