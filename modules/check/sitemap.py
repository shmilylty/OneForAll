"""
检查内容安全策略收集子域名收集子域名
"""
from common.module import Module


class CheckRobots(Module):
    """
    检查sitemap收集子域名
    """
    def __init__(self, domain):
        Module.__init__(self)
        self.domain = domain
        self.module = 'Check'
        self.source = 'Sitemap'

    def check(self):
        """
        正则匹配域名的sitemap文件中的子域
        """
        urls = [f'http://{self.domain}/sitemap.xml',
                f'http://www.{self.domain}/sitemap.xml',
                f'http://{self.domain}/sitemap.txt',
                f'http://www.{self.domain}/sitemap.txt',
                f'http://{self.domain}/sitemap.html',
                f'http://www.{self.domain}/sitemap.html',
                f'http://{self.domain}/sitemap_index.xml',
                f'http://www.{self.domain}/sitemap_index.xml']
        for url in urls:
            self.header = self.get_header()
            self.proxy = self.get_proxy(self.source)
            self.timeout = 10
            resp = self.get(url, check=False)
            self.subdomains = self.collect_subdomains(resp)

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

    :param str domain: 域名
    """
    check = CheckRobots(domain)
    check.run()


if __name__ == '__main__':
    run('qq.com')
