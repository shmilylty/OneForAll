#!/usr/bin/python3
# coding=utf-8

"""
OneForAll is a powerful subdomain collection tool

:copyright: Copyright (c) 2019, Jing Ling. All rights reserved.
:license: GNU General Public License v3.0, see LICENSE for more details.
"""

from datetime import datetime

import fire

import dbexport
from brute import Brute
from common import utils, resolve, request
from common.database import Database
from modules.collect import Collect
from config import setting
from config.log import logger
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
OneForAll is a powerful subdomain collection tool{yellow}
             ___             _ _ 
 ___ ___ ___|  _|___ ___ ___| | | {message}{green}
| . |   | -_|  _| . |  _| .'| | | {blue}
|___|_|_|___|_| |___|_| |__,|_|_| {white}git.io/fjHT1

{red}OneForAll is under development, please update before each use!{end}
"""


class OneForAll(object):
    """
    OneForAll help summary page

    OneForAll is a powerful subdomain collection tool

    Example:
        python3 oneforall.py version
        python3 oneforall.py --target example.com run
        python3 oneforall.py --target ./domains.txt run
        python3 oneforall.py --target example.com --alive False run
        python3 oneforall.py --target example.com --brute True run
        python3 oneforall.py --target example.com --port medium run
        python3 oneforall.py --target example.com --format csv run
        python3 oneforall.py --target example.com --dns False run
        python3 oneforall.py --target example.com --req False run
        python3 oneforall.py --target example.com --takeover False run
        python3 oneforall.py --target example.com --show True run

    Note:
        --alive  True/False           Only export alive subdomains or not (default False)
        --port   default/small/large  See details in ./config/setting.py(default port 80)
        --format rst/csv/tsv/json/yaml/html/jira/xls/xlsx/dbf/latex/ods (result format)
        --path   Result directory (default directory is ./results)

    :param str target:     One domain or File path of one domain per line (required)
    :param bool brute:     Use brute module (default False)
    :param bool dns:       Use DNS resolution (default True)
    :param bool req:       HTTP request subdomains (default True)
    :param str port:       The port range request to the subdomains (default port 80)
    :param bool alive:     Only export alive subdomains (default False)
    :param str format:     Result format (default csv)
    :param str path:       Result directory (default None)
    :param bool takeover:  Scan subdomain takeover (default False)
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
        self.domain = str()  # The domain currently being collected
        self.domains = set()  # All domains that are to be collected
        self.data = list()  # The subdomain results of the current domain
        self.datas = list()  # All subdomain results of the domain
        self.old_table = str()  # The table name of the last result
        self.new_table = str()  # The table name of the current result
        self.origin_table = str()  # The table name of the origin result
        self.resolve_table = str()  # The table name of the resolute result

    def config(self):
        """
        Configuration parameter
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
        Export data from the database and do some follow-up processing

        :param table: table name
        :return: export data
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
        Process the data when the collection task is completed
        """
        db = Database()
        db.deal_table(self.domain, self.origin_table)
        db.close()

    def mark(self):
        """
        Mark the new discovered subdomain

        :return: marked data
        :rtype: list
        """
        db = Database()
        old_data = list()
        now_data = db.get_data(self.domain).as_dict()
        # Database pre-processing when it is not the first time to collect this subdomain
        if db.exist_table(self.new_table):
            # If there is the last collection result table, delete it first
            db.drop_table(self.old_table)
            # Rename the new table to the old table
            db.rename_table(self.new_table, self.old_table)
            old_data = db.get_data(self.old_table).as_dict()
            db.close()
        marked_data = utils.mark_subdomain(old_data, now_data)
        return marked_data

    def main(self):
        """
        OneForAll main process

        :return: subdomain results
        :rtype: list
        """
        self.old_table = self.domain + '_old_result'
        self.new_table = self.domain + '_now_result'
        self.origin_table = self.domain + '_origin_result'
        self.resolve_table = self.domain + '_resolve_result'

        collect = Collect(self.domain, export=False)
        collect.run()
        if self.brute:
            # Due to there will be a large number of dns resolution requests,
            # may cause other network tasks to be error
            brute = Brute(self.domain, word=True, export=False)
            brute.check_env = False
            brute.quite = True
            brute.run()

        # Database processing
        self.deal_db()
        # Mark the new discovered subdomain
        self.data = self.mark()

        # Export results without resolve
        if not self.dns:
            return self.export(self.domain)

        # Resolve subdomains
        self.data = resolve.run_resolve(self.domain, self.data)
        # Save resolve results
        resolve.save_data(self.resolve_table, self.data)

        # Export results without HTTP request
        if not self.req:
            return self.export(self.resolve_table)

        # HTTP request
        self.data = request.run_request(self.domain, self.data, self.port)
        # Save HTTP request result
        request.save_data(self.domain, self.data)

        # Add the final result list to the total data list
        self.datas.extend(self.data)

        # Export
        self.export(self.domain)

        # Scan subdomain takeover
        if self.takeover:
            subdomains = utils.get_subdomains(self.data)
            takeover = Takeover(subdomains)
            takeover.run()
        return self.data

    def run(self):
        """
        OneForAll running entrance

        :return: All subdomain results
        :rtype: list
        """
        print(banner)
        dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f'[*] Starting OneForAll @ {dt}\n')
        utils.check_env()
        logger.log('DEBUG', 'Python ' + utils.python_version())
        logger.log('DEBUG', 'OneForAll ' + version)
        logger.log('INFOR', f'Start running OneForAll')
        self.config()
        self.domains = utils.get_domains(self.target)
        if self.domains:
            for self.domain in self.domains:
                self.main()
            utils.export_all(self.alive, self.format, self.path, self.datas)
        else:
            logger.log('FATAL', f'Failed to obtain domain')
        logger.log('INFOR', f'Finished OneForAll')

    @staticmethod
    def version():
        print(banner)
        exit(0)


if __name__ == '__main__':
    fire.Fire(OneForAll)
    # OneForAll('example.com').run()
    # OneForAll('./domains.txt').run()
