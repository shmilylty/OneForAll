from config.log import logger
from common.query import Query


class PhoneBook(Query):
    def __init__(self, domain):
        Query.__init__(self)
        self.domain = domain
        self.module = 'Dataset'
        self.source = 'PhoneBookQuery'

    def query(self):
        """
        向接口查询子域并做子域匹配
        """
        self.header = self.get_header()
        self.proxy = self.get_proxy(self.source)
        self.header.update({'Referer': 'https://phonebook.cz/',
                            'Origin': 'https://phonebook.cz'})
        addr = 'https://public.intelx.io/phonebook/search'
        key = 'd7d1ed06-f0c5-49d4-a9ca-a167e6d2ffab'
        url = f'{addr}?k={key}'
        data = {"term": self.domain, "maxresults": 10000,
                "media": 0, "target": 1,
                "terminate": [], "timeout": 20}
        resp = self.post(url, json=data)
        if not resp:
            return
        json = resp.json()
        ids = json.get('id')
        if not ids:
            logger.log('ALERT', f'Get PhoneBook id fail')
            return
        url = f'{addr}/result?k={key}&id={ids}&limit=10000'
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
    query = PhoneBook(domain)
    query.run()


if __name__ == '__main__':
    run('freebuf.com')
