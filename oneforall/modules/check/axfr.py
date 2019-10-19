"""
查询域名的NS记录(域名服务器记录，记录该域名由哪台域名服务器解析)，检查查出的域名服务器是
否开启DNS域传送，如果开启且没做访问控制和身份验证便加以利用获取域名的所有记录。

DNS域传送(DNS zone transfer)指的是一台备用域名服务器使用来自主域名服务器的数据刷新自己
的域数据库，目的是为了做冗余备份，防止主域名服务器出现故障时 dns 解析不可用。
当主服务器开启DNS域传送同时又对来请求的备用服务器未作访问控制和身份验证便可以利用此漏洞获
取某个域的所有记录。
"""
import dns.resolver
import dns.zone

from common import resolve, utils
from common.module import Module
from config import logger


class CheckAXFR(Module):
    """
    DNS域传送漏洞检查类
    """
    def __init__(self, domain: str):
        Module.__init__(self)
        self.domain = self.register(domain)
        self.module = 'Check'
        self.source = 'AXFRCheck'
        self.results = []

    def axfr(self, server):
        """
        执行域传送

        :param server: 域名服务器
        """
        logger.log('DEBUG', f'尝试对{self.domain}的域名服务器{server}进行域传送')
        try:
            xfr = dns.query.xfr(where=server, zone=self.domain)
            zone = dns.zone.from_xfr(xfr)
        except Exception as e:
            logger.log('DEBUG', str(e))
            logger.log('DEBUG', f'对{self.domain}的域名服务器{server}进行域传送失败')
            return
        names = zone.nodes.keys()
        for name in names:
            full_domain = str(name) + '.' + self.domain
            subdomain = utils.match_subdomain(self.domain, full_domain)
            self.subdomains = self.subdomains.union(subdomain)
            record = zone[name].to_text(name)
            self.results.append(record)
        if self.results:
            logger.log('DEBUG', f'发现{self.domain}在{server}上的域传送记录')
            logger.log('DEBUG', '\n'.join(self.results))
            self.results = []

    def check(self):
        """
        正则匹配响应头中的内容安全策略字段以发现子域名
        """
        resolver = resolve.dns_resolver()
        try:
            answers = resolver.query(self.domain, "NS")
        except Exception as e:
            logger.log('ERROR', e)
            return
        nsservers = [str(answer) for answer in answers]
        if not len(nsservers):
            logger.log('ALERT', f'没有找到{self.domain}的NS域名服务器记录')
            return
        for nsserver in nsservers:
            self.axfr(nsserver)

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


def do(domain):  # 统一入口名字 方便多线程调用
    """
    类统一调用入口

    :param str domain: 域名
    """
    check = CheckAXFR(domain)
    check.run()


if __name__ == '__main__':
    do('ZoneTransfer.me')
    # do('example.com')
