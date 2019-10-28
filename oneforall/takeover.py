#!/usr/bin/python3
# coding=utf-8

"""
OneForAll子域接管模块

:copyright: Copyright (c) 2019, Jing Ling. All rights reserved.
:license: GNU General Public License v3.0, see LICENSE for more details.
"""
import time
import json
from threading import Thread
from queue import Queue

import fire
from tablib import Dataset
from tqdm import tqdm

import config
from config import logger
from common import resolve, utils
from common.module import Module
from common.domain import Domain


def get_fingerprint():
    path = config.data_storage_path.joinpath('fingerprints.json')
    with open(path) as file:
        fingerprints = json.load(file)
    return fingerprints


def get_cname(subdomain):
    resolver = resolve.dns_resolver()
    try:
        answers = resolver.query(subdomain, 'CNAME')
    except Exception as exception:
        logger.log('TRACE', exception.args)
        return None
    for answer in answers:
        return answer.to_text()  # 一个子域只有一个CNAME记录


def get_maindomain(subdomain):
    return Domain(subdomain).registered()


class Takeover(Module):
    """
    OneForAll多线程子域接管风险检查模块

    Example:
        python3 takeover.py --target www.example.com  --format csv run
        python3 takeover.py --target ./subdomains.txt --thread 10 run

    Note:
        参数format可选格式有'txt', 'rst', 'csv', 'tsv', 'json', 'yaml', 'html',
                          'jira', 'xls', 'xlsx', 'dbf', 'latex', 'ods'
        参数dpath为None默认使用OneForAll结果目录

    :param any target:  单个子域或者每行一个子域的文件路径(必需参数)
    :param int thread:  线程数(默认100)
    :param str format:  导出格式(默认csv)
    :param str dpath:   导出目录(默认None)
    """
    def __init__(self, target, thread=100, dpath=None, format='csv'):
        Module.__init__(self)
        self.subdomains = set()
        self.module = 'Check'
        self.source = 'Takeover'
        self.target = target
        self.thread = thread
        self.dpath = dpath
        self.format = format
        self.fingerprints = None
        self.subdomainq = Queue()
        self.cnames = list()
        self.results = Dataset()

    def save(self):
        logger.log('INFOR', '正在保存检查结果')
        if self.format == 'txt':
            data = str(self.results)
        else:
            data = self.results.export(self.format)
        ts = int(time.time())
        fpath = self.dpath.joinpath(f'takeover_{ts}.{self.format}')
        utils.save_data(fpath, data)

    def compare(self, subdomain, cname, responses):
        domain_resp = self.get('http://' + subdomain, check=False)
        cname_resp = self.get('http://' + cname, check=False)
        if domain_resp is None or cname_resp is None:
            return

        for resp in responses:
            if resp in domain_resp.text and resp in cname_resp.text:
                logger.log('ALERT', f'{subdomain}存在子域接管风险')
                self.results.append([subdomain, cname])
                break

    def worker(self, subdomain):
        cname = get_cname(subdomain)
        if cname is None:
            return
        maindomain = get_maindomain(cname)
        for fingerprint in self.fingerprints:
            cnames = fingerprint.get('cname')
            if maindomain not in cnames:
                continue
            responses = fingerprint.get('response')
            self.compare(subdomain, cname, responses)

    def check(self):
        while not self.subdomainq.empty():  # 保证域名队列遍历结束后能退出线程
            subdomain = self.subdomainq.get()  # 从队列中获取域名
            self.worker(subdomain)
            self.subdomainq.task_done()

    def progress(self):
        # 设置进度
        bar = tqdm()
        bar.total = len(self.subdomains)
        bar.desc = 'Progress'
        bar.ncols = True
        while True:
            done = bar.total - self.subdomainq.qsize()
            bar.n = done
            bar.update()
            if done == bar.total:  # 完成队列中所有子域的检查退出
                break
        bar.close()

    def run(self):
        start = time.time()
        logger.log('INFOR', f'开始执行{self.source}模块')
        self.format = utils.check_format(self.format)
        self.dpath = utils.check_dpath(self.dpath)
        self.subdomains = utils.get_domains(self.target)
        if self.subdomains:
            logger.log('INFOR', f'正在检查子域接管风险')
            self.fingerprints = get_fingerprint()
            self.results.headers = ['subdomain', 'cname']
            # 创建待检查的子域队列
            for domain in self.subdomains:
                self.subdomainq.put(domain)
            # 检查线程
            for _ in range(self.thread):
                check_thread = Thread(target=self.check, daemon=True)
                check_thread.start()
            # 进度线程
            progress_thread = Thread(target=self.progress, daemon=True)
            progress_thread.start()

            self.subdomainq.join()
            self.save()
        else:
            logger.log('FATAL', f'获取域名失败')
        end = time.time()
        elapsed = round(end - start, 1)
        logger.log('INFOR', f'{self.source}模块耗时{elapsed}秒'
                            f'发现{len(self.results)}个子域存在接管风险')
        logger.log('DEBUG', f'结束执行{self.source}模块')


if __name__ == '__main__':
    fire.Fire(Takeover)
    # takeover = Takeover('www.example.com')
    # takeover = Takeover('./subdomains.txt')
    # takeover.run()
