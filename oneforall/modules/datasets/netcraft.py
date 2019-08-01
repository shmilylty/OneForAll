# coding=utf-8
import re
import time
import queue
import hashlib
from urllib import parse
from common.query import Query
from config import logger


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
        self.cookie = self.get(self.init).cookies
        cookie_value = self.cookie['netcraft_js_verification_challenge']
        verify_taken = hashlib.sha1(parse.unquote(cookie_value).encode('utf-8')).hexdigest()
        self.cookie['netcraft_js_verification_response'] = verify_taken

    def query(self):
        """
        向接口查询子域并做子域匹配
        """
        self.bypass_verification()
        last = ''
        while True:
            time.sleep(self.delay)
            self.header = self.get_header()
            self.proxy = self.get_proxy(self.source)
            params = {'host': '*.' + self.domain, 'from': self.page_num}
            resp = self.get(self.addr + last, params)
            if not resp:
                return
            subdomains_find = self.match(self.domain, resp.text)
            if not subdomains_find:  # 搜索没有发现子域名则停止搜索
                break
            self.subdomains = self.subdomains.union(subdomains_find)  # 合并搜索子域名搜索结果
            if 'Next page' not in resp.text:  # 搜索页面没有出现下一页时停止搜索
                break
            last = re.search(r'&last=.*' + self.domain, resp.text).group(0)
            self.page_num += self.per_page_num

    def run(self, rx_queue):
        """
        类执行入口
        """
        logger.log('DEBUG', f'开始执行{self.source}模块查询{self.domain}的子域')
        start = time.time()
        self.query()
        end = time.time()
        self.elapsed = round(end - start, 1)
        self.save_json()
        self.gen_result()
        self.save_db()
        rx_queue.put(self.results)
        logger.log('DEBUG', f'结束执行{self.source}模块查询{self.domain}的子域')


def do(domain, rx_queue):  # 统一入口名字 方便多线程调用
    """
    类统一调用入口

    :param str domain: 域名
    :param rx_queue: 结果集队列
    """
    query = NetCraft(domain)
    query.run(rx_queue)
    logger.log('INFOR', f'{query.source}模块耗时{query.elapsed}秒发现{query.domain}的子域{len(query.subdomains)}个')
    logger.log('DEBUG', f'{query.source}模块发现{query.domain}的子域 {query.subdomains}')


if __name__ == '__main__':
    result_queue = queue.Queue()
    do('owasp.org', result_queue)
