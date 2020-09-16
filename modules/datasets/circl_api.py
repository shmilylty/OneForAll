from config import settings
from common.query import Query


class CirclAPI(Query):
    def __init__(self, domain):
        Query.__init__(self)
        self.domain = domain
        self.module = 'Dataset'
        self.source = 'CirclAPIQuery'
        self.addr = 'https://www.circl.lu/pdns/query/'
        self.user = settings.circl_api_username
        self.pwd = settings.circl_api_password

    def query(self):
        """
        向接口查询子域并做子域匹配
        """
        self.header = self.get_header()
        self.proxy = self.get_proxy(self.source)
        resp = self.get(self.addr + self.domain, auth=(self.user, self.pwd))
        self.subdomains = self.collect_subdomains(resp)

    def run(self):
        """
        类执行入口
        """
        if not self.have_api(self.user, self.pwd):
            return
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
    query = CirclAPI(domain)
    query.run()


if __name__ == '__main__':
    run('example.com')
