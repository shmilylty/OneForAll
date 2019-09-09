import time
import config
from common import utils
from common.query import Query


class SpyseAPI(Query):
    def __init__(self, domain):
        Query.__init__(self)
        self.domain = domain
        self.module = 'Certificate'
        self.source = 'CertDBAPIQuery'
        self.addr = 'https://api.spyse.com/v1/subdomains'
        self.token = config.spyse_api_token

    def query(self):
        """
        向接口查询子域并做子域匹配
        """
        page_num = 1
        while True:
            time.sleep(self.delay)
            self.header = self.get_header()
            self.proxy = self.get_proxy(self.source)
            params = {'domain': self.domain,
                      'api_token': self.token,
                      'page': page_num}
            resp = self.get(self.addr, params)
            if not resp:
                return
            json = resp.json()
            subdomains = utils.match_subdomain(self.domain, str(json))
            if not subdomains:  # 搜索没有发现子域名则停止搜索
                break
            # 合并搜索子域名搜索结果
            self.subdomains = self.subdomains.union(subdomains)
            page_num += 1
            # 默认每次查询最多返回30条 当前条数小于30条说明已经查完
            if json.get('count') < 30:
                break

    def run(self):
        """
        类执行入口
        """
        if not self.check(self.token):
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
    query = SpyseAPI(domain)
    query.run()


if __name__ == '__main__':
    do('example.com')
