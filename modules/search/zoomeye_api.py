import time
from config import settings
from common.search import Search
from config.log import logger


class ZoomEyeAPI(Search):
    def __init__(self, domain):
        Search.__init__(self)
        self.domain = domain
        self.module = 'Search'
        self.source = 'ZoomEyeAPISearch'
        self.addr = 'https://api.zoomeye.org/web/search'
        self.delay = 2
        self.user = settings.zoomeye_api_usermail
        self.pwd = settings.zoomeye_api_password

    def login(self):
        """
        登陆获取查询taken
        """
        url = 'https://api.zoomeye.org/user/login'
        data = {'username': self.user, 'password': self.pwd}
        resp = self.post(url=url, json=data)
        if not resp:
            logger.log('ALERT', f'{self.source} module login failed')
            return None
        data = resp.json()
        if resp.status_code == 200:
            logger.log('DEBUG', f'{self.source} module login success')
            return data.get('access_token')
        else:
            logger.log('ALERT', data.get('message'))
            return None

    def search(self):
        """
        发送搜索请求并做子域匹配
        """
        page_num = 1
        access_token = self.login()
        if not access_token:
            return
        while True:
            time.sleep(self.delay)
            self.header = self.get_header()
            self.proxy = self.get_proxy(self.source)
            self.header.update({'Authorization': 'JWT ' + access_token})
            params = {'query': 'hostname:' + self.domain, 'page': page_num}
            resp = self.get(self.addr, params)
            subdomains = self.match_subdomains(resp)
            if not subdomains:  # 搜索没有发现子域名则停止搜索
                break
            self.subdomains.update(subdomains)
            page_num += 1
            if page_num > 500:
                break
            if resp.status_code == 403:
                break

    def run(self):
        """
        类执行入口
        """
        if not self.have_api(self.user, self.pwd):
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
    search = ZoomEyeAPI(domain)
    search.run()


if __name__ == '__main__':
    run('mi.com')
