# coding=utf-8
import time
import queue
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
        :return:
        """
        url = 'https://api.zoomeye.org/user/login'
        data = {'username': self.user, 'password': self.pwd}
        resp = self.post(url=url, json=data)
        if not resp:
            logger.log('FETAL', f'登录失败无法获取{self.source}的访问token')
            return
        resp_json = resp.json()
        if resp.status_code == 200:
            # print('登陆成功')
            return resp_json.get('access_token')
        else:
            logger.log('ALERT', resp_json.get('message'))
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
            subdomain_find = self.match(self.domain, resp.text)
            self.subdomains = self.subdomains.union(subdomain_find)
            page_num += 1
            if page_num > 500:
                break
            if resp.status_code == 403:
                break

    def run(self, rx_queue):
        """
        类执行入口
        """
        if not (self.user and self.pwd):
            logger.log('ERROR', f'{self.source}模块API配置错误')
            logger.log('ALERT', f'不执行{self.source}模块')
            return
        logger.log('DEBUG', f'开始执行{self.source}模块搜索{self.domain}的子域')

        self.search()

        self.save_json()
        self.gen_result()
        self.save_db()
        rx_queue.put(self.results)
        logger.log('DEBUG', f'结束执行{self.source}模块搜索{self.domain}的子域')


def do(domain, rx_queue):  # 统一入口名字 方便多线程调用
    """
    类统一调用入口

    :param str domain: 域名
    :param rx_queue: 结果集队列
    """
    search = ZoomEyeAPI(domain)
    search.run(rx_queue)


if __name__ == '__main__':
    result_queue = queue.Queue()
    do('example.com', result_queue)
