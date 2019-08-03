# coding=utf-8
"""
检查内容安全策略收集子域名收集子域名
"""
import queue
import requests
from common import utils
from common.module import Module
from config import logger


class CheckCSP(Module):
    """
    检查内容安全策略收集子域名
    """

    def __init__(self, domain, header):
        Module.__init__(self)
        self.domain = self.register(domain)
        self.module = 'Check'
        self.source = 'Content-Security-Policy'
        self.header = header

    def check(self):
        """
        正则匹配响应头中的内容安全策略字段以发现子域名
        """
        if not self.header:
            url = f'http://www.{self.domain}'
            resp = self.get(url)
            if not resp:
                return
            self.header = resp.headers
        csp = self.header.get('Content-Security-Policy')
        if not csp:
            logger.log('DEBUG', f'{self.domain}域的响应头不存在内容安全策略字段')
            return
        logger.log('DEBUG', f'{self.domain}域的响应头存在内容安全策略字段')
        self.subdomains = utils.match_subdomain(self.domain, csp)

    def run(self, rx_queue):
        """
        类执行入口
        """
        logger.log('DEBUG', f'开始执行{self.source}检查{self.domain}域响应头中的内容安全策略字段')
        self.check()
        self.save_json()
        self.gen_result()
        self.save_db()
        rx_queue.put(self.results)
        logger.log('DEBUG', f'结束执行{self.source}检查{self.domain}域响应头中的内容安全策略字段')
        self.finish()


def do(domain, rx_queue, header=None):  # 统一入口名字 方便多线程调用
    """
    类统一调用入口

    :param str domain: 域名
    :param rx_queue: 结果集队列
    :param dict or None header: 响应头
    """
    check = CheckCSP(domain, header)
    check.run(rx_queue)


if __name__ == '__main__':
    # resp = requests.get('https://content-security-policy.com/')
    result_queue = queue.Queue()
    resp = requests.get('https://www.baidu.com/')
    do('google-analytics.com', result_queue, resp.headers)
