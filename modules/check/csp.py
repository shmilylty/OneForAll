"""
Collect subdomains from ContentSecurityPolicy
"""
import requests

from common import utils
from common.module import Module
from config.log import logger


class CheckCSP(Module):
    """
    Collect subdomains from ContentSecurityPolicy
    """
    def __init__(self, domain, header):
        Module.__init__(self)
        self.domain = self.get_maindomain(domain)
        self.module = 'Check'
        self.source = 'ContentSecurityPolicy'
        self.csp_header = header

    def grab_header(self):
        """
        Get header

        :return: ContentSecurityPolicy header
        """
        csp_header = dict()
        urls = [f'http://{self.domain}',
                f'https://{self.domain}',
                f'http://www.{self.domain}',
                f'https://www.{self.domain}']
        for url in urls:
            self.header = self.get_header()
            self.proxy = self.get_proxy(self.source)
            response = self.get(url, check=False)
            if response:
                csp_header = response.headers
                break
        return csp_header

    def check(self):
        """
        正则匹配响应头中的内容安全策略字段以发现子域名
        """
        if not self.csp_header:
            self.csp_header = self.grab_header()
        csp = self.header.get('Content-Security-Policy')
        if not self.csp_header:
            logger.log('DEBUG', f'Failed to get header of {self.domain} domain')
            return
        if not csp:
            logger.log('DEBUG', f'There is no Content-Security-Policy in the header of {self.domain}')
            return
        self.subdomains = self.match_subdomains(csp)

    def run(self):
        """
        类执行入口
        """
        self.begin()
        self.check()
        self.finish()
        self.save_json()
        self.gen_result()
        self.save_db()


def do(domain, header=None):  # 统一入口名字 方便多线程调用
    """
    类统一调用入口

    :param str domain: 域名
    :param dict or None header: 响应头
    """
    check = CheckCSP(domain, header)
    check.run()


if __name__ == '__main__':
    resp = requests.get('https://content-security-policy.com/')
    do('google-analytics.com', resp.headers)
