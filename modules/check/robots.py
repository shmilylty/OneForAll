"""
检查内容安全策略收集子域名收集子域名
"""
from common.check import Check


class Robots(Check):
    def __init__(self, domain):
        Check.__init__(self)
        self.domain = domain
        self.module = 'check'
        self.source = 'RobotsCheck'

    def check(self):
        """
        正则匹配域名的robots.txt文件中的子域
        """
        filenames = {'robots.txt'}
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

    :param str domain: 域名
    """
    check = Robots(domain)
    check.run()


if __name__ == '__main__':
    run('qq.com')
