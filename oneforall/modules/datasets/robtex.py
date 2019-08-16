import json
import time

from common.query import Query


class Robtex(Query):
    def __init__(self, domain):
        Query.__init__(self)
        self.domain = self.register(domain)
        self.module = 'Dataset'
        self.source = "RobtexQuery"
        self.addr = 'https://freeapi.robtex.com/pdns/'

    def query(self):
        """
        向接口查询子域并做子域匹配
        """
        self.header = self.get_header()
        self.proxy = self.get_proxy(self.source)
        url = self.addr + 'forward/' + self.domain
        resp = self.get(url)
        if not resp:
            return
        text_list = resp.text.splitlines()
        text_json = list(map(lambda x: json.loads(x), text_list))
        for record in text_json:
            if record.get('rrtype') in ['A', 'AAAA']:
                time.sleep(self.delay)  # Robtex有查询频率限制
                ip = record.get('rrdata')
                url = self.addr + 'reverse/' + ip
                resp = self.get(url)
                if not resp:
                    return
                subdomains = self.match(self.domain, resp.text)
                if subdomains:
                    # 合并搜索子域名搜索结果
                    self.subdomains = self.subdomains.union(subdomains)

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
    query = Robtex(domain)
    query.run()


if __name__ == '__main__':
    do('example.com')
