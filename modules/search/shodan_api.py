from config import settings
from common.search import Search


class ShodanAPI(Search):
    def __init__(self, domain):
        Search.__init__(self)
        self.domain = domain
        self.module = 'Search'
        self.source = 'ShodanAPISearch'
        self.addr = 'https://api.shodan.io/shodan/host/search'
        self.key = settings.shodan_api_key

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
            subdomains = self.match_subdomains(resp)
            if not subdomains:  # 搜索没有发现子域名则停止搜索
                break
            self.subdomains.update(subdomains)
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


def run(domain):
    """
    类统一调用入口

    :param str domain: 域名
    """
    search = ShodanAPI(domain)
    search.run()


if __name__ == '__main__':
    run('example.com')
