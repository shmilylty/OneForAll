import time
from common.search import Search


class Bing(Search):
    def __init__(self, domain):
        Search.__init__(self)
        self.domain = domain
        self.module = 'Search'
        self.source = 'BingSearch'
        self.init = 'https://www.bing.com/'
        self.addr = 'https://www.bing.com/search'
        self.limit_num = 1000  # 限制搜索条数

    def search(self, domain, filtered_subdomain=''):
        """
        发送搜索请求并做子域匹配

        :param str domain: 域名
        :param str filtered_subdomain: 过滤的子域
        """
        self.header = self.get_header()
        self.proxy = self.get_proxy(self.source)
        self.page_num = 0  # 二次搜索重新置0
        resp = self.get(self.init)
        if not resp:
            return
        self.cookie = resp.cookies  # 获取cookie bing在搜索时需要带上cookie
        while True:
            time.sleep(self.delay)
            self.proxy = self.get_proxy(self.source)
            query = 'site:.' + domain + filtered_subdomain
            params = {'q': query, 'first': self.page_num,
                      'count': self.per_page_num}
            resp = self.get(self.addr, params)
            subdomains = self.match_subdomains(resp, fuzzy=False)
            if not self.check_subdomains(subdomains):
                break
            self.subdomains.update(subdomains)
            # 搜索页面没有出现下一页时停止搜索
            if '<div class="sw_next">' not in resp.text:
                break
            self.page_num += self.per_page_num
            if self.page_num >= self.limit_num:  # 搜索条数限制
                break

    def run(self):
        """
        类执行入口
        """
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
    search = Bing(domain)
    search.run()


if __name__ == '__main__':
    run('example.com')
