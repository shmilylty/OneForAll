from common.query import Query


class DNSDumpster(Query):
    def __init__(self, domain):
        Query.__init__(self)
        self.domain = domain
        self.module = 'Dataset'
        self.source = "DNSDumpsterQuery"
        self.addr = 'https://dnsdumpster.com/'

    def query(self):
        """
        向接口查询子域并做子域匹配
        """
        self.header = self.get_header()
        self.header.update({'Referer': 'https://dnsdumpster.com'})
        self.proxy = self.get_proxy(self.source)
        resp = self.get(self.addr)
        if not resp:
            return
        self.cookie = resp.cookies
        data = {'csrfmiddlewaretoken': self.cookie.get('csrftoken'),
                'targetip': self.domain}
        resp = self.post(self.addr, data)
        self.subdomains = self.collect_subdomains(resp)

    def run(self):
        """
        类执行入口
        """
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
    query = DNSDumpster(domain)
    query.run()


if __name__ == '__main__':
    run('mi.com')
