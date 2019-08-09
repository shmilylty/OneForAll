"""
检查crossdomain.xml文件收集子域名
"""

from common.module import Module
from common import utils
from config import logger


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
        urls = [f'http://{self.domain}/crossdomain.xml',
                f'https://{self.domain}/crossdomain.xml',
                f'http://www.{self.domain}/crossdomain.xml',
                f'https://www.{self.domain}/crossdomain.xml']
        response = None
        for url in urls:
            self.header = self.get_header()
            self.proxy = self.get_proxy(self.source)
            response = self.get(url)
            if response:
                break
        if not response:
            return
        self.subdomains = utils.match_subdomain(self.domain, response.text)

    def run(self):
        """
        类执行入口
        """
        self.begin()
        logger.log('DEBUG', f'开始执行{self.source}检查{self.domain}域的跨域策略')
        self.check()
        self.save_json()
        self.gen_result()
        self.save_db()
        logger.log('DEBUG', f'结束执行{self.source}检查{self.domain}域的跨域策略')
        self.finish()


def do(domain):  # 统一入口名字 方便多线程调用
    """
    类统一调用入口

    :param domain: 域名
    """
    check = CheckCDX(domain)
    check.run()


if __name__ == '__main__':
    do('example.com')
