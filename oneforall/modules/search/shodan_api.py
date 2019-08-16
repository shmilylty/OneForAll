import config
from common.search import Search


class ShodanAPI(Search):
    def __init__(self, domain):
        Search.__init__(self)
        self.domain = self.register(domain)
        self.module = 'Search'
        self.source = 'ShodanAPISearch'
        self.addr = 'https://api.shodan.io/shodan/host/search'
        self.key = config.shodan_api_key

    def search(self):
        """
        发送搜索请求并做子域匹配
        """
        self.header = self.get_header()
        self.proxy = self.get_proxy(self.source)
        query = 'hostname:.' + self.domain
        page = 1
        while True:
            params = {'key': self.key, 'page': page, 'query': query,
                      'minify': True, 'facets': {'hostnames'}}
            resp = self.get(self.addr, params)
            if not resp:
                return
            subdomains = self.match(self.domain, resp.text)
            if not subdomains:  # 搜索没有发现子域名则停止搜索
                break
            if subdomains:
                self.subdomains = self.subdomains.union(subdomains)
            page += 1

    def run(self):
        """
        类执行入口
        """
        if not self.check(self.key):
            return
        self.begin()
        self.search()
        self.finish()
        self.save_json()
        self.gen_result()
        self.save_db()


def do(domain):  # 统一入口名字 方便多线程调用
    """
    类统一调用入口

    :param str domain: 域名
    """
    search = ShodanAPI(domain)
    search.run()


if __name__ == '__main__':
    do('example.com')
