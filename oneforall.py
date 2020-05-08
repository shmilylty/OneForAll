#!/usr/bin/python3
# coding=utf-8

"""
OneForAll是一款功能强大的子域收集工具

:copyright: Copyright (c) 2019, Jing Ling. All rights reserved.
:license: GNU General Public License v3.0, see LICENSE for more details.
"""

import fire

import dbexport
from datetime import datetime
from config.log import logger
from config import setting
from collect import Collect
from brute import Brute
from common import utils, resolve, request
from common.database import Database
from takeover import Takeover

yellow = '\033[01;33m'
white = '\033[01;37m'
green = '\033[01;32m'
blue = '\033[01;34m'
red = '\033[1;31m'
end = '\033[0m'

version = 'v0.2.0#dev'
message = white + '{' + red + version + white + '}'

banner = f"""
OneForAll是一款功能强大的子域收集工具{yellow}
             ___             _ _ 
 ___ ___ ___|  _|___ ___ ___| | | {message}{green}
| . |   | -_|  _| . |  _| .'| | | {blue}
|___|_|_|___|_| |___|_| |__,|_|_| {white}git.io/fjHT1

{red}OneForAll处于开发中，会进行版本快速迭代，请每次在使用前进行更新！{end}
"""


class OneForAll(object):
    """
    OneForAll帮助信息

    OneForAll是一款功能强大的子域收集工具

    Example:
        python3 oneforall.py version
        python3 oneforall.py --target example.com run
        python3 oneforall.py --target ./domains.txt run
        python3 oneforall.py --target example.com --alive None run
        python3 oneforall.py --target example.com --brute True run
        python3 oneforall.py --target example.com --port medium run
        python3 oneforall.py --target example.com --format csv run
        python3 oneforall.py --target example.com --dns False run
        python3 oneforall.py --target example.com --req False run
        python3 oneforall.py --target example.com --takeover False run
        python3 oneforall.py --target example.com --show True run

    Note:
        参数alive可选值True，False分别表示导出存活，全部子域结果
        参数port可选值有'default', 'small', 'large', 详见setting.py配置
        参数format可选格式有'rst', 'csv', 'tsv', 'json', 'yaml', 'html',
                          'jira', 'xls', 'xlsx', 'dbf', 'latex', 'ods'
        参数path默认None使用OneForAll结果目录自动生成路径

    :param str target:     单个域名或者每行一个域名的文件路径(必需参数)
    :param bool brute:     使用爆破模块(默认False)
    :param bool dns:       DNS解析子域(默认True)
    :param bool req:       HTTP请求子域(默认True)
    :param str port:       请求验证子域的端口范围(默认探测80端口)
    :param bool alive:     只导出存活的子域结果(默认False)
    :param str format:     结果保存格式(默认csv)
    :param str path:       结果保存路径(默认None)
    :param bool takeover:  检查子域接管(默认False)
    """
    def __init__(self, target, brute=None, dns=None, req=None, port=None,
                 alive=None, format=None, path=None, takeover=None):
        self.target = target
        self.brute = brute
        self.dns = dns
        self.req = req
        self.port = port
        self.alive = alive
        self.format = format
        self.path = path
        self.takeover = takeover
        self.domain = str()  # 当前正在进行收集的主域
        self.domains = set()  # 所有即将进行收集的主机
        self.data = list()  # 存放当前主域的子域结果
        self.datas = list()  # 存放所有主域的子域结果
        self.old_table = str()  # 存放上一次结果的表名
        self.new_table = str()  # 存放现在结果的表名
        self.origin_table = str()  # 存放最初收集结果的表名
        self.resolve_table = str()  # 存放解析后的结果表名

    def config(self):
        """
        配置参数
        """
        if self.brute is None:
            self.brute = bool(setting.enable_brute_module)
        if self.dns is None:
            self.dns = bool(setting.enable_dns_resolve)
        if self.req is None:
            self.req = bool(setting.enable_http_request)
        if self.takeover is None:
            self.takeover = bool(setting.enable_takeover_check)
        if self.port is None:
            self.port = setting.http_request_port
        if self.alive is None:
            self.alive = bool(setting.result_export_alive)
        if self.format is None:
            self.format = setting.result_save_format
        if self.path is None:
            self.path = setting.result_save_path

    def export(self, table):
        """
        从数据库中导出数据并做一些后续数据库善后处理

        :param table: 要导出的表名
        :return: 导出的数据
        :rtype: list
        """
        db = Database()
        data = dbexport.export(table, alive=self.alive, format=self.format)
        db.drop_table(self.new_table)
        db.rename_table(self.domain, self.new_table)
        db.close()
        return data

    def deal_db(self):
        """
        收集任务完成时对数据库进行处理
        """
        db = Database()
        db.deal_table(self.domain, self.origin_table)
        db.close()

    def mark(self):
        """
        标记新发现子域

        :return: 标记后的的子域数据
        :rtype: list
        """
        db = Database()
        old_data = list()
        now_data = db.get_data(self.domain).as_dict()
        # 非第一次收集子域的情况时数据库预处理
        if db.exist_table(self.new_table):
            db.drop_table(self.old_table)  # 如果存在上次收集结果表就先删除
            db.rename_table(self.new_table, self.old_table)  # 新表重命名为旧表
            old_data = db.get_data(self.old_table).as_dict()
            db.close()
        marked_data = utils.mark_subdomain(old_data, now_data)
        return marked_data

    def main(self):
        """
        OneForAll实际运行主流程

        :return: 子域结果
        :rtype: list
        """
        self.old_table = self.domain + '_old_result'
        self.new_table = self.domain + '_now_result'
        self.origin_table = self.domain + '_origin_result'
        self.resolve_table = self.domain + '_resolve_result'

        collect = Collect(self.domain, export=False)
        collect.run()
        if self.brute:
            # 由于爆破会有大量dns解析请求 并发爆破可能会导致其他任务中的网络请求异常
            brute = Brute(self.domain, word=True, export=False)
            brute.check_env = False
            brute.run()

        # 有关数据库处理
        self.deal_db()
        # 标记新发现子域
        self.data = self.mark()

        # 不解析子域直接导出结果
        if not self.dns:
            return self.export(self.domain)

        # 解析子域
        self.data = resolve.run_resolve(self.domain, self.data)
        # 保存解析结果
        resolve.save_data(self.resolve_table, self.data)

        # 不请求子域直接导出结果
        if not self.req:
            return self.export(self.resolve_table)

        # 请求子域
        self.data = request.run_request(self.domain, self.data, self.port)
        # 保存请求结果
        request.save_data(self.domain, self.data)

        # 将最终结果列表添加到总的数据列表中
        self.datas.extend(self.data)

        # 数据库导出
        self.export(self.domain)

        # 子域接管检查
        if self.takeover:
            subdomains = utils.get_subdomains(self.data)
            takeover = Takeover(subdomains)
            takeover.run()
        return self.data

    def run(self):
        """
        OneForAll运行入口

        :return: 总的子域结果
        :rtype: list
        """
        print(banner)
        dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f'[*] Starting OneForAll @ {dt}\n')
        utils.check_env()
        logger.log('DEBUG', 'Python ' + utils.python_version())
        logger.log('DEBUG', 'OneForAll ' + version)
        logger.log('INFOR', f'开始运行OneForAll')
        self.config()
        self.domains = utils.get_domains(self.target)
        if self.domains:
            for self.domain in self.domains:
                self.main()
            utils.export_all(self.format, self.path, self.datas)
        else:
            logger.log('FATAL', f'获取域名失败')
        logger.log('INFOR', f'结束运行OneForAll')

    @staticmethod
    def version():
        print(banner)
        exit(0)


if __name__ == '__main__':
    fire.Fire(OneForAll)
    # OneForAll('example.com').run()
    # OneForAll('./domains.txt').run()
