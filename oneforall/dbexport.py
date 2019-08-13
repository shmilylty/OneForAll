#!/usr/bin/python3
# coding=utf-8

"""
OneForAll数据库导出模块

:copyright: Copyright (c) 2019, Jing Ling. All rights reserved.
:license: GNU General Public License v3.0, see LICENSE for more details.
"""

import fire
from common.database import Database
from config import logger


def export(table, db=None, valid=None, path=None, format='xlsx', show=False):
    """
    OneForAll数据库导出模块

    Example:
        python3 dbexport.py --table name --format csv --path= ./result.csv
        python3 dbexport.py --db result.db --table name --show False

    Note:
        参数port可选值有'small', 'medium', 'large', 'xlarge'，详见config.py配置
        参数format可选格式有'csv', 'tsv', 'json', 'yaml', 'html', 'xls', 'xlsx',
                         'dbf', 'latex', 'ods'
        参数path为None会根据format参数和域名名称在项目结果目录生成相应文件

    :param str table:   要导出的表
    :param str db:      要导出的数据库路径(默认为results/result.sqlite3)
    :param int valid:   导出子域的有效性(默认None)
    :param str format:  导出格式(默认xlsx)
    :param str path:    导出路径(默认None)
    :param bool show:   终端显示导出数据(默认False)
    """
    formats = ['csv', 'tsv', 'json', 'yaml', 'html',
               'latex', 'xls', 'xlsx', 'dbf', 'ods']
    if format not in formats:
        logger.log('FATAL', f'不支持{format}格式导出')
        return
    database = Database(db)
    if valid is None:
        rows = database.get_data(table)
    elif isinstance(valid, int):
        rows = database.get_subdomain(table, valid)
    else:
        rows = database.get_data(table)  # 意外情况导出全部子域
    if show:
        print(rows.dataset)
    if not path:
        path = 'export.' + format
    logger.log('INFOR', f'正在将数据库中{table}表导出')
    data = rows.export(format)
    try:
        with open(path, 'w') as file:
            file.write(data)
            logger.log('INFOR', '成功完成导出')
            logger.log('INFOR', path)
    except TypeError:
        with open(path, 'wb') as file:
            file.write(data)
            logger.log('INFOR', '成功完成导出')
            logger.log('INFOR', path)
    except Exception as e:
        logger.log('ERROR', e)


if __name__ == '__main__':
    fire.Fire(export)
