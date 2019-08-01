# coding=utf-8
import time
import queue
import cdx_toolkit
from common.crawl import Crawl
from config import logger


class ArchiveCrawl(Crawl):
    def __init__(self, domain):
        Crawl.__init__(self)
        self.domain = domain
        self.module = 'Crawl'
        self.source = 'ArchiveCrawl'

    def crawl(self, domain, limit):
        """

        :param domain:
        :param limit:
        """
        self.header = self.get_header()
        self.proxy = self.get_proxy(self.source)
        cdx = cdx_toolkit.CDXFetcher(source='ia')
        url = f'*.{domain}/*'
        size = cdx.get_size_estimate(url)
        logger.log('DEBUG', f'{url} ArchiveCrawl size estimate {size}')

        for resp in cdx.iter(url, limit=limit):
            if resp.data.get('status') not in ['301', '302']:
                url = resp.data.get('url')
                subdomains_find = self.match(self.register(domain), url + resp.text)
                self.subdomains = self.subdomains.union(subdomains_find)  # 合并搜索子域名搜索结果

    def run(self, rx_queue):
        """
        类执行入口
        """
        logger.log('DEBUG', f'开始执行{self.source}模块查询{self.domain}的子域')
        start = time.time()
        self.crawl(self.domain, 50)

        # 爬取已发现的子域以发现新的子域
        for subdomain in self.subdomains:
            if subdomain != self.domain:
                self.crawl(subdomain, 10)
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
    crawl = ArchiveCrawl(domain)
    crawl.run(result)
    logger.log('INFOR', f'{crawl.source}模块耗时{crawl.elapsed}秒发现{crawl.domain}的子域{len(crawl.subdomains)}个')
    logger.log('DEBUG', f'{crawl.source}模块发现{crawl.domain}的子域 {crawl.subdomains}')


if __name__ == '__main__':
    result_queue = queue.Queue()
    do('owasp.org', result_queue)
