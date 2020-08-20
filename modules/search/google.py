import random
import time
from common.search import Search


class Google(Search):
    def __init__(self, domain):
        Search.__init__(self)
        self.domain = domain
        self.module = 'Search'
        self.source = 'GoogleSearch'
        self.init = 'https://www.google.com/'
        self.addr = 'https://www.google.com/search'

    def search(self, domain, filtered_subdomain=''):
        """
        发送搜索请求并做子域匹配

        :param str domain: 域名
        :param str filtered_subdomain: 过滤的子域
        """
        page_num = 1
        per_page_num = 50
        self.header = self.get_header()
        self.header.update({'User-Agent': 'Googlebot',
                            'Referer': 'https://www.google.com'})
        self.proxy = self.get_proxy(self.source)
        resp = self.get(self.init)
        if not resp:
            return
        self.cookie = resp.cookies
        while True:
            self.delay = random.randint(1, 5)
            time.sleep(self.delay)
            self.proxy = self.get_proxy(self.source)
            word = 'site:.' + domain + filtered_subdomain
            payload = {'q': word, 'start': page_num, 'num': per_page_num,
                       'filter': '0', 'btnG': 'Search', 'gbv': '1', 'hl': 'en'}
            resp = self.get(url=self.addr, params=payload)
            subdomains = self.match_subdomains(resp, fuzzy=False)
            if not self.check_subdomains(subdomains):
                break
            self.subdomains.update(subdomains)
            page_num += per_page_num
            if 'start=' + str(page_num) not in resp.text:
                break
            if '302 Moved' in resp.text:
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
    search = Google(domain)
    search.run()


if __name__ == '__main__':
    run('example.com')
