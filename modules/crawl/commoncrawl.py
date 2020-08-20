import cdx_toolkit
from tqdm import tqdm

from common.crawl import Crawl


class CommonCrawl(Crawl):
    def __init__(self, domain):
        Crawl.__init__(self)
        self.domain = domain
        self.module = 'Crawl'
        self.source = 'CommonCrawl'

    def crawl(self, domain, limit):
        """

        :param domain:
        :param limit:
        """
        self.header = self.get_header()
        self.proxy = self.get_proxy(self.source)
        cdx = cdx_toolkit.CDXFetcher()
        url = f'*.{domain}/*'
        size = cdx.get_size_estimate(url)
        print(url, 'CommonCrawl size estimate', size)

        for resp in tqdm(cdx.iter(url, limit=limit), total=limit):
            if resp.data.get('status') not in ['301', '302']:
                subdomains = self.match_subdomains(domain, resp.text)
                self.subdomains.update(subdomains)

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


def run(domain):
    """
    类统一调用入口

    :param str domain: 域名
    """
    crawl = CommonCrawl(domain)
    crawl.run()


if __name__ == '__main__':
    run('example.com')
