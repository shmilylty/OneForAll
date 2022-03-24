import base64
import time

from config import settings
from common.search import Search


class FoFa(Search):
    def __init__(self, domain):
        Search.__init__(self)
        self.domain = domain
        self.module = 'Search'
        self.source = 'FoFaAPISearch'
        self.addr = 'https://fofa.info/api/v1/search/all'
        self.delay = 1
        self.email = settings.fofa_api_email
        self.key = settings.fofa_api_key

    def search(self):
        """
        发送搜索请求并做子域匹配
        """
        self.page_num = 1
        subdomain_encode = f'domain="{self.domain}"'.encode('utf-8')
        query_data = base64.b64encode(subdomain_encode)
        while True:
            time.sleep(self.delay)
            self.header = self.get_header()
            self.proxy = self.get_proxy(self.source)
            query = {'email': self.email,
                     'key': self.key,
                     'qbase64': query_data,
                     'page': self.page_num,
                     'full': 'true',
                     'size': 1000}
            resp = self.get(self.addr, query)
            if not resp:
                return
            resp_json = resp.json()
            subdomains = self.match_subdomains(resp)
            if not subdomains:  # 搜索没有发现子域名则停止搜索
                break
            self.subdomains.update(subdomains)
            size = resp_json.get('size')
            if size < 1000:
                break
            self.page_num += 1

    def run(self):
        """
        类执行入口
        """
        if not self.have_api(self.email, self.key):
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
    search = FoFa(domain)
    search.run()


if __name__ == '__main__':
    run('example.com')
