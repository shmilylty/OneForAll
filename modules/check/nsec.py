# https://www.icann.org/resources/pages/dnssec-what-is-it-why-important-2019-03-20-zh
# https://appsecco.com/books/subdomain-enumeration/active_techniques/zone_walking.html

from common import utils
from common.check import Check


class NSEC(Check):
    def __init__(self, domain):
        Check.__init__(self)
        self.domain = domain
        self.module = 'check'
        self.source = "NSECCheck"

    def walk(self):
        domain = self.domain
        while True:
            answer = utils.dns_query(domain, 'NSEC')
            if answer is None:
                break
            subdomain = str()
            for item in answer:
                record = item.to_text()
                subdomains = self.match_subdomains(record)
                subdomain = ''.join(subdomains)  # 其实这里的subdomains的长度为1 也就是说只会有一个子域
                self.subdomains.update(subdomains)
            if subdomain == self.domain:  # 当查出子域为主域 说明完成了一个循环 不再继续查询
                break
            if domain != self.domain:  # 防止出现wwdmas.cn 000.000.wwdmas.cn 000.000.000.wwdmas.cn情况
                if domain.split('.')[0] == subdomain.split('.')[0]:
                    break
            domain = subdomain
        return self.subdomains

    def run(self):
        """
        类执行入口
        """
        self.begin()
        self.walk()
        self.finish()
        self.save_json()
        self.gen_result()
        self.save_db()


def run(domain):
    """
    类统一调用入口

    :param str domain: 域名
    """
    brute = NSEC(domain)
    brute.run()


if __name__ == '__main__':
    run('iana.org')
