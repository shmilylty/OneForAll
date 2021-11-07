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


def export_data(target, db=None, alive=False, limit=None, path=None, fmt='csv', show=False):
    """
    OneForAll export from database module

    Example:
        python3 export.py --target name --fmt csv --dir= ./result.csv
        python3 export.py --target name --tb True --show False
        python3 export.py --db result.db --target name --show False

    Note:
        --fmt csv/json (result format)
        --path   Result directory (default directory is ./results)

    :param str  target:  Table to be exported
    :param str  db:      Database path to be exported (default ./results/result.sqlite3)
    :param bool alive:   Only export the results of alive subdomains (default False)
    :param str  limit:   Export limit (default None)
    :param str  fmt:     Result format (default csv)
    :param str  path:    Result directory (default None)
    :param bool show:    Displays the exported data in terminal (default False)
    """

    database = Database(db)
    domains = utils.get_domains(target)
    datas = list()
    if domains:
        for domain in domains:
            table_name = domain.replace('.', '_')
            rows = database.export_data(table_name, alive, limit)
            if rows is None:
                continue
            data, _, _ = do_export(fmt, path, rows, show, domain, target)
            datas.extend(data)
    database.close()
    if len(domains) > 1:
        utils.export_all(alive, fmt, path, datas)
    return datas


def do_export(fmt, path, rows, show, domain, target):
    fmt = utils.check_format(fmt)
    path = utils.check_path(path, target, fmt)
    if show:
        print(rows.dataset)
    data = rows.export(fmt)
    utils.save_to_file(path, data)
    logger.log('ALERT', f'The subdomain result for {domain}: {path}')
    data = rows.as_dict()
    return data, fmt, path


if __name__ == '__main__':
    fire.Fire(export_data)
