#!/usr/bin/python3
# coding=utf-8

"""
OneForAll数据库导出模块

:copyright: Copyright (c) 2019, Jing Ling. All rights reserved.
:license: GNU General Public License v3.0, see LICENSE for more details.
"""

from pathlib import Path
import fire
import config
from common.database import Database
from config import logger


def export(table, db=None, valid=None, dpath=None, format='xls', show=False):
    """
    OneForAll数据库导出模块

    Example:
        python3 dbexport.py --table name --format csv --dir= ./result.csv
        python3 dbexport.py --db result.db --table name --show False

    Note:
        参数port可选值有'small', 'medium', 'large', 'xlarge'，详见config.py配置
        参数format可选格式有'txt', 'rst', 'csv', 'tsv', 'json', 'yaml', 'html',
                          'jira', 'xls', 'xlsx', 'dbf', 'latex', 'ods'
        参数dir为None默认使用OneForAll结果目录

    :param str table:   要导出的表
    :param str db:      要导出的数据库路径(默认为results/result.sqlite3)
    :param int valid:   导出子域的有效性(默认None)
    :param str format:  导出格式(默认xls)
    :param str dpath:    导出目录(默认None)
    :param bool show:   终端显示导出数据(默认False)
    """
    formats = ['txt', 'rst', 'csv', 'tsv', 'json', 'yaml', 'html',
               'jira', 'xls', 'xlsx', 'dbf', 'latex', 'ods']
    if format not in formats:
        logger.log('FATAL', f'不支持{format}格式导出')
        return
    if dpath is None:
        dpath = config.result_save_path
    if isinstance(dpath, str):
        dpath = Path(dpath)
    if not dpath.is_dir():
        logger.log('FATAL', f'{dpath}不是目录')
        return
    if not dpath.exists():
        logger.log('ALERT', f'不存在{dpath}将会新建此目录')
        dpath.mkdir(parents=True, exist_ok=True)

    database = Database(db)
    if valid is None:
        rows = database.get_data(table)
    elif isinstance(valid, int):
        rows = database.get_subdomain(table, valid)
    else:
        rows = database.get_data(table)  # 意外情况导出全部子域
    if show:
        print(rows.dataset)
    if format == 'txt':
        data = str(rows.dataset)
    else:
        data = rows.export(format)
    database.close()
    fpath = dpath.joinpath(f'{table}.{format}')
    try:
        with open(fpath, 'w', encoding="utf-8", newline='') as file:
            file.write(data)
            logger.log('INFOR', '成功完成导出')
            logger.log('INFOR', fpath)
    except TypeError:
        with open(fpath, 'wb') as file:
            file.write(data)
            logger.log('INFOR', '成功完成导出')
            logger.log('INFOR', fpath)
    except Exception as e:
        logger.log('ERROR', e)


if __name__ == '__main__':
    fire.Fire(export)
    # export('example_com_last', format='txt')
