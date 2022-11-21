import time

from config import settings
from common.search import Search


class Quake(Search):
    def __init__(self, domain):
        Search.__init__(self)
        self.domain = domain
        self.module = 'Quake'
        self.source = "QuakeAPISearch"
        self.addr = 'https://quake.360.net/api/v3/search/quake_service'
        self.delay = 1
        self.key = settings.quake_api_key

    def search(self):
        """
        发送搜索请求并做子域匹配
        """
        self.per_page_num = 100
        self.page_num = 0
        while True:
            time.sleep(self.delay)
            self.header = self.get_header()
            self.header.update({'Content-Type': 'application/json'})
            self.header.update({'X-QuakeToken': self.key})
            self.proxy = self.get_proxy(self.source)

            query = {'query': 'domain:"' + self.domain + '"',
                     'start': self.page_num * self.per_page_num,
                     'size': self.per_page_num,
                     'include': ["service.http.host"]}
            resp = self.post(self.addr, json=query)
            if not resp:
                return
            resp_json = resp.json()
            subdomains = self.match_subdomains(resp)
            if not subdomains:  # 搜索没有发现子域名则停止搜索
                break
            self.subdomains.update(subdomains)
            total = resp_json.get('meta').get('pagination').get('total')
            self.page_num += 1
            if self.page_num * self.per_page_num >= int(total):
                break

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
    query = Quake(domain)
    query.run()


if __name__ == '__main__':
    run('nosugartech.com')
