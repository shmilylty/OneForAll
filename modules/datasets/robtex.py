import json
import time

from common.query import Query


class Robtex(Query):
    def __init__(self, domain):
        Query.__init__(self)
        self.domain = domain
        self.module = 'Dataset'
        self.source = "RobtexQuery"

    def query(self):
        """
        向接口查询子域并做子域匹配
        """
        self.header = self.get_header()
        self.proxy = self.get_proxy(self.source)
        base_addr = 'https://freeapi.robtex.com/pdns'
        url = f'{base_addr}/forward/{self.domain}'
        resp = self.get(url)
        if not resp:
            return
        text_list = resp.text.splitlines()
        for item in text_list:
            record = json.loads(item)
            if record.get('rrtype') in ['A', 'AAAA']:
                time.sleep(self.delay)  # Robtex有查询频率限制
                ip = record.get('rrdata')
                url = f'{base_addr}/reverse/{ip}'
                resp = self.get(url)
                self.subdomains = self.collect_subdomains(resp)

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


def run(domain):
    """
    类统一调用入口

    :param str domain: 域名
    """
    query = Robtex(domain)
    query.run()


if __name__ == '__main__':
    run('google.com')
