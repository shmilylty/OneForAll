# coding=utf-8
import time
import queue
import queue
import config
# from shodan import Shodan
from common.search import Search
from config import logger


class ShodanAPI(Search):
    def __init__(self, domain):
        Search.__init__(self)
        self.domain = self.register(domain)
        self.module = 'Search'
        self.source = 'ShodanSearch'
        self.addr = 'https://api.shodan.io/shodan/host/search'
        self.key = config.shodan_api_key

    def search(self):
        """
        发送搜索请求并做子域匹配
        """
        self.header = self.get_header()
        self.proxy = self.get_proxy(self.source)
        query = 'hostname:.' + self.domain
        page = 1
        while True:
            params = {'key': self.key, 'page': page, 'query': query, 'minify': True, 'facets': {'hostnames'}}
            resp = self.get(self.addr, params)
            if not resp:
                return
            subdomain_find = self.match(self.domain, resp.text)
            if subdomain_find:
                self.subdomains = self.subdomains.union(subdomain_find)
            page += 1

    def run(self, rx_queue):
        """
        类执行入口
        """
        if not self.key:
            logger.log('ERROR', f'{self.source}模块API配置错误')
            logger.log('ALERT', f'不执行{self.source}模块')
            return
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
    search = ShodanAPI(domain)
    search.run(rx_queue)
    logger.log('INFOR', f'{search.source}模块耗时{search.elapsed}秒发现{search.domain}的子域{len(search.subdomains)}个')
    logger.log('DEBUG', f'{search.source}模块发现{search.domain}的子域 {search.subdomains}')


if __name__ == '__main__':
    results = queue.Queue()
    do('qq.com', results)
