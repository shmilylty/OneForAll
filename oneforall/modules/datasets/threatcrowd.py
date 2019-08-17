import cloudscraper

from common.query import Query
from config import logger


class ThreatCrowd(Query):
    def __init__(self, domain):
        Query.__init__(self)
        self.domain = self.register(domain)
        self.source = 'ThreatCrowdQuery'
        self.addr = 'https://www.threatcrowd.org/searchApi' \
                    '/v2/domain/report?domain='

    def query(self):
        # 绕过cloudFlare验证
        scraper = cloudscraper.create_scraper()
        scraper.interpreter = 'js2py'
        scraper.proxies = self.get_proxy(self.source)
        url = self.addr + self.domain
        try:
            resp = scraper.get(url, timeout=self.timeout)
        except Exception as e:
            logger.log('ERROR', e.args)
            return
        if not resp:
            return
        subdomains = self.match(self.domain, str(resp.json()))
        # 合并搜索子域名搜索结果
        self.subdomains = self.subdomains.union(subdomains)

    def run(self):
        """
        类执行入口
        """
        self.begin()
        self.query()
        self.finish()
        self.save_json()
        self.gen_result()
        self.save_db()


def do(domain):  # 统一入口名字 方便多线程调用
    """
    类统一调用入口

    :param str domain: 域名
    """
    query = ThreatCrowd(domain)
    query.run()


if __name__ == '__main__':
    do('example.com')
