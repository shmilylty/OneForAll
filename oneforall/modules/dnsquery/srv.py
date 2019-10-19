#!/usr/bin/env python3

"""
通过枚举域名常见的SRV记录并做查询来发现子域
"""

import json
import asyncio

from common import utils
from common import resolve
from common.module import Module
from config import data_storage_path, logger


class BruteSRV(Module):
    def __init__(self, domain):
        Module.__init__(self)
        self.domain = self.register(domain)
        self.module = 'dnsquery'
        self.source = "BruteSRV"
        self.resolver = resolve.dns_resolver()

    async def query(self, name):
        """
        查询域名的SRV记录
        :param str name: SRV记录
        :return: 查询结果
        """
        logger.log('TRACE', f'尝试查询{name}的SRV记录')
        try:
            answers = self.resolver.query(name, 'SRV')
        except Exception as e:
            logger.log('TRACE', e)
            logger.log('TRACE', f'查询{name}的SRV记录失败')
            return None
        else:
            logger.log('TRACE', f'查询{name}的SRV记录成功')
            return answers

    def brute(self):
        """
        枚举域名的SRV记录
        """
        names_path = data_storage_path.joinpath('srv_names.json')
        with open(names_path) as fp:
            names_dict = json.load(fp)
        names = map(lambda prefix: prefix + self.domain, names_dict)

        tasks = []
        for name in names:
            tasks.append(self.query(name))
        loop = asyncio.get_event_loop()
        group = asyncio.gather(*tasks)
        results = loop.run_until_complete(group)
        loop.close()
        for result in results:
            for answer in result:
                if answer is None:
                    continue
                subdomains = utils.match_subdomain(self.domain, str(answer))
                self.subdomains = self.subdomains.union(subdomains)
        if not len(self.subdomains):
            logger.log('DEBUG', f'没有找到{self.domain}的SRV记录')

    def run(self):
        """
        类执行入口
        """
        self.begin()
        self.brute()
        self.finish()
        self.save_json()
        self.gen_result()
        self.save_db()


def do(domain):  # 统一入口名字 方便多线程调用
    """
    类统一调用入口

    :param str domain: 域名
    """
    brute = BruteSRV(domain)
    brute.run()


if __name__ == '__main__':
    do('zonetransfer.me')
    do('example.com')
