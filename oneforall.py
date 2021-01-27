#!/usr/bin/python3
# coding=utf-8

"""
OneForAll is a powerful subdomain integration tool

:copyright: Copyright (c) 2019, Jing Ling. All rights reserved.
:license: GNU General Public License v3.0, see LICENSE for more details.
"""

import fire
from datetime import datetime


import export
from brute import Brute
from common import utils, resolve, request
from modules.collect import Collect
from modules.srv import BruteSRV
from modules.finder import Finder
from modules.altdns import Altdns
from modules.enrich import Enrich
from modules import wildcard
from config import settings
from config.log import logger
from takeover import Takeover

yellow = '\033[01;33m'
white = '\033[01;37m'
green = '\033[01;32m'
blue = '\033[01;34m'
red = '\033[1;31m'
end = '\033[0m'

version = 'v0.4.3'
message = white + '{' + red + version + ' #dev' + white + '}'

oneforall_banner = f"""
OneForAll is a powerful subdomain integration tool{yellow}
             ___             _ _ 
 ___ ___ ___|  _|___ ___ ___| | | {message}{green}
| . |   | -_|  _| . |  _| .'| | | {blue}
|___|_|_|___|_| |___|_| |__,|_|_| {white}git.io/fjHT1

{red}OneForAll is under development, please update before each use!{end}
"""


