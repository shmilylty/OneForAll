from config import settings
from common.query import Query


class FullHuntAPI(Query):
    def __init__(self, domain):
        Query.__init__(self)
        self.domain = domain
        self.module = 'Dataset'
        self.source = 'FullHuntAPIQuery'
        self.api = settings.fullhunt_api_key

    def query(self):
        """
        向接口查询子域并做子域匹配
        """
        self.header = self.get_header()
        self.header.update({'X-API-KEY': self.api})
        self.proxy = self.get_proxy(self.source)
        url = f'https://fullhunt.io/api/v1/domain/{self.domain}/subdomains'
        resp = self.get(url)
        self.subdomains = self.collect_subdomains(resp)

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


def run(domain):
    """
    类统一调用入口

    :param str domain: 域名

    """
    query = FullHuntAPI(domain)
    query.run()


if __name__ == '__main__':
    run('qq.com')
