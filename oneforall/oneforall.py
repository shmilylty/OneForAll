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
from  common.database import Database


banner = """\033[01;33m
             ___             _ _ 
 ___ ___ ___|  _|___ ___ ___| | | \033[01;37m{\033[1;31mv0.0.3#dev\033[01;37m}\033[01;32m
| . |   | -_|  _| . |  _| .'| | | \033[01;34m
|___|_|_|___|_| |___|_| |__,|_|_| \033[0m\033[4;37mgit.io/fjHT1\033[0m\n
        """


class OneForAll(object):
    """
    OneForAll是一款功能强大的子域收集工具

    Version: 0.0.3
    Project: https://github.com/shmilylty/OneForAll/

    Example:
        python oneforall.py --target example.com run
        python oneforall.py --target example.com --brute True --port medium --valid 1 run
        python oneforall.py --target ./domains.txt --format csv --path= ./result.csv  --output True run

    Note:
        参数valid可选值有1，0，None，分别表示导出有效，无效，全部子域
        参数port可选值有'small', 'medium', 'large', 'xlarge'，详见config.py配置
        参数format可选格式有'csv', 'tsv', 'json', 'yaml', 'html', 'xls', 'xlsx', 'dbf', 'latex', 'ods'
        参数path为None会根据format参数和域名名称在项目结果目录生成相应文件

    :param str target:  单个域名或者每行一个域名的文件路径
    :param bool brute:  是否使用爆破模块(默认禁用)
    :param str port:    HTTP请求验证的端口范围(默认medium)
    :param int valid:   导出子域的有效性(默认1)
    :param str format:  导出格式(默认xlsx)
    :param str path:    导出路径(默认None)
    :param bool output: 是否将导出数据输出到终端(默认False)
    """
    def __init__(self, target, brute=False, port='medium', valid=1, path=None,
                 format='xlsx', output=False):
        self.target = target
        self.port = port
        self.domains = set()
        self.domain = ''
        self.datas = list()
        self.brute = brute or config.enable_brute_module
        self.valid = valid
        self.path = path
        self.format = format
        self.output = output

    def run(self):
        print(banner)
        dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f'[*] Starting OneForAll @ {dt}\n')
        logger.log('INFOR', f'开始运行OneForAll')
        self.domains = utils.get_domains(self.target)
        if self.domains:
            for self.domain in self.domains:
                collect = Collect(self.domain, export=False)
                collect.run()
                if self.brute:
                    # 由于爆破会有大量dns解析请求 并发常常会导致其他任务中的网络请求超时
                    brute = AIOBrute(self.domain)
                    brute.run()
                db = Database()
                self.datas = db.get_data(self.domain).as_dict()
                loop = asyncio.get_event_loop()
                asyncio.set_event_loop(loop)
                self.datas = loop.run_until_complete(resolve.bulk_query_a(self.datas))
                self.datas = loop.run_until_complete(request.bulk_get_request(self.datas, self.port))
                # 在关闭事件循环前加入一小段延迟让底层连接得到关闭的缓冲时间
                loop.run_until_complete(asyncio.sleep(0.25))
                loop.close()
                db.clear_table(self.domain)
                db.save_db(self.domain, self.datas)
                # 数据库导出
                if not self.path:
                    self.path = config.result_save_path.joinpath(f'{self.domain}.{self.format}')
                dbexport.export(self.domain, db.conn, self.valid, self.path, self.format, self.output)
        else:
            logger.log('FATAL', f'获取域名失败')
        logger.log('INFOR', f'结束运行OneForAll')


if __name__ == '__main__':
    fire.Fire(OneForAll)
    # OneForAll('example.com').run()
