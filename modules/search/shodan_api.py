from config import settings
from common.search import Search


class ShodanAPI(Search):
    def __init__(self, domain):
        Search.__init__(self)
        self.domain = domain
        self.module = 'Search'
        self.source = 'ShodanAPISearch'
        self.key = settings.shodan_api_key

    def search(self):
        """
        发送搜索请求并做子域匹配
        """
        self.header = self.get_header()
        self.proxy = self.get_proxy(self.source)
        url = f'https://api.shodan.io/dns/domain/{self.domain}?key={self.key}'
        resp = self.get(url)
        if not resp:
            return
        data = resp.json()
        names = data.get('subdomains')
        subdomain_str = str(set(map(lambda name: f'{name}.{self.domain}', names)))
        self.subdomains = self.collect_subdomains(subdomain_str)

    def run(self):
        """
        类执行入口
        """
        if not self.have_api(self.key):
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
    run('freebuf.com')
