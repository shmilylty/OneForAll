# coding=utf-8
import time
import queue
from common.search import Search
from config import logger


class So(Search):
    def __init__(self, domain):
        Search.__init__(self)
        self.domain = domain
        self.module = 'Search'
        self.source = 'SoSearch'
        self.addr = 'http://www.so.com/s'
        self.limit_num = 640  # 限制搜索条数
        self.per_page_num = 10  # 默认每页显示10页

    def search(self, domain, filtered_subdomain='', full_search=False):
        """
        发送搜索请求并做子域匹配

        :param str domain: 域名
        :param str filtered_subdomain: 过滤的子域
        :param bool full_search: 全量搜索
        """
        page_num = 1
        while True:
            time.sleep(self.delay)
            self.header = self.get_header()
            self.proxy = self.get_proxy(self.source)
            word = 'site:' + domain + filtered_subdomain
            payload = {'q': word, 'pn': page_num}
            resp = self.get(url=self.addr, params=payload)
            if not resp:
                return
            subdomain_find = self.match(domain, resp.text)
            if not subdomain_find:
                break
            if not full_search:
                if subdomain_find.issubset(self.subdomains):  # 搜索中发现搜索出的结果有完全重复的结果就停止搜索
                    break
            self.subdomains = self.subdomains.union(subdomain_find)
            page_num += 1
            if '<a id="snext"' not in resp.text:  # 搜索页面没有出现下一页时停止搜索
                break
            if self.page_num * self.per_page_num >= self.limit_num:  # 搜索条数限制
                break

    def run(self, rx_queue):
        """
        类执行入口
        """
        logger.log('DEBUG', f'开始执行{self.source}模块搜索{self.domain}的子域')
        start = time.time()
        self.search(self.domain, full_search=True)

        # 排除同一子域搜索结果过多的子域以发现新的子域
        for statement in self.filter(self.domain, self.subdomains):
            self.search(self.domain, filtered_subdomain=statement)

        # 递归搜索下一层的子域
        if self.recursive_search:
            for layer_num in range(1, self.recursive_times):  # 从1开始是之前已经做过1层子域搜索了,当前实际递归层数是layer+1
                for subdomain in self.subdomains:
                    if subdomain.count('.') - self.domain.count('.') == layer_num:  # 进行下一层子域搜索的限制条件
                        self.search(subdomain)
        end = time.time()
        self.elapsed = round(end - start, 1)
        self.save_json()
        self.gen_result()
        self.save_db()
        rx_queue.put(self.results)
        logger.log('DEBUG', f'结束执行{self.source}模块搜索{self.domain}的子域')


def do(domain, rx_queue):  # 统一入口名字 方便多线程调用
    """
    类统一调用入口

    :param str domain: 域名
    :param rx_queue: 结果集队列
    """
    search = So(domain)
    search.run(rx_queue)
    logger.log('INFOR', f'{search.source}模块耗时{search.elapsed}秒发现{search.domain}的子域{len(search.subdomains)}个')
    logger.log('DEBUG', f'{search.source}模块发现{search.domain}的子域 {search.subdomains}')


if __name__ == '__main__':
    result_queue = queue.Queue()
    do('owasp.org', result_queue)
