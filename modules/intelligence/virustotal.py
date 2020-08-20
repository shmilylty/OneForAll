from common.query import Query

'''
最多查询100条
'''


class VirusTotal(Query):
    def __init__(self, domain):
        Query.__init__(self)
        self.source = 'VirusTotalQuery'
        self.module = 'Intelligence'
        self.domain = domain

    def query(self):
        """
        向接口查询子域并做子域匹配
        """
        next_cursor = ''
        while True:
            self.header = self.get_header()
            self.header.update({'Referer': 'https://www.virustotal.com/',
                                'TE': 'Trailers'})
            self.proxy = self.get_proxy(self.source)
            params = {'limit': '40', 'cursor': next_cursor}
            addr = f'https://www.virustotal.com/ui/domains/{self.domain}/subdomains'
            resp = self.get(url=addr, params=params)
            if not resp:
                break
            subdomains = self.match_subdomains(resp)
            if not subdomains:
                break
            self.subdomains.update(subdomains)
            data = resp.json()
            next_cursor = data.get('meta').get('cursor')

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
    query = VirusTotal(domain)
    query.run()


if __name__ == '__main__':
    run('mi.com')
