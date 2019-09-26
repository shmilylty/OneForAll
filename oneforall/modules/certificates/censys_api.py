import time
import config
from common.query import Query
from config import logger


class CensysAPI(Query):
    def __init__(self, domain):
        Query.__init__(self)
        self.domain = self.register(domain)
        self.module = 'Certificate'
        self.source = "CensysAPIQuery"
        self.addr = 'https://www.censys.io/api/v1/search/certificates'
        self.id = config.censys_api_id
        self.secret = config.censys_api_secret
        self.delay = 3.0  # Censys 接口查询速率限制 最快2.5秒查1次

    def query(self):
        """
        向接口查询子域并做子域匹配
        """
        self.header = self.get_header()
        self.proxy = self.get_proxy(self.source)
        data = {
            'query': f'parsed.names: {self.domain}',
            'page': 1,
            'fields': ['parsed.subject_dn', 'parsed.names'],
            'flatten': True}
        resp = self.post(self.addr, json=data, auth=(self.id, self.secret))
        if not resp:
            return
        json = resp.json()
        status = json.get('status')
        if status != 'ok':
            logger.log('ALERT', status)
            return
        subdomains = self.match(self.domain, str(json))
        self.subdomains = self.subdomains.union(subdomains)
        pages = json.get('metadata').get('pages')
        for page in range(2, pages + 1):
            time.sleep(self.delay)
            data['page'] = page
            resp = self.post(self.addr, json=data, auth=(self.id, self.secret))
            if not resp:
                return
            subdomains = self.match(self.domain, str(resp.json()))
            self.subdomains = self.subdomains.union(subdomains)

    def run(self):
        """
        类执行入口
        """
        if not self.check(self.id, self.secret):
            return
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
    query = CensysAPI(domain)
    query.run()


if __name__ == '__main__':
    do('example.com')
