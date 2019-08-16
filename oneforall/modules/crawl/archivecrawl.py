import cdx_toolkit
from common.crawl import Crawl
from config import logger


class ArchiveCrawl(Crawl):
    def __init__(self, domain):
        Crawl.__init__(self)
        self.domain = domain
        self.module = 'Crawl'
        self.source = 'ArchiveCrawl'

    def crawl(self, domain, limit):
        """

        :param domain:
        :param limit:
        """
        self.header = self.get_header()
        self.proxy = self.get_proxy(self.source)
        cdx = cdx_toolkit.CDXFetcher(source='ia')
        url = f'*.{domain}/*'
        size = cdx.get_size_estimate(url)
        logger.log('DEBUG', f'{url} ArchiveCrawl size estimate {size}')

        for resp in cdx.iter(url, limit=limit):
            if resp.data.get('status') not in ['301', '302']:
                url = resp.data.get('url')
                subdomains = self.match(self.register(domain),
                                             url + resp.text)
                # 合并搜索子域名搜索结果
                self.subdomains = self.subdomains.union(subdomains)

    def run(self):
        """
        类执行入口
        """
        self.begin()
        self.crawl(self.domain, 50)
        # 爬取已发现的子域以发现新的子域
        for subdomain in self.subdomains:
            if subdomain != self.domain:
                self.crawl(subdomain, 10)
        self.finish()
        self.save_json()
        self.gen_result()
        self.save_db()


def do(domain):  # 统一入口名字 方便多线程调用
    """
    类统一调用入口

    :param str domain: 域名
    """
    crawl = ArchiveCrawl(domain)
    crawl.run()


if __name__ == '__main__':
    do('example.com')
