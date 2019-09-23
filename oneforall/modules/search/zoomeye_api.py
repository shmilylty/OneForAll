import time
import config
from common.search import Search
from config import logger


class ZoomEyeAPI(Search):
    def __init__(self, domain):
        Search.__init__(self)
        self.domain = domain
        self.module = 'Search'
        self.source = 'ZoomEyeAPISearch'
        self.addr = 'https://api.zoomeye.org/web/search'
        self.delay = 2
        self.user = config.zoomeye_api_username
        self.pwd = config.zoomeye_api_password

    def login(self):
        """
        登陆获取查询taken
        """
        url = 'https://api.zoomeye.org/user/login'
        data = {'username': self.user, 'password': self.pwd}
        resp = self.post(url=url, json=data)
        if not resp:
            logger.log('FATAL', f'登录失败无法获取{self.source}的访问token')
            return
        data = resp.json()
        if resp.status_code == 200:
            logger.log('DEBUG', f'{self.source}模块登录成功')
            return data.get('access_token')
        else:
            logger.log('ALERT', data.get('message'))
            exit(1)

    def search(self):
        """
        发送搜索请求并做子域匹配
        """
        page_num = 1
        access_token = self.login()
        while True:
            time.sleep(self.delay)
            self.header = self.get_header()
            self.proxy = self.get_proxy(self.source)
            self.header.update({'Authorization': 'JWT ' + access_token})
            params = {'query': 'hostname:' + self.domain, 'page': page_num}
            resp = self.get(self.addr, params)
            if not resp:
                return
            subdomains = self.match(self.domain, resp.text)
            if not subdomains:  # 搜索没有发现子域名则停止搜索
                break
            self.subdomains = self.subdomains.union(subdomains)
            page_num += 1
            if page_num > 500:
                break
            if resp.status_code == 403:
                break

    def run(self):
        """
        类执行入口
        """
        if not self.check(self.user, self.pwd):
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
    search = ZoomEyeAPI(domain)
    search.run()


if __name__ == '__main__':
    do('example.com')
