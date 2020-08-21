"""
检查crossdomain.xml文件收集子域名
"""
from common.check import Check


class CheckCDX(Check):
    """
    检查crossdomain.xml文件收集子域名
    """
    def __init__(self, domain: str):
        Check.__init__(self)
        self.domain = domain
        self.module = 'Check'
        self.source = "CrossDomainXml"

    def check(self):
        """
        检查crossdomain.xml收集子域名
        """
        filenames = {'crossdomain.xml'}
        self.to_check(filenames)

    def run(self):
        """
        类执行入口
        """
        self.begin()
        self.check()
        self.finish()
        self.save_json()
        self.gen_result()
        self.save_db()


def run(domain):
    """
    类统一调用入口

    :param domain: 域名
    """
    check = CheckCDX(domain)
    check.run()


if __name__ == '__main__':
    run('example.com')
