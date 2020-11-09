import time
from bs4 import BeautifulSoup
from common.search import Search


class Baidu(Search):
    def __init__(self, domain):
        Search.__init__(self)
        self.module = 'Search'
        self.source = 'BaiduSearch'
        self.addr = 'https://www.baidu.com/s'
        self.domain = domain
        self.limit_num = 750  # 限制搜索条数

    def redirect_match(self, html):
        """
        获取跳转地址并传递地址进行跳转head请求

        :param html: 响应体
        :return: 子域
        """
        bs = BeautifulSoup(html, 'html.parser')
        subdomains_all = set()
        # 获取搜索结果中所有的跳转URL地址
        for find_res in bs.find_all('a', {'class': 'c-showurl'}):
            url = find_res.get('href')
            subdomains = self.match_location(url)
            subdomains_all.update(subdomains)
        return subdomains_all

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
            self.proxy = self.get_proxy(self.source)
            query = 'site:.' + domain + filtered_subdomain
            params = {'wd': query,
                      'pn': self.page_num,
                      'rn': self.per_page_num}
            resp = self.get(self.addr, params)
            if not resp:
                return
            if len(domain) > 12:  # 解决百度搜索结果中域名过长会显示不全的问题
                # 获取百度跳转URL响应头的Location字段获取直链
                subdomains = self.redirect_match(resp.text)
            else:
                subdomains = self.match_subdomains(resp, fuzzy=False)
            if not self.check_subdomains(subdomains):
                break
            self.subdomains.update(subdomains)
            self.page_num += self.per_page_num
            # 搜索页面没有出现下一页时停止搜索
            if f'&pn={self.page_num}&' not in resp.text:
                break
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
    search = Baidu(domain)
    search.run()


if __name__ == '__main__':
    run('mi.com')
