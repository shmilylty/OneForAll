import time

from config import settings
from common.search import Search
from config.log import logger


class GithubAPI(Search):
    def __init__(self, domain):
        Search.__init__(self)
        self.source = 'GithubAPISearch'
        self.module = 'Search'
        self.addr = 'https://api.github.com/search/code'
        self.domain = domain
        self.delay = 5
        self.token = settings.github_api_token

    def search(self):
        """
        向接口查询子域并做子域匹配
        """
        self.header = self.get_header()
        self.proxy = self.get_proxy(self.source)
        self.header.update(
            {'Accept': 'application/vnd.github.v3.text-match+json'})
        self.header.update(
            {'Authorization': 'token ' + self.token})

        page = 1
        while True:
            time.sleep(self.delay)
            params = {'q': self.domain, 'per_page': 100,
                      'page': page, 'sort': 'indexed',
                      'access_token': self.token}
            try:
                resp = self.get(self.addr, params=params)
            except Exception as e:
                logger.log('ERROR', e.args)
                break
            if not resp or resp.status_code != 200:
                logger.log('ERROR', f'{self.source} module query failed')
                break
            subdomains = self.match_subdomains(resp)
            if not subdomains:
                break
            self.subdomains.update(subdomains)
            page += 1
            try:
                resp_json = resp.json()
            except Exception as e:
                logger.log('ERROR', e.args)
                break
            total_count = resp_json.get('total_count')
            if not isinstance(total_count, int):
                break
            if page * 100 > total_count:
                break
            if page * 100 > 1000:
                break

    def run(self):
        """
        类执行入口
        """
        if not self.have_api(self.token):
            return
        self.begin()
        self.search()
        self.finish()
        self.save_json()
        self.gen_result()
        self.save_db()


def run(domain):
    """
    类统一调用入口

    :param str domain: 域名
    """
    query = GithubAPI(domain)
    query.run()


if __name__ == '__main__':
    run('freebuf.com')
