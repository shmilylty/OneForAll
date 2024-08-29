from config import settings
from common.query import Query
from config.log import logger


class CensysAPI(Query):
    def __init__(self, domain):
        Query.__init__(self)
        self.domain = domain
        self.module = 'Certificate'
        self.source = "CensysAPIQuery"
        self.addr = 'https://search.censys.io/api/v2/certificates/search'
        self.id = settings.censys_api_id
        self.secret = settings.censys_api_secret
        self.delay = 3.0  # Censys 接口查询速率限制 最快2.5秒查1次

    def query(self):
        """
        向接口查询子域并做子域匹配
        """
        self.header = self.get_header()
        self.proxy = self.get_proxy(self.source)
        params = {
            'q': f'names: {self.domain}',
            'per_page': 100,
        }
        resp = self.get(self.addr, params=params, auth=(self.id, self.secret))
        if not resp:
            return
        json = resp.json()
        status = json.get('status')
        if status != 'OK':
            logger.log('ALERT', f'{self.source} module {status}')
            return
        subdomains = self.match_subdomains(resp.text)
        self.subdomains.update(subdomains)
        next_cursor = json.get("result").get("links").get("next")
        while next_cursor:
            tmp_params = {
                'q': f'names: {self.domain}',
                'per_page': 100,
                "cursor": next_cursor
            }
            tmp_resp = self.get(self.addr, params=tmp_params, auth=(self.id, self.secret))
            self.subdomains = self.collect_subdomains(tmp_resp)
            next_cursor = tmp_resp.json().get("result").get("links").get("next")

    def run(self):
        """
        类执行入口
        """
        if not self.have_api(self.id, self.secret):
            return
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
    query = CensysAPI(domain)
    query.run()


if __name__ == '__main__':
    run('example.com')
