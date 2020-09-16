import time
from config import settings
from common.search import Search


class GoogleAPI(Search):
    def __init__(self, domain):
        Search.__init__(self)
        self.domain = domain
        self.module = 'Search'
        self.source = 'GoogleAPISearch'
        self.addr = 'https://www.googleapis.com/customsearch/v1'
        self.delay = 1
        self.key = settings.google_api_key
        self.id = settings.google_api_id
        self.per_page_num = 10  # 每次只能请求10个结果

    def search(self, domain, filtered_subdomain=''):
        """
        发送搜索请求并做子域匹配

        :param str domain: 域名
        :param str filtered_subdomain: 过滤的子域
        """
        self.page_num = 1
        while True:
            word = 'site:.' + domain + filtered_subdomain
            time.sleep(self.delay)
            self.header = self.get_header()
            self.proxy = self.get_proxy(self.source)
            params = {'key': self.key, 'cx': self.id,
                      'q': word, 'fields': 'items/link',
                      'start': self.page_num, 'num': self.per_page_num}
            resp = self.get(self.addr, params)
            subdomains = self.match_subdomains(resp)
            if not self.check_subdomains(subdomains):
                break
            self.subdomains.update(subdomains)
            self.page_num += self.per_page_num
            if self.page_num > 100:  # 免费的API只能查询前100条结果
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
    search = GoogleAPI(domain)
    search.run()


if __name__ == '__main__':
    run('mi.com')
