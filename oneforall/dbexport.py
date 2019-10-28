#!/usr/bin/python3
# coding=utf-8

"""
OneForAll数据库导出模块

:copyright: Copyright (c) 2019, Jing Ling. All rights reserved.
:license: GNU General Public License v3.0, see LICENSE for more details.
"""

import fire
from common import utils
from common.database import Database


def export(table, db=None, valid=None, dpath=None, format='csv', show=False):
    """
    OneForAll数据库导出模块

    Example:
        python3 dbexport.py --table name --format csv --dir= ./result.csv
        python3 dbexport.py --db result.db --table name --show False

    Note:
        参数port可选值有'small', 'medium', 'large', 'xlarge'，详见config.py配置
        参数format可选格式有'txt', 'rst', 'csv', 'tsv', 'json', 'yaml', 'html',
                          'jira', 'xls', 'xlsx', 'dbf', 'latex', 'ods'
        参数dpath为None默认使用OneForAll结果目录

    :param str table:   要导出的表
    :param str db:      要导出的数据库路径(默认为results/result.sqlite3)
    :param int valid:   导出子域的有效性(默认None)
    :param str format:  导出格式(默认csv)
    :param str dpath:    导出目录(默认None)
    :param bool show:   终端显示导出数据(默认False)
    """
    format = utils.check_format(format)
    dpath = utils.check_dpath(dpath)
    database = Database(db)
    rows = database.export_data(table, valid)  # 意外情况导出全部子域
    if show:
        print(rows.dataset)
    if format == 'txt':
        data = str(rows.dataset)
    else:
        data = rows.export(format)
    database.close()
    fpath = dpath.joinpath(f'{table}_subdomain.{format}')
    utils.save_data(fpath, data)


if __name__ == '__main__':
    fire.Fire(export)
    # save('example_com_last', format='txt')
