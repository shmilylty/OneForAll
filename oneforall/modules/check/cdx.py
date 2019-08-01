# coding=utf-8
"""
检查crossdomain.xml文件收集子域名
"""
import time
import queue
from config import logger
from common.utils import match_subdomain
from common.module import Module


class CheckCDX(Module):
    """
    检查crossdomain.xml文件收集子域名
    """
    def __init__(self, domain: str):
        Module.__init__(self)
        self.domain = self.register(domain)
        self.module = 'Check'
        self.source = "CrossDomainXml"

    def check(self):
        """
        检查crossdomain.xml收集子域名
        :return:
        """
        url = f'http://{self.domain}/crossdomain.xml'
        self.header = self.get_header()
        self.proxy = self.get_proxy(self.source)
        resp = self.get(url)
        if not resp:
            return
        self.subdomains = match_subdomain(self.domain, resp.text)

    def run(self, rx_queue):
        """
        类执行入口
        """
        logger.log('DEBUG', f'开始执行{self.source}检查{self.domain}域的crossdomain.xml')
        start = time.time()
        self.check()
        end = time.time()
        self.elapsed = round(end - start, 1)
        self.save_json()
        self.gen_result()
        self.save_db()
        rx_queue.put(self.results)
        logger.log('DEBUG', f'结束执行{self.source}检查{self.domain}域的crossdomain.xml')


def do(domain, rx_queue):  # 统一入口名字 方便多线程调用
    """
    类统一调用入口
    :param domain: 域名
    :param rx_queue: 结果集队列
    """
    check = CheckCDX(domain)
    check.run(rx_queue)
    logger.log('INFOR', f'{check.source}模块耗时{check.elapsed}秒发现子域{len(check.subdomains)}个')
    logger.log('DEBUG', f'{check.source}模块发现的子域 {check.subdomains}')


if __name__ == '__main__':
    do('163.com')
