#!/usr/bin/python3
# coding=utf-8

"""
OneForAll export from database module

:copyright: Copyright (c) 2019, Jing Ling. All rights reserved.
:license: GNU General Public License v3.0, see LICENSE for more details.
"""

import fire

from common import utils
from common.database import Database
from config.log import logger


def export(table, db=None, alive=False, limit=None, path=None, format='csv', show=False):
    """
    OneForAll export from database module

    Example:
        python3 dbexport.py --table name --format csv --dir= ./result.csv
        python3 dbexport.py --db result.db --table name --show False

    Note:
        --alive  True/False           Only export alive subdomains or not (default False)
        --format rst/csv/tsv/json/yaml/html/jira/xls/xlsx/dbf/latex/ods (result format)
        --path   Result directory (default directory is ./results)

    :param str  table:   Table to be exported
    :param str  db:      Database path to be exported (default ./results/result.sqlite3)
    :param bool alive:   Only export the results of alive subdomains (default False)
    :param str  limit:   Export limit (default None)
    :param str  format:  Result format (default csv)
    :param str  path:    Result directory (default None)
    :param bool show:    Displays the exported data in terminal (default False)
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
    logger.log('INFOR', f'{table}\'s subdomains result: {path}')
    data_dict = rows.as_dict()
    return data_dict


if __name__ == '__main__':
    fire.Fire(export)
    # save('example_com_last', format='txt')
