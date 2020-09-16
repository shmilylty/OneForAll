from config import settings
from common.query import Query
from config.log import logger


class IPv4InfoAPI(Query):
    def __init__(self, domain):
        Query.__init__(self)
        self.domain = domain
        self.module = 'Dataset'
        self.source = 'IPv4InfoAPIQuery'
        self.addr = ' http://ipv4info.com/api_v1/'
        self.api = settings.ipv4info_api_key

    def query(self):
        """
        向接口查询子域并做子域匹配
        """
        page = 0
        while True:
            self.header = self.get_header()
            self.proxy = self.get_proxy(self.source)
            params = {'type': 'SUBDOMAINS', 'key': self.api,
                      'value': self.domain, 'page': page}
            resp = self.get(self.addr, params)
            if not resp:
                return
            if resp.status_code != 200:
                break  # 请求不正常通常网络是有问题，不再继续请求下去
            try:
                json = resp.json()
            except Exception as e:
                logger.log('DEBUG', e.args)
                break
            subdomains = self.match_subdomains(str(json))
            if not subdomains:
                break
            self.subdomains.update(subdomains)
            # 不直接使用subdomains是因为可能里面会出现不符合标准的子域名
            subdomains = json.get('Subdomains')
            if subdomains and len(subdomains) < 300:
                # ipv4info子域查询接口每次最多返回300个 用来判断是否还有下一页
                break
            page += 1
            if page >= 50:  # ipv4info子域查询接口最多允许查询50页
                break

    def run(self):
        """
        类执行入口
        """
        if not self.have_api(self.api):
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
    query = IPv4InfoAPI(domain)
    query.run()


if __name__ == '__main__':
    run('example.com')
