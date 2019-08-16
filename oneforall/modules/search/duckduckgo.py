import re
import time
from common.search import Search
from config import logger


class DuckDuckGO(Search):
    def __init__(self, domain):
        Search.__init__(self)
        self.domain = domain
        self.module = 'Search'
        self.source = 'DuckDuckGoSearch'
        self.addr = 'https://duckduckgo.com/html/'
        self.header = self.get_header()
        self.delay = 2

    def search(self, domain, filtered_subdomain='', full_search=False):
        """
        发送搜索请求并做子域匹配

        :param str domain: 域名
        :param str filtered_subdomain: 过滤的子域
        :param bool full_search: 全量搜索
        """
        query = 'site:' + domain + filtered_subdomain
        data = {'q': query, 'kl': 'us-en', 'v': 'l'}
        while True:
            time.sleep(self.delay)
            self.proxy = self.get_proxy(self.source)
            resp = self.post(self.addr, data)
            if not resp:
                return
            subdomains = self.match(domain, resp.text)
            if not subdomains:
                break
            if not full_search:
                # 搜索中发现搜索出的结果有完全重复的结果就停止搜索
                if subdomains.issubset(self.subdomains):
                    break
            self.subdomains = self.subdomains.union(subdomains)
            try:
                s = re.findall(r'name="s" value="(\d.*)"', resp.text)[-1]
                dc = re.findall(r'name="dc" value="(\d.*)"', resp.text)
            except Exception as e:
                logger.error(e)
                break
            data.update({'s': s, 'nextParams': '', 'o': 'json',
                         'dc': dc, 'api': '/d.js'})

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
    # return  # 暂时还有点问题
    search = DuckDuckGO(domain)
    search.run()


if __name__ == '__main__':

    do('example.com')
