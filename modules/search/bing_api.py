import time
from config import settings
from common.search import Search


class BingAPI(Search):
    def __init__(self, domain):
        Search.__init__(self)
        self.domain = domain
        self.module = 'Search'
        self.source = 'BingAPISearch'
        self.addr = 'https://api.cognitive.microsoft.com/bing/v7.0/search'
        self.id = settings.bing_api_id
        self.key = settings.bing_api_key
        self.limit_num = 1000  # 必应同一个搜索关键词限制搜索条数
        self.delay = 1  # 必应自定义搜索限制时延1秒

    def search(self, domain, filtered_subdomain=''):
        """
        发送搜索请求并做子域匹配

        :param str domain: 域名
        :param str filtered_subdomain: 过滤的子域
        """
        self.page_num = 0  # 二次搜索重新置0
        while True:
            time.sleep(self.delay)
            self.header = self.get_header()
            self.header = {'Ocp-Apim-Subscription-Key': self.key}
            self.proxy = self.get_proxy(self.source)
            query = 'site:.' + domain + filtered_subdomain
            params = {'q': query, 'safesearch': 'Off',
                      'count': self.per_page_num,
                      'offset': self.page_num}
            resp = self.get(self.addr, params)
            subdomains = self.match_subdomains(resp)
            if not self.check_subdomains(subdomains):
                break
            self.subdomains.update(subdomains)
            self.page_num += self.per_page_num
            if self.page_num >= self.limit_num:  # 搜索条数限制
                break

    def run(self):
        """
        类执行入口
        """
        if not self.have_api(self.id, self.key):
            return
        self.begin()
        self.search(self.domain)

        # 排除同一子域搜索结果过多的子域以发现新的子域
        for statement in self.filter(self.domain, self.subdomains):
            self.search(self.domain, filtered_subdomain=statement)

        # 递归搜索下一层的子域
        if self.recursive_search:
            for subdomain in self.recursive_subdomain():
                self.search(subdomain)
        self.finish()
        self.save_json()
        self.gen_result()
        self.save_db()


def run(domain):
    """
    类统一调用入口

    :param str domain: 域名
    """
    search = BingAPI(domain)
    search.run()


if __name__ == '__main__':
    run('example.com')
