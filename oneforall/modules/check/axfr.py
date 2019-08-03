# coding=utf-8
"""
查询域名的NS记录(域名服务器记录，记录该域名由哪台域名服务器解析)，
检查查出的域名服务器是否开启DNS域传送，如果开启且没做访问控制和身份验证便加以利用获取域名的所有记录

DNS域传送(DNS zone transfer)指的是一台备用域名服务器使用来自主域名服务器的数据刷新自己的域数据库，
目的是为了做冗余备份，防止主域名服务器出现故障时 dns 解析不可用。
当主服务器开启DNS域传送同时又对来请求的备用服务器未作访问控制和身份验证便可以利用此漏洞获取某个域的所有记录。
"""
import queue
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
        self.nsservers = []
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
        self.nsservers = [str(answer) for answer in answers]
        if not len(self.nsservers):
            logger.log('ALERT', f'没有找到{self.domain}的NS域名服务器记录')
            return
        for nsserver in self.nsservers:
            logger.log('DEBUG', f'正在尝试对{self.domain}的域名服务器{nsserver}进行域传送')
            try:
                xfr = dns.query.xfr(nsserver, self.domain)
                zone = dns.zone.from_xfr(xfr)
            except Exception as e:
                logger.log('DEBUG', str(e))
                logger.log('DEBUG', f'对{self.domain}的域名服务器{nsserver}进行域传送失败')
                continue
            else:
                names = zone.nodes.keys()
                for name in names:
                    subdomain = utils.match_subdomain(self.domain, str(name) + '.' + self.domain)
                    self.subdomains = self.subdomains.union(subdomain)
                    record = zone[name].to_text(name)
                    self.results.append(record)
            if self.results:
                logger.log('DEBUG', f'发现{self.domain}在{nsserver}上的域传送记录')
                logger.log('DEBUG', '\n'.join(self.results))
                self.results = []

    def run(self, rx_queue):
        """
        类执行入口
        """
        self.begin()
        logger.log('DEBUG', f'开始执行{self.source}检查{self.domain}的域传送漏洞')
        self.check()
        self.save_json()
        self.gen_result()
        self.save_db()
        rx_queue.put(self.results)
        logger.log('DEBUG', f'结束执行{self.source}检查{self.domain}的域传送漏洞')
        self.finish()


def do(domain, rx_queue):  # 统一入口名字 方便多线程调用
    """
    类统一调用入口

    :param str domain: 域名
    :param rx_queue: 结果集队列
    """
    check = CheckAXFR(domain)
    check.run(rx_queue)


if __name__ == '__main__':
    # do('ZoneTransfer.me')
    result_queue = queue.Queue()
    do('example.com', result_queue)
