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
from config.log import logger


def export(table, db=None, alive=False, limit=None, path=None, format='csv', show=False):
    """
    OneForAll数据库导出模块

    Example:
        python3 dbexport.py --table name --format csv --dir= ./result.csv
        python3 dbexport.py --db result.db --table name --show False

    Note:
        参数alive可选值True，False分别表示导出存活，全部子域结果
        参数format可选格式有'txt', 'rst', 'csv', 'tsv', 'json', 'yaml', 'html',
                          'jira', 'xls', 'xlsx', 'dbf', 'latex', 'ods'
        参数path默认None使用OneForAll结果目录自动生成路径

    :param str table:   要导出的表
    :param str db:      要导出的数据库路径(默认为results/result.sqlite3)
    :param bool alive:  只导出存活的子域结果(默认False)
    :param str limit:   导出限制条件(默认None)
    :param str format:  导出文件格式(默认csv)
    :param str path:    导出文件路径(默认None)
    :param bool show:   终端显示导出数据(默认False)
    """

    database = Database(db)
    rows = database.export_data(table, alive, limit)
    format = utils.check_format(format, len(rows))
    path = utils.check_path(path, table, format)
    if show:
        print(rows.dataset)
    data = rows.export(format)
    database.close()
    utils.save_data(path, data)
    logger.log('INFOR', f'{table}主域的子域结果 {path}')
    data_dict = rows.as_dict()
    return data_dict


if __name__ == '__main__':
    fire.Fire(export)
    # save('example_com_last', format='txt')
