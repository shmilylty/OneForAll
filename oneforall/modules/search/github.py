import time

from common.query import Query


class Github(Query):
    def __init__(self, domain):
        Query.__init__(self)
        self.source = 'GithubSearch'
        self.module = 'Search'
        self.addr = 'https://github.com/search'
        self.domain = self.register(domain)

    def query(self):
        """
        向接口查询子域并做子域匹配
        """
        page_num = 1
        while True:
            time.sleep(self.delay)
            self.header = self.get_header()
            self.proxy = self.get_proxy(self.source)
            params = {'p': page_num, 'q': f'"{self.domain}"', 'type': 'Code'}
            resp = self.get(url=self.addr, params=params)
            if not resp:
                return
            subdomains = self.match(self.domain, resp.text)
            self.subdomains = self.subdomains.union(subdomains)
            if 'class="next_page disabled"' in resp.text:
                break
            page_num += 1

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
    query = Github(domain)
    query.run()


if __name__ == '__main__':
    do('example.com')
