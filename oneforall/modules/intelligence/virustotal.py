# coding=utf-8
import time
import queue
from common.query import Query
from config import logger


'''
最多查询100条
'''


class VirusTotal(Query):
    def __init__(self, domain):
        Query.__init__(self)
        self.source = 'VirusTotalQuery'
        self.module = 'Intelligence'
        self.addr = 'https://www.virustotal.com/ui/domains/{}/subdomains'
        self.domain = self.register(domain)

    def query(self, domain):
        """
        向接口查询子域并做子域匹配
        """
        next_cursor = ''
        while True:
            time.sleep(self.delay)
            self.header = self.get_header()
            self.header.update({'Referer': 'https://www.virustotal.com/',
                                'TE': 'Trailers'})
            self.proxy = self.get_proxy(self.source)
            params = {'limit': '40', 'cursor': next_cursor}
            resp = self.get(url=self.addr.format(domain), params=params)
            if not resp:
                return
            resp_json = resp.json()
            subdomain_find = set()
            datas = resp_json.get('data')

            if datas:
                for data in datas:
                    subdomain = data.get('id')
                    if subdomain:
                        subdomain_find.add(subdomain)
            else:
                break
            self.subdomains = self.subdomains.union(subdomain_find)
            meta = resp_json.get('meta')
            if meta:
                next_cursor = meta.get('cursor')
            else:
                break

    def run(self, rx_queue):
        """
        类执行入口
        """
        logger.log('DEBUG', f'开始执行{self.source}模块查询{self.domain}的子域')
        start = time.time()
        self.query(self.domain)
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
    query = VirusTotal(domain)
    query.run(rx_queue)
    logger.log('INFOR', f'{query.source}模块耗时{query.elapsed}秒发现{query.domain}的子域{len(query.subdomains)}个')
    logger.log('DEBUG', f'{query.source}模块发现{query.domain}的子域 {query.subdomains}')


if __name__ == '__main__':
    result_queue = queue.Queue()
    do('owasp.org', result_queue)
