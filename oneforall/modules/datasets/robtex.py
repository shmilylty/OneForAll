# coding=utf-8
import time
import queue
import json
from common.query import Query
from config import logger


class Robtex(Query):
    def __init__(self, domain):
        Query.__init__(self)
        self.domain = self.register(domain)
        self.module = 'Dataset'
        self.source = "RobtexQuery"
        self.addr = 'https://freeapi.robtex.com/pdns/'

    def query(self):
        """
        向接口查询子域并做子域匹配
        """
        self.header = self.get_header()
        self.proxy = self.get_proxy(self.source)
        url = self.addr + 'forward/' + self.domain
        resp = self.get(url)
        if not resp:
            return
        text_list = resp.text.splitlines()
        text_json = list(map(lambda x: json.loads(x), text_list))
        for record in text_json:
            if record.get('rrtype') in ['A', 'AAAA']:
                time.sleep(self.delay)  # Robtex有查询频率限制
                ip = record.get('rrdata')
                url = self.addr + 'reverse/' + ip
                resp = self.get(url)
                if not resp:
                    return
                subdomains_find = self.match(self.domain, resp.text)
                if subdomains_find:
                    self.subdomains = self.subdomains.union(subdomains_find)  # 合并搜索子域名搜索结果

    def run(self, rx_queue):
        """
        类执行入口
        """
        logger.log('DEBUG', f'开始执行{self.source}模块查询{self.domain}的子域')
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
    query = Robtex(domain)
    query.run(rx_queue)
    logger.log('INFOR', f'{query.source}模块耗时{query.elapsed}秒发现{query.domain}的子域{len(query.subdomains)}个')
    logger.log('DEBUG', f'{query.source}模块发现{query.domain}的子域 {query.subdomains}')


if __name__ == '__main__':
    result_queue = queue.Queue()
    do('owasp.org', result_queue)
