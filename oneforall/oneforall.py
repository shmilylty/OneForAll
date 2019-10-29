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
    """
    def __init__(self, target, brute=None, verify=None, port='default',
                 valid=1, format='csv', takeover=True, show=False):
        self.target = target
        self.port = port
        self.domains = set()
        self.domain = str()
        self.data = list()
        self.brute = brute
        self.verify = verify
        self.takeover = takeover
        self.valid = valid
        self.format = format
        self.show = show

    def main(self):
        if self.brute is None:
            self.brute = config.enable_brute_module
        if self.verify is None:
            self.verify = config.enable_verify_subdomain
        old_table = self.domain + '_last'
        new_table = self.domain + '_now'
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

        old_data = []
        # 非第一次收集子域的情况时数据库预处理
        if db.exist_table(new_table):
            db.drop_table(old_table)  # 如果存在上次收集结果表就先删除
            db.rename_table(new_table, old_table)  # 新表重命名为旧表
            old_data = db.get_data(old_table).as_dict()

        # 不验证子域的情况
        if not self.verify:
            # 数据库导出
            self.valid = None
            dbexport.export(self.domain, valid=self.valid,
                            format=self.format, show=self.show)
            db.drop_table(new_table)
            db.rename_table(self.domain, new_table)
            return
        # 开始验证子域工作
        self.data = db.get_data(self.domain).as_dict()

        # 标记新发现子域
        self.data = utils.mark_subdomain(old_data, self.data)

        loop = asyncio.get_event_loop()
        asyncio.set_event_loop(loop)

        # 解析域名地址
        task = resolve.bulk_query_a(self.data)
        self.data = loop.run_until_complete(task)

        # 保存解析结果
        resolve_table = self.domain + '_res'
        db.drop_table(resolve_table)
        db.create_table(resolve_table)
        db.save_db(resolve_table, self.data, 'resolve')

        # 请求域名地址
        task = request.bulk_get_request(self.data, self.port)
        self.data = loop.run_until_complete(task)
        # 在关闭事件循环前加入一小段延迟让底层连接得到关闭的缓冲时间
        loop.run_until_complete(asyncio.sleep(0.25))

        db.clear_table(self.domain)
        db.save_db(self.domain, self.data)

        # 数据库导出
        dbexport.export(self.domain, valid=self.valid,
                        format=self.format, show=self.show)
        db.drop_table(new_table)
        db.rename_table(self.domain, new_table)
        db.close()
        # 子域接管检查

        if self.takeover:
            subdomains = set(map(lambda x: x.get('subdomain'), self.data))
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
