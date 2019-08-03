# coding=utf-8
import queue

import cdx_toolkit
from tqdm import tqdm

from common.crawl import Crawl
from config import logger


class CommonCrawl(Crawl):
    def __init__(self, domain):
        Crawl.__init__(self)
        self.domain = domain
        self.module = 'Crawl'
        self.source = 'CommonCrawl'

    def crawl(self, domain, limit):
        """

        :param domain:
        :param limit:
        """
        self.header = self.get_header()
        self.proxy = self.get_proxy(self.source)
        cdx = cdx_toolkit.CDXFetcher()
        url = f'*.{domain}/*'
        size = cdx.get_size_estimate(url)
        print(url, 'CommonCrawl size estimate', size)

        for resp in tqdm(cdx.iter(url, limit=limit), total=limit):
            if resp.data.get('status') not in ['301', '302']:
                subdomains_find = self.match(self.register(domain), resp.text)
                self.subdomains = self.subdomains.union(subdomains_find)  # 合并搜索子域名搜索结果

    def run(self, rx_queue):
        """
        类执行入口
        """
        self.begin()
        self.crawl(self.domain, 50)
        # 爬取已发现的子域以发现新的子域
        for subdomain in self.subdomains:
            if subdomain != self.domain:
                self.crawl(subdomain, 10)
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
    crawl = CommonCrawl(domain)
    crawl.run(rx_queue)
    logger.log('INFOR', f'{crawl.source}模块耗时{crawl.elapsed}秒发现{crawl.domain}的子域{len(crawl.subdomains)}个')
    logger.log('DEBUG', f'{crawl.source}模块发现{crawl.domain}的子域 {crawl.subdomains}')


if __name__ == '__main__':
    result_queue = queue.Queue()
    do('example.com', result_queue)
