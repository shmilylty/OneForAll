"""
检查crossdomain.xml文件收集子域名
"""

from common.module import Module


class CheckCDX(Module):
    """
    检查crossdomain.xml文件收集子域名
    """
    def __init__(self, domain: str):
        Module.__init__(self)
        self.domain = domain
        self.module = 'Check'
        self.source = "CrossDomainXml"

    def check(self):
        """
        检查crossdomain.xml收集子域名
        """
        urls = [f'http://{self.domain}/crossdomain.xml',
                f'https://{self.domain}/crossdomain.xml',
                f'http://www.{self.domain}/crossdomain.xml',
                f'https://www.{self.domain}/crossdomain.xml']
        for url in urls:
            self.header = self.get_header()
            self.proxy = self.get_proxy(self.source)
            resp = self.get(url, check=False)
            if not resp:
                return
            if resp and len(resp.content):
                self.subdomains = self.match_subdomains(resp.text)

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


def run(domain):
    """
    类统一调用入口

    :param domain: 域名
    """
    check = CheckCDX(domain)
    check.run()


if __name__ == '__main__':
    run('example.com')
