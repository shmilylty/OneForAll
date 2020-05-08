import requests
from config import api
from common.utils import match_subdomain
from common.search import Search
from config.log import logger


class GithubAPI(Search):
    def __init__(self, domain):
        Search.__init__(self)
        self.source = 'GithubAPISearch'
        self.module = 'Search'
        self.addr = 'https://api.github.com/search/code'
        self.domain = self.register(domain)
        self.session = requests.Session()
        self.auth_url = 'https://api.github.com'
        self.token = api.github_api_token

    def auth_github(self):
        """
        github api 认证

        :return: 认证失败返回False 成功返回True
        """
        self.session.headers.update({'Authorization': 'token ' + self.token})
        try:
            resp = self.session.get(self.auth_url)
        except Exception as e:
            logger.log('ERROR', e.args)
            return False
        if resp.status_code != 200:
            resp_json = resp.json()
            msg = resp_json.get('message')
            logger.log('ERROR', msg)
            return False
        else:
            return True

    def search(self):
        """
        向接口查询子域并做子域匹配
        """
        self.session.headers = self.get_header()
        self.session.proxies = self.get_proxy(self.source)
        self.session.verify = self.verify
        self.session.headers.update(
            {'Accept': 'application/vnd.github.v3.text-match+json'})

        if not self.auth_github():
            logger.log('ERROR', f'{self.source}模块登录失败')
            return
        page = 1
        while True:
            params = {'q': self.domain, 'per_page': 100,
                      'page': page, 'sort': 'indexed'}
            try:
                resp = self.session.get(self.addr, params=params)
            except Exception as e:
                logger.log('ERROR', e.args)
                break
            if resp.status_code != 200:
                logger.log('ERROR', f'{self.source}模块搜索出错')
                break
            subdomains = match_subdomain(self.domain, resp.text)
            if not subdomains:
                break
            self.subdomains = self.subdomains.union(subdomains)
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
        if not self.check(self.token):
            return
        self.begin()
        self.search()
        self.finish()
        self.save_json()
        self.gen_result()
        self.save_db()


def do(domain):  # 统一入口名字 方便多线程调用
    """
    类统一调用入口

    :param str domain: 域名
    """
    query = GithubAPI(domain)
    query.run()


if __name__ == '__main__':
    do('exmaple.com')
