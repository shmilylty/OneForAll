# coding=utf-8
import queue
import random
import time

from bs4 import BeautifulSoup

from common.query import Query


class DNSdb(Query):
    def __init__(self, domain):
        Query.__init__(self)
        self.domain = self.register(domain)
        self.module = 'Dataset'
        self.source = 'DNSdbQuery'
        self.addr = 'https://www.dnsdb.org/'

    def query(self):
        """
        向接口查询子域并做子域匹配
        """
        self.header = self.get_header()
        self.header.update({'Referer': self.addr})
        self.proxy = self.get_proxy(self.source)
        url = self.addr + self.domain + '/'
        resp = self.get(url)
        if not resp:
            return
        if resp.status_code == 200:
            if 'index' in resp.text:
                soup = BeautifulSoup(resp.text, features='lxml')
                index_urls = set(map(lambda x: self.addr + self.domain + x.text, soup.find_all('a')))
                for url in index_urls:
                    self.delay = random.randint(2, 5)  # 休眠绕过CloudFlare的DDoS保护
                    time.sleep(self.delay)
                    resp = self.get(url)
                    if not resp:
                        return
                    subdomains_find = self.match(self.domain, resp.text)
                    self.subdomains = self.subdomains.union(subdomains_find)  # 合并搜索子域名搜索结果
            else:
                subdomains_find = self.match(self.domain, resp.text)
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
    query = DNSdb(domain)
    query.run(rx_queue)


if __name__ == '__main__':
    result_queue = queue.Queue()
    do('example.com', result_queue)
