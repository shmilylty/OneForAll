"""
Collect subdomains from ContentSecurityPolicy
"""
import requests

from config.log import logger
from common.check import Check


class CSP(Check):
    """
    Collect subdomains from ContentSecurityPolicy
    """

    def __init__(self, domain, header):
        Check.__init__(self)
        self.domain = domain
        self.module = 'check'
        self.source = 'CSPCheck'
        self.csp_header = header

    @property
    def grab_header(self):
        """
        Get header

        :return: ContentSecurityPolicy header
        """
        csp_header = dict()
        urls = [f'http://{self.domain}',
                f'https://{self.domain}']
        urls_www = [f'http://www.{self.domain}',
                    f'https://www.{self.domain}']
        header = self.grab_loop(csp_header, urls)
        if header:
            return header
        header = self.grab_loop(csp_header, urls_www)
        return header

    def grab_loop(self, csp_header, urls):
        for url in urls:
            self.header = self.get_header()
            self.proxy = self.get_proxy(self.source)
            try:
                response = self.get(url, check=False, ignore=True, raise_error=True)
            except requests.exceptions.ConnectTimeout:
                logger.log('DEBUG', f'Connection to {url} timed out, so break check')
                break
            if response:
                return response.headers
        return csp_header

    def check(self):
        """
        正则匹配响应头中的内容安全策略字段以发现子域名
        """
        if not self.csp_header:
            self.csp_header = self.grab_header
        csp = self.csp_header.get('Content-Security-Policy')
        if not self.csp_header:
            logger.log('DEBUG', f'Failed to get header of {self.domain} domain')
            return
        if not csp:
            logger.log('DEBUG', f'There is no Content-Security-Policy in the header '
                                f'of {self.domain}')
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


def run(domain, header=None):
    """
    类统一调用入口

    :param str domain: 域名
    :param dict or None header: 响应头
    """
    check = CSP(domain, header)
    check.run()


if __name__ == '__main__':
    resp = requests.get('https://content-security-policy.com/')
    run('google-analytics.com', dict(resp.headers))
