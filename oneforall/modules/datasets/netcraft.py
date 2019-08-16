import hashlib
import re
import time
from urllib import parse

from common.query import Query


class NetCraft(Query):
    def __init__(self, domain):
        Query.__init__(self)
        self.domain = self.register(domain)
        self.module = 'Dataset'
        self.source = 'NetCraftQuery'
        self.init = 'https://searchdns.netcraft.com/'
        self.addr = 'https://searchdns.netcraft.com/?restriction=site+contains'
        self.page_num = 1
        self.per_page_num = 20

    def bypass_verification(self):
        """
        绕过NetCraft的JS验证
        """
        self.header = self.get_header()  # Netcraft会检查User-Agent
        resp = self.get(self.init)
        if not resp:
            return None
        self.cookie = resp.cookies
        cookie_value = self.cookie['netcraft_js_verification_challenge']
        cookie_encode = parse.unquote(cookie_value).encode('utf-8')
        verify_taken = hashlib.sha1(cookie_encode).hexdigest()
        self.cookie['netcraft_js_verification_response'] = verify_taken

    def query(self):
        """
        向接口查询子域并做子域匹配
        """
        if not self.bypass_verification():
            return
        last = ''
        while True:
            time.sleep(self.delay)
            self.header = self.get_header()
            self.proxy = self.get_proxy(self.source)
            params = {'host': '*.' + self.domain, 'from': self.page_num}
            resp = self.get(self.addr + last, params)
            if not resp:
                return
            subdomains = self.match(self.domain, resp.text)
            if not subdomains:  # 搜索没有发现子域名则停止搜索
                break
            # 合并搜索子域名搜索结果
            self.subdomains = self.subdomains.union(subdomains)
            if 'Next page' not in resp.text:  # 搜索页面没有出现下一页时停止搜索
                break
            last = re.search(r'&last=.*' + self.domain, resp.text).group(0)
            self.page_num += self.per_page_num

    def run(self):
        """
        类执行入口
        """
        self.begin()
        self.query()
        self.finish()
        self.save_json()
        self.gen_result()
        self.save_db()


def do(domain):  # 统一入口名字 方便多线程调用
    """
    类统一调用入口

    :param str domain: 域名
    """
    query = NetCraft(domain)
    query.run()


if __name__ == '__main__':
    do('example.com')
