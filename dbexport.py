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


def domain_to_table(table):
    return table.replace('.', '_') + "_now_result"


def export(target, db=None, alive=False, limit=None, path=None, format='csv', show=False):
    """
    OneForAll export from database module

    Example:
        python3 dbexport.py --target name --format csv --dir= ./result.csv
        python3 dbexport.py --db result.db --target name --show False

    Note:
        --alive  True/False           Only export alive subdomains or not (default False)
        --format rst/csv/tsv/json/yaml/html/jira/xls/xlsx/dbf/latex/ods (result format)
        --path   Result directory (default directory is ./results)

    :param str  target:   Table to be exported
    :param str  db:      Database path to be exported (default ./results/result.sqlite3)
    :param bool alive:   Only export the results of alive subdomains (default False)
    :param str  limit:   Export limit (default None)
    :param str  format:  Result format (default csv)
    :param str  path:    Result directory (default None)
    :param bool show:    Displays the exported data in terminal (default False)
    """

    database = Database(db)
    domains = utils.get_domains(target)
    datas = []
    if domains:
        for domain in domains:
            table_name = domain_to_table(domain)
            rows = database.export_data(table_name, alive, limit)
            if rows is None:
                continue
            format = utils.check_format(format, len(rows))
            if show:
                print(rows.dataset)
            data = rows.as_dict()
            datas.extend(data)
    database.close()
    if datas:
        utils.export_all(alive, format, path, datas)


if __name__ == '__main__':
    # fire.Fire(export)
    export('example.com')
