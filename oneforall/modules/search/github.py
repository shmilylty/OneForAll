import re
import time
import requests
import config
from bs4 import BeautifulSoup
from common.search import Search
from config import logger


class Github(Search):
    def __init__(self, domain):
        Search.__init__(self)
        self.source = 'GithubSearch'
        self.module = 'Search'
        self.addr = 'https://github.com/search'
        self.domain = self.register(domain)
        self.header = self.get_header()
        self.session = requests.Session()
        self.login_url = 'https://github.com/login'
        self.post_url = 'https://github.com/session'
        self.email = config.github_email
        self.password = config.github_password

    def login_github(self):
        """
        登录github

        :return: 登录失败返回False 成功返回True
        """
        token = self.get_token()
        if token is None:
            logger.log('ERROR', f'{self.source}模块获取token失败')
            return False
        post_data = {
            'commit': 'Sign in',
            'utf8': '✓',
            'authenticity_token': token,
            'login': self.email,
            'password': self.password
        }
        resp = self.session.post(self.post_url, data=post_data)
        if resp.status_code != 200:
            return False
        match = re.search(r'"user-login" content="(.*?)"', resp.text)
        if match:
            return True

    def get_token(self):
        """
        获取github登录token

        :return: 获取失败返回None，成功返回token
        """
        resp = self.session.get(self.login_url)
        if resp.status_code != 200:
            return None
        match = re.search(
            r'name="authenticity_token" value="(.*?)"', resp.text)
        if not match:
            return None
        return match.group(1)

    def search(self, full_search=True):
        """
        向接口查询子域并做子域匹配
        """
        self.session.headers = self.get_header()
        self.session.proxies = self.get_proxy(self.source)
        self.session.verify = self.verify
        if not self.login_github():
            logger.log('ERROR', f'{self.session}模块登录失败')
            return
        page_num = 1
        while True:
            time.sleep(self.delay)
            params = {'p': page_num, 'q': f'"{self.domain}"', 'type': 'Code'}
            resp = self.session.get(self.addr, params=params)
            if resp.status_code != 200:
                logger.log('ERROR', f'{self.session}模块搜索出错')
                break
            soup = BeautifulSoup(resp.text, 'lxml')
            subdomains = self.match(self.domain, soup.text)
            self.subdomains = self.subdomains.union(subdomains)
            if not subdomains:
                break
            if not full_search:
                # 搜索中发现搜索出的结果有完全重复的结果就停止搜索
                if subdomains.issubset(self.subdomains):
                    break
            if 'class="next_page disabled"' in resp.text:
                break
            if page_num > 100:
                break
            page_num += 1

    def run(self):
        """
        类执行入口
        """
        if not self.check(self.email, self.password):
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
    query = Github(domain)
    query.run()


if __name__ == '__main__':
    do('mi.com')