class OneForAll(object):
    """
    OneForAll help summary page

    OneForAll is a powerful subdomain integration tool

    Example:
        python3 oneforall.py version
        python3 oneforall.py check
        python3 oneforall.py --target example.com run
        python3 oneforall.py --targets ./domains.txt run
        python3 oneforall.py --target example.com --alive False run
        python3 oneforall.py --target example.com --brute False run
        python3 oneforall.py --target example.com --port medium run
        python3 oneforall.py --target example.com --fmt csv run
        python3 oneforall.py --target example.com --dns False run
        python3 oneforall.py --target example.com --req False run
        python3 oneforall.py --target example.com --takeover False run
        python3 oneforall.py --target example.com --show True run

    Note:
        --port   small/medium/large  See details in ./config/setting.py(default small)
        --fmt csv/json (result format)
        --path   Result path (default None, automatically generated)

    :param str  target:     One domain (target or targets must be provided)
    :param str  targets:    File path of one domain per line
    :param bool brute:      Use brute module (default True)
    :param bool dns:        Use DNS resolution (default True)
    :param bool req:        HTTP request subdomains (default True)
    :param str  port:       The port range to request (default small port is 80,443)
    :param bool alive:      Only export alive subdomains (default False)
    :param str  fmt:        Result format (default csv)
    :param str  path:       Result path (default None, automatically generated)
    :param bool takeover:   Scan subdomain takeover (default False)
    """
    def __init__(self, target=None, targets=None, brute=None, dns=None, req=None,
                 port=None, alive=None, fmt=None, path=None, takeover=None):
        self.target = target
        self.targets = targets
        self.brute = brute
        self.dns = dns
        self.req = req
        self.port = port
        self.alive = alive
        self.fmt = fmt
        self.path = path
        self.takeover = takeover
        self.domain = str()  # The domain currently being collected
        self.domains = set()  # All domains that are to be collected
        self.data = list()  # The subdomain results of the current domain
        self.datas = list()  # All subdomain results of the domain
        self.in_china = None
        self.access_internet = False
        self.enable_wildcard = False

    def config_param(self):
        """
        Config parameter
        """
        if self.brute is None:
            self.brute = bool(settings.enable_brute_module)
        if self.dns is None:
            self.dns = bool(settings.enable_dns_resolve)
        if self.req is None:
            self.req = bool(settings.enable_http_request)
        if self.takeover is None:
            self.takeover = bool(settings.enable_takeover_check)
        if self.port is None:
            self.port = settings.http_request_port
        if self.alive is None:
            self.alive = bool(settings.result_export_alive)
        if self.fmt is None:
            self.fmt = settings.result_save_format
        if self.path is None:
            self.path = settings.result_save_path

    def check_param(self):
        """
        Check parameter
        """
        if self.target is None and self.targets is None:
            logger.log('FATAL', 'You must provide either target or targets parameter')
            exit(1)

    def export_data(self):
        """
        Export data from the database

        :return: exported data
        :rtype: list
        """
        return export.export_data(self.domain, alive=self.alive, fmt=self.fmt, path=self.path)

    def main(self):
        """
        OneForAll main process

        :return: subdomain results
        :rtype: list
        """
        utils.init_table(self.domain)

        if not self.access_internet:
            logger.log('ALERT', 'Because it cannot access the Internet, '
                                'OneForAll will not execute the subdomain collection module!')
        if self.access_internet:
            self.enable_wildcard = wildcard.detect_wildcard(self.domain)

            collect = Collect(self.domain)
            collect.run()

        srv = BruteSRV(self.domain)
        srv.run()

        if self.brute:
            # Due to there will be a large number of dns resolution requests,
            # may cause other network tasks to be error
            brute = Brute(self.domain, word=True, export=False)
            brute.enable_wildcard = self.enable_wildcard
            brute.in_china = self.in_china
            brute.quite = True
            brute.run()

        utils.deal_data(self.domain)
        # Export results without resolve
        if not self.dns:
            self.data = self.export_data()
            self.datas.extend(self.data)
            return self.data

        self.data = utils.get_data(self.domain)

        # Resolve subdomains
        utils.clear_data(self.domain)
        self.data = resolve.run_resolve(self.domain, self.data)
        # Save resolve results
        resolve.save_db(self.domain, self.data)

        # Export results without HTTP request
        if not self.req:
            self.data = self.export_data()
            self.datas.extend(self.data)
            return self.data

        if self.enable_wildcard:
            # deal wildcard
            self.data = wildcard.deal_wildcard(self.data)

        # HTTP request
        utils.clear_data(self.domain)
        request.run_request(self.domain, self.data, self.port)

        # Finder module
        if settings.enable_finder_module:
            finder = Finder()
            finder.run(self.domain, self.data, self.port)

        # altdns module
        if settings.enable_altdns_module:
            altdns = Altdns(self.domain)
            altdns.run(self.data, self.port)

        # Information enrichment module
        if settings.enable_enrich_module:
            enrich = Enrich(self.domain)
            enrich.run()

        self.data = self.export_data()
        self.datas.extend(self.data)

        # Scan subdomain takeover
        if self.takeover:
            subdomains = utils.get_subdomains(self.data)
            takeover = Takeover(targets=subdomains)
            takeover.run()
        return self.data

    def run(self):
        """
        OneForAll running entrance

        :return: All subdomain results
        :rtype: list
        """
        print(oneforall_banner)
        dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f'[*] Starting OneForAll @ {dt}\n')
        logger.log('DEBUG', 'Python ' + utils.python_version())
        logger.log('DEBUG', 'OneForAll ' + version)
        utils.check_dep()
        self.access_internet, self.in_china = utils.get_net_env()
        if self.access_internet and settings.enable_check_version:
            utils.check_version(version)
        logger.log('INFOR', 'Start running OneForAll')
        self.config_param()
        self.check_param()
        self.domains = utils.get_domains(self.target, self.targets)
        count = len(self.domains)
        logger.log('INFOR', f'Got {count} domains')
        if not count:
            logger.log('FATAL', 'Failed to obtain domain')
            exit(1)
        for domain in self.domains:
            self.domain = utils.get_main_domain(domain)
            self.main()
        if count > 1:
            utils.export_all(self.alive, self.fmt, self.path, self.datas)
        logger.log('INFOR', 'Finished OneForAll')

    @staticmethod
    def version():
        """
        Print version information and exit
        """
        print(oneforall_banner)
        exit(0)

    @staticmethod
    def check():
        """
        Check if there is a new version and exit
        """
        utils.check_version(version)
        exit(0)


if __name__ == '__main__':
    fire.Fire(OneForAll)
