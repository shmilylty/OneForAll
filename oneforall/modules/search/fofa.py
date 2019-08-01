# coding=utf-8
import time
import queue
import json
import base64
import config
from common.search import Search
from config import logger


class FoFa(Search):
    def __init__(self, domain):
        Search.__init__(self)
        self.domain = domain
        self.module = 'Search'
        self.source = 'FoFaSearch'
        self.addr = 'https://fofa.so/api/v1/search/all'
        self.delay = 1
        self.email = config.fofa_api_email
        self.key = config.fofa_api_key

    def search(self):
        """
        发送搜索请求并做子域匹配
        """
        self.page_num = 1
        query_base64 = base64.b64encode(f'domain={self.domain}'.encode('utf-8'))
        while True:
            time.sleep(self.delay)
            self.header = self.get_header()
            self.proxy = self.get_proxy(self.source)
            query = {'email': self.email, 'key': self.key, 'qbase64': query_base64, 'page': self.page_num}
            resp = self.get(self.addr, query)
            if not resp:
                return
            subdomain_find = self.match(self.domain, resp.text)
            self.subdomains = self.subdomains.union(subdomain_find)
            self.page_num += 1

    def run(self, rx_queue):
        """
        类执行入口
        """
        logger.log('DEBUG', f'开始执行{self.source}模块搜索{self.domain}的子域')
        start = time.time()
        self.search()
        end = time.time()
        self.elapsed = round(end - start, 1)
        self.save_json()
        self.gen_result()
        self.save_db()
        rx_queue.put(self.results)
        logger.log('DEBUG', f'结束执行{self.source}模块搜索{self.domain}的子域')


def do(domain, rx_queue):  # 统一入口名字 方便多线程调用
    """
    类统一调用入口

    :param str domain: 域名
    :param rx_queue: 结果集队列
    """
    search = FoFa(domain)
    search.run(rx_queue)
    logger.log('INFOR', f'{search.source}模块耗时{search.elapsed}秒发现{search.domain}的子域{len(search.subdomains)}个')
    logger.log('DEBUG', f'{search.source}模块发现{search.domain}的子域 {search.subdomains}')


if __name__ == '__main__':
    result_queue = queue.Queue()
    do('owasp.org', result_queue)
