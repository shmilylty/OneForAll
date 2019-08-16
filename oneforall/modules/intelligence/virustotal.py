import time

from common.query import Query

'''
最多查询100条
'''


class VirusTotal(Query):
    def __init__(self, domain):
        Query.__init__(self)
        self.source = 'VirusTotalQuery'
        self.module = 'Intelligence'
        self.addr = 'https://www.virustotal.com/ui/domains/{}/subdomains'
        self.domain = self.register(domain)

    def query(self):
        """
        向接口查询子域并做子域匹配
        """
        next_cursor = ''
        while True:
            time.sleep(self.delay)
            self.header = self.get_header()
            self.header.update({'Referer': 'https://www.virustotal.com/',
                                'TE': 'Trailers'})
            self.proxy = self.get_proxy(self.source)
            params = {'limit': '40', 'cursor': next_cursor}
            resp = self.get(url=self.addr.format(self.domain), params=params)
            if not resp:
                return
            data = resp.json()
            subdomains = set()
            datas = data.get('data')

            if datas:
                for data in datas:
                    subdomain = data.get('id')
                    if subdomain:
                        subdomains.add(subdomain)
            else:
                break
            self.subdomains = self.subdomains.union(subdomains)
            meta = data.get('meta')
            if meta:
                next_cursor = meta.get('cursor')
            else:
                break

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
    query = VirusTotal(domain)
    query.run()


if __name__ == '__main__':
    do('example.com')
