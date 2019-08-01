# coding=utf-8
import time
import queue
import config
from common.query import Query
from config import logger


class IPv4InfoAPI(Query):
    def __init__(self, domain):
        Query.__init__(self)
        self.domain = self.register(domain)
        self.module = 'Dataset'
        self.source = 'IPv4InfoAPIQuery'
        self.addr = ' http://ipv4info.com/api_v1/'
        self.api = config.ipv4info_api_key

    def query(self):
        """
        向接口查询子域并做子域匹配
        """
        page = 0
        while True:
            self.header = self.get_header()
            self.proxy = self.get_proxy(self.source)
            params = {'type': 'SUBDOMAINS', 'key': self.api, 'value': self.domain, 'page': page}
            resp = self.get(self.addr, params)
            if not resp:
                return
            if resp.status_code != 200:
                break  # 请求不正常通常网络是有问题，不再继续请求下去
            resp_json = resp.json()
            subdomains_find = self.match(self.domain, str(resp_json))
            if not subdomains_find:
                break
            self.subdomains = self.subdomains.union(subdomains_find)  # 合并搜索子域名搜索结果
            subdomains = resp_json.get('Subdomains')  # 不直接使用subdomains是因为可能里面会出现不符合标准的子域名
            if len(subdomains) < 300:  # ipv4info子域查询接口每次最多返回300个 用来判断是否还有下一页
                break
            page += 1
            if page >= 50:  # ipv4info子域查询接口最多允许查询50页
                break

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
    query = IPv4InfoAPI(domain)
    query.run(rx_queue)
    logger.log('INFOR', f'{query.source}模块耗时{query.elapsed}秒发现{query.domain}的子域{len(query.subdomains)}个')
    logger.log('DEBUG', f'{query.source}模块发现{query.domain}的子域 {query.subdomains}')


if __name__ == '__main__':
    result_queue = queue.Queue()
    do('owasp.org', result_queue)
