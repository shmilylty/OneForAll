import time
from common.search import Search


class Yahoo(Search):
    def __init__(self, domain):
        Search.__init__(self)
        self.domain = domain
        self.module = 'Search'
        self.source = 'YahooSearch'
        self.init = 'https://search.yahoo.com/'
        self.addr = 'https://search.yahoo.com/search'
        self.limit_num = 1000  # 限制搜索条数
        self.delay = 5
        self.per_page_num = 40

    def search(self, domain, filtered_subdomain='', full_search=False):
        """
        发送搜索请求并做子域匹配

        :param str domain: 域名
        :param str filtered_subdomain: 过滤的子域
        :param bool full_search: 全量搜索
        """
        self.page_num = 0
        resp = self.get(self.init)
        if not resp:
            return
        self.cookie = resp.cookies  # 获取cookie Yahoo在搜索时需要带上cookie
        while True:
            time.sleep(self.delay)
            self.header = self.get_header()
            self.proxy = self.get_proxy(self.source)
            query = 'site:' + domain + filtered_subdomain
            params = {'q': query, 'b': self.page_num, 'n': self.per_page_num}
            resp = self.get(self.addr, params)
            if not resp:
                return
            subdomains = self.match(domain, resp.text)
            if not subdomains:  # 搜索没有发现子域名则停止搜索
                break
            if not full_search:
                # 搜索中发现搜索出的结果有完全重复的结果就停止搜索
                if subdomains.issubset(self.subdomains):
                    break
            # 合并搜索子域名搜索结果
            self.subdomains = self.subdomains.union(subdomains)
            if '>Next</a>' not in resp.text:  # 搜索页面没有出现下一页时停止搜索
                break
            self.page_num += self.per_page_num
            if self.page_num >= self.limit_num:  # 搜索条数限制
                break

    def run(self):
        """
        类执行入口
        """
        self.begin()

        self.search(self.domain, full_search=True)

        # 排除同一子域搜索结果过多的子域以发现新的子域
        for statement in self.filter(self.domain, self.subdomains):
            self.search(self.domain, filtered_subdomain=statement)

        # 递归搜索下一层的子域
        if self.recursive_search:
            # 从1开始是之前已经做过1层子域搜索了,当前实际递归层数是layer+1
            for layer_num in range(1, self.recursive_times):
                for subdomain in self.subdomains:
                    # 进行下一层子域搜索的限制条件
                    count = subdomain.count('.') - self.domain.count('.')
                    if count == layer_num:
                        self.search(subdomain)
        self.finish()
        self.save_json()
        self.gen_result()
        self.save_db()


def do(domain):  # 统一入口名字 方便多线程调用
    """
    类统一调用入口

    :param str domain: 域名
    """
    search = Yahoo(domain)
    search.run()


if __name__ == '__main__':
    do('example.com')
