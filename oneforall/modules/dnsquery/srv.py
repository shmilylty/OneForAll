#!/usr/bin/env python3

"""
通过枚举域名常见的SRV记录并做查询来发现子域
"""

import asyncio
import json

import aiodns

from common import utils
from common.module import Module
from config import data_storage_path, logger, resolver_nameservers


class BruteSRV(Module):
    def __init__(self, domain: str):
        Module.__init__(self)
        self.domain = self.register(domain)
        self.module = 'dnsquery'
        self.source = "BruteSRV"
        self.loop = asyncio.new_event_loop()
        self.nameservers = resolver_nameservers
        self.resolver = aiodns.DNSResolver(self.nameservers, self.loop)

    async def query(self, name):
        """
        查询域名的SRV记录
        :param str name: SRV记录
        :return: 查询结果
        """
        logger.log('TRACE', f'尝试查询{name}的SRV记录')
        try:
            answers = await self.resolver.query(name, 'SRV')
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
        query_map = map(lambda name: name + self.domain, names_dict)

        tasks = []
        for query in query_map:
            tasks.append(self.query(query))
        task_group = asyncio.gather(*tasks, loop=self.loop)
        self.loop.run_until_complete(asyncio.gather(task_group))
        self.loop.close()
        results = task_group.result()
        for result in results:
            if result:
                for answer in result:
                    subdomain = utils.match_subdomain(self.domain, answer.host)
                    if subdomain:
                        self.subdomains = self.subdomains.union(subdomain)
                    else:
                        logger.log('DEBUG', f'{answer.host}不是{self.domain}的子域')
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

    do('example.com')
