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


def export(target, type='target', db=None, alive=False, limit=None, path=None, format='csv', show=False):
    """
    OneForAll export from database module

    Example:
        python3 dbexport.py --target name --format csv --dir= ./result.csv
        python3 dbexport.py --db result.db --target name --show False
        python3 dbexport.py --target table_name --tb True --show False

    Note:
        --alive  True/False           Only export alive subdomains or not (default False)
        --format rst/csv/tsv/json/yaml/html/jira/xls/xlsx/dbf/latex/ods (result format)
        --path   Result directory (default directory is ./results)

    :param str  target:  Table to be exported
    :param str  type:    Type of target
    :param str  db:      Database path to be exported (default ./results/result.sqlite3)
    :param bool alive:   Only export the results of alive subdomains (default False)
    :param str  limit:   Export limit (default None)
    :param str  format:  Result format (default csv)
    :param str  path:    Result directory (default None)
    :param bool show:    Displays the exported data in terminal (default False)
    """

    if type == 'target':
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
                path = utils.check_path(path, target, format)
                if show:
                    print(rows.dataset)
                data = rows.export(format)
                utils.save_data(path, data)
                logger.log('ALERT', f'The subdomain result for {table_name}: {path}')
                data = rows.as_dict()
                datas.extend(data)
        database.close()
        if len(domains) > 1:
            utils.export_all(alive, format, path, datas)
    elif type == 'table':
        database = Database(db)
        rows = database.export_data(target, alive, limit)
        format = utils.check_format(format, len(rows))
        path = utils.check_path(path, target, format)
        if show:
            print(rows.dataset)
        data = rows.export(format)
        database.close()
        utils.save_data(path, data)
        logger.log('ALERT', f'The subdomain result for {target}: {path}')
        data_dict = rows.as_dict()
        return data_dict


if __name__ == '__main__':
    fire.Fire(export)
    # export('example.com')
