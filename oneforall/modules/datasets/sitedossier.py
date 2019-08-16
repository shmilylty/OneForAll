import time

from common.query import Query


class SiteDossier(Query):
    def __init__(self, domain):
        Query.__init__(self)
        self.domain = self.register(domain)
        self.module = 'Dataset'
        self.source = 'SiteDossierQuery'
        self.addr = 'http://www.sitedossier.com/parentdomain/'
        self.delay = 2
        self.page_num = 1
        self.per_page_num = 100

    def query(self):
        """
        向接口查询子域并做子域匹配
        """
        while True:
            time.sleep(self.delay)
            self.header = self.get_header()
            self.proxy = self.get_proxy(self.source)
            url = f'{self.addr}{self.domain}/{self.page_num}'
            resp = self.get(url)
            if not resp:
                return
            subdomains = self.match(self.domain, resp.text)
            if not subdomains:  # 搜索没有发现子域名则停止搜索
                break
            # 合并搜索子域名搜索结果
            self.subdomains = self.subdomains.union(subdomains)
            # 搜索页面没有出现下一页时停止搜索
            if 'Show next 100 items' not in resp.text:
                break
            self.page_num += self.per_page_num

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
    query = SiteDossier(domain)
    query.run()


if __name__ == '__main__':
    do('example.com')
