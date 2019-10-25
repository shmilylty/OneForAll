#!/usr/bin/python3
# coding=utf-8

"""
OneForAll是一款功能强大的子域收集工具

:copyright: Copyright (c) 2019, Jing Ling. All rights reserved.
:license: GNU General Public License v3.0, see LICENSE for more details.
"""

import asyncio

import fire
import config
import dbexport
from datetime import datetime
from config import logger
from collect import Collect
from aiobrute import AIOBrute
from common import utils, resolve, request
from common.database import Database
from takeover import Takeover

yellow = '\033[01;33m'
white = '\033[01;37m'
green = '\033[01;32m'
blue = '\033[01;34m'
red = '\033[1;31m'
end = '\033[0m'

version = white + '{' + red + 'v0.0.7#dev' + white + '}'

banner = f"""{yellow}
             ___             _ _ 
 ___ ___ ___|  _|___ ___ ___| | | {version}{green}
| . |   | -_|  _| . |  _| .'| | | {blue}
|___|_|_|___|_| |___|_| |__,|_|_| {white}git.io/fjHT1{end}
"""


class OneForAll(object):
    """
    OneForAll是一款功能强大的子域收集工具

    Version: 0.0.7
    Project: https://git.io/fjHT1

    Example:
        python3 oneforall.py --target example.com run
        python3 oneforall.py --target ./subdomains.txt run
        python3 oneforall.py --target example.com --valid None run
        python3 oneforall.py --target example.com --brute True run
        python3 oneforall.py --target example.com --port medium run
        python3 oneforall.py --target example.com --format csv run
        python3 oneforall.py --target example.com --verify False run
        python3 oneforall.py --target example.com --takeover False run
        python3 oneforall.py --target example.com --show True run

    Note:
        参数valid可选值1，0，None分别表示导出有效，无效，全部子域
        参数verify为True会尝试解析和请求子域并根据结果给子域有效性打上标签
        参数port可选值有'default', 'small', 'medium', 'large', 详见config.py配置
        参数format可选格式有'txt', 'rst', 'csv', 'tsv', 'json', 'yaml', 'html',
                          'jira', 'xls', 'xlsx', 'dbf', 'latex', 'ods'

    :param str target:  单个域名或者每行一个域名的文件路径(必需参数)
    :param bool brute:  使用爆破模块(默认False)
    :param bool verify: 验证子域有效性(默认True)
    :param str port:    请求验证子域的端口范围(默认只探测80端口)
    :param int valid:   导出子域的有效性(默认1)
    :param str format:  导出格式(默认csv)
    :param bool show:   终端显示导出数据(默认False)
    :param str vulnhunter:   是否对接vulnhunter平台(默认空)
    """
    def __init__(self, target, brute=None, verify=None, port='default',
                 valid=1, format='csv', takeover=True, show=False, vulnhunter=''):
        self.target = target
        self.port = port
        self.domains = set()
        self.domain = str()
        self.datas = list()
        self.brute = brute
        self.verify = verify
        self.takeover = takeover
        self.valid = valid
        self.format = format
        self.show = show
        self.vulnhunter = vulnhunter

    def main(self):
        if self.brute is None:
            self.brute = config.enable_brute_module
        if self.verify is None:
            self.verify = config.enable_verify_subdomain
        rename_table = self.domain + '_last'
        collect = Collect(self.domain, export=False)
        collect.run()
        if self.brute:
            # 由于爆破会有大量dns解析请求 并发爆破可能会导致其他任务中的网络请求异常
            brute = AIOBrute(self.domain, export=False)
            brute.run()

        db = Database()
        db.copy_table(self.domain, self.domain+'_ori')
        db.remove_invalid(self.domain)
        db.deduplicate_subdomain(self.domain)
        # 不验证子域的情况
        if not self.verify:
            # 数据库导出
            self.valid = None
            dbexport.export(self.domain, valid=self.valid, format=self.format,
                            show=self.show)
            db.drop_table(rename_table)
            db.rename_table(self.domain, rename_table)
            return
        # 开始验证子域工作
        self.datas = db.get_data(self.domain).as_dict()
        loop = asyncio.get_event_loop()
        asyncio.set_event_loop(loop)

        # 解析域名地址
        task = resolve.bulk_query_a(self.datas)
        self.datas = loop.run_until_complete(task)

        # 保存解析结果
        resolve_table = self.domain + '_res'
        db.drop_table(resolve_table)
        db.create_table(resolve_table)
        db.save_db(resolve_table, self.datas, 'resolve')

        # 请求域名地址
        task = request.bulk_get_request(self.datas, self.port)
        self.datas = loop.run_until_complete(task)
        # 在关闭事件循环前加入一小段延迟让底层连接得到关闭的缓冲时间
        loop.run_until_complete(asyncio.sleep(0.25))

        db.clear_table(self.domain)
        db.save_db(self.domain, self.datas)

        # 数据库导出
        dbexport.export(self.domain, valid=self.valid, format=self.format,
                        show=self.show)
        db.drop_table(rename_table)
        db.rename_table(self.domain, rename_table)
        db.close()
        # 对接web平台
        if self.vulnhunter != '':
            from vulnhunter import save_subdomain
            save_subdomain(self.datas, self.vulnhunter, self.domain)
        # 子域接管检查

        if self.takeover:
            subdomains = set(map(lambda x: x.get('subdomain'), self.datas))
            takeover = Takeover(subdomains)
            takeover.run()

    def run(self):
        print(banner)
        dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f'[*] Starting OneForAll @ {dt}\n')
        logger.log('INFOR', f'开始运行OneForAll')
        self.domains = utils.get_domains(self.target)
        if self.domains:
            for self.domain in self.domains:
                self.main()
        else:
            logger.log('FATAL', f'获取域名失败')
        logger.log('INFOR', f'结束运行OneForAll')


if __name__ == '__main__':
    fire.Fire(OneForAll)
    # OneForAll('example.com').run()
    # OneForAll('./domains.txt').run()
