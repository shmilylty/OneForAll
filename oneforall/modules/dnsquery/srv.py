#!/usr/bin/env python3

"""
通过枚举域名常见的SRV记录并做查询来发现子域
"""

import json
import queue
import threading

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
        self.thread_num = 10
        self.names_que = queue.Queue()
        self.answers_que = queue.Queue()

    def gen_names(self):
        path = data_storage_path.joinpath('srv_prefixes.json')
        with open(path) as file:
            prefixes = json.load(file)
        names = map(lambda prefix: prefix + self.domain, prefixes)

        for name in names:
            self.names_que.put(name)

    def brute(self):
        """
        枚举域名的SRV记录
        """
        self.gen_names()

        for i in range(self.thread_num):
            thread = BruteThread(self.names_que, self.answers_que)
            thread.daemon = True
            thread.start()

        self.names_que.join()

        while not self.answers_que.empty():
            answer = self.answers_que.get()
            if answer is not None:
                for item in answer:
                    subdomains = utils.match_subdomain(self.domain, str(item))
                    self.subdomains = self.subdomains.union(subdomains)

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


class BruteThread(threading.Thread):
    def __init__(self, names_que, answers_que):
        threading.Thread.__init__(self)
        self.names_que = names_que
        self.answers_que = answers_que
        self.resolver = resolve.dns_resolver()

    def query(self, name):
        """
        查询域名的SRV记录
        :param str name: SRV记录
        :return: 查询结果
        """
        logger.log('TRACE', f'尝试查询{name}的SRV记录')
        try:
            answer = self.resolver.query(name, 'SRV')
        except Exception as exception:
            logger.log('TRACE', exception.args)
            logger.log('TRACE', f'查询{name}的SRV记录失败')
            return None
        else:
            logger.log('TRACE', f'查询{name}的SRV记录成功')
            return answer

    def run(self):
        while True:
            name = self.names_que.get()
            answer = self.query(name)
            self.answers_que.put(answer)
            self.names_que.task_done()


def do(domain):  # 统一入口名字 方便多线程调用
    """
    类统一调用入口

    :param str domain: 域名
    """
    brute = BruteSRV(domain)
    brute.run()


if __name__ == '__main__':
    do('zonetransfer.me')
    # do('example.com')
