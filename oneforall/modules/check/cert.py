#!/usr/bin/env python3
# coding=utf-8

"""
检查域名证书收集子域名
"""
import socket
import ssl

from common import utils
from common.module import Module
from config import logger


class CheckCert(Module):
    def __init__(self, domain):
        Module.__init__(self)
        self.domain = self.register(domain)
        self.port = 443  # ssl port
        self.module = 'Check'
        self.source = 'CertInfo'

    def check(self):
        """
        获取域名证书并匹配证书中的子域名
        """
        ctx = ssl.create_default_context()
        sock = ctx.wrap_socket(socket.socket(), server_hostname=self.domain)
        try:
            sock.connect((self.domain, self.port))
            cert_dict = sock.getpeercert()
        except Exception as e:
            logger.log('ERROR', e)
            return
        subdomains_find = utils.match_subdomain(self.domain, str(cert_dict))
        self.subdomains = self.subdomains.union(subdomains_find)

    def run(self):
        """
        类执行入口
        """
        logger.log('DEBUG', f'开始执行{self.source}检查{self.domain}域的证书中的子域')
        self.check()
        self.save_json()
        self.gen_result()
        self.save_db()
        logger.log('DEBUG', f'结束执行{self.source}检查{self.domain}域的证书中的子域')
        self.finish()


def do(domain):  # 统一入口名字 方便多线程调用
    """
    类统一调用入口

    :param str domain: 域名
    """
    check = CheckCert(domain)
    check.run()


if __name__ == '__main__':
    do('example.com')
