# coding=utf-8
"""
Module base class
"""

import json
import threading
import time

import requests
from config.log import logger
from config import setting
from common import utils
from common.domain import Domain
from common.database import Database

lock = threading.Lock()


class Module(object):
    def __init__(self):
        self.module = 'Module'
        self.source = 'BaseModule'
        self.cookie = None
        self.header = dict()
        self.proxy = None
        self.delay = setting.request_delay  # 请求睡眠时延
        self.timeout = setting.request_timeout  # 请求超时时间
        self.verify = setting.request_verify  # 请求SSL验证
        self.domain = str()  # 当前进行子域名收集的主域
        self.type = 'A'  # 对主域进行子域收集时利用的DNS记录查询类型(默认利用A记录)
        self.subdomains = set()  # 存放发现的子域
        self.records = dict()  # 存放子域解析记录
        self.results = list()  # 存放模块结果
        self.start = time.time()  # 模块开始执行时间
        self.end = None  # 模块结束执行时间
        self.elapse = None  # 模块执行耗时

    def check(self, *apis):
        """
        Simply check whether the api information configure or not

        :param  apis: apis set
        :return bool: check result
        """
        if not all(apis):
            logger.log('DEBUG', f'{self.source} module is not configured')
            return False
        return True

    def begin(self):
        """
        begin log
        """
        logger.log('DEBUG', f'Start {self.source} module to '
                            f'collect subdomains of {self.domain}')

    def finish(self):
        """
        finish log
        """
        self.end = time.time()
        self.elapse = round(self.end - self.start, 1)
        logger.log('DEBUG', f'Finished {self.source} module to '
                            f'collect {self.domain}\'s subdomains')
        logger.log('INFOR', f'The {self.source} module took {self.elapse} seconds '
                            f'found {len(self.subdomains)} subdomains')
        logger.log('DEBUG', f'{self.source} module found subdomains of {self.domain}\n'
                            f'{self.subdomains}')

    def head(self, url, params=None, check=True, **kwargs):
        """
        Custom head request

        :param str  url: request url
        :param dict params: request parameters
        :param bool check: check response
        :param kwargs: other params
        :return: requests's response object
        """
        try:
            resp = requests.head(url,
                                 params=params,
                                 cookies=self.cookie,
                                 headers=self.header,
                                 proxies=self.proxy,
                                 timeout=self.timeout,
                                 verify=self.verify,
                                 **kwargs)
        except Exception as e:
            logger.log('ERROR', e.args)
            return None
        if not check:
            return resp
        if utils.check_response('HEAD', resp):
            return resp
        return None

    def get(self, url, params=None, check=True, **kwargs):
        """
        Custom get request

        :param str  url: request url
        :param dict params: request parameters
        :param bool check: check response
        :param kwargs: other params
        :return: requests's response object
        """
        try:
            resp = requests.get(url,
                                params=params,
                                cookies=self.cookie,
                                headers=self.header,
                                proxies=self.proxy,
                                timeout=self.timeout,
                                verify=self.verify,
                                **kwargs)
        except Exception as e:
            logger.log('ERROR', e.args)
            return None
        if not check:
            return resp
        if utils.check_response('GET', resp):
            return resp
        return None

    def post(self, url, data=None, check=True, **kwargs):
        """
        Custom post request

        :param str  url: request url
        :param dict data: request data
        :param bool check: check response
        :param kwargs: other params
        :return: requests's response object
        """
        try:
            resp = requests.post(url,
                                 data=data,
                                 cookies=self.cookie,
                                 headers=self.header,
                                 proxies=self.proxy,
                                 timeout=self.timeout,
                                 verify=self.verify,
                                 **kwargs)
        except Exception as e:
            logger.log('ERROR', e.args)
            return None
        if not check:
            return resp
        if utils.check_response('POST', resp):
            return resp
        return None

    def delete(self, url, check=True, **kwargs):
        """
        Custom delete request

        :param str  url: request url
        :param bool check: check response
        :param kwargs: other params
        :return: requests's response object
        """
        try:
            resp = requests.delete(url,
                                   cookies=self.cookie,
                                   headers=self.header,
                                   proxies=self.proxy,
                                   timeout=self.timeout,
                                   verify=self.verify,
                                   **kwargs)
        except Exception as e:
            logger.log('ERROR', e.args)
            return None
        if not check:
            return resp
        if utils.check_response('DELETE', resp):
            return resp
        return None

    def get_header(self):
        """
        Get request header

        :return: header
        """
        # logger.log('DEBUG', f'Get request header')
        if setting.enable_fake_header:
            return utils.gen_fake_header()
        else:
            return self.header

    def get_proxy(self, module):
        """
        Get proxy

        :param str module: module name
        :return: proxy
        """
        if not setting.enable_proxy:
            logger.log('TRACE', f'All modules do not use proxy')
            return self.proxy
        if setting.proxy_all_module:
            logger.log('TRACE', f'{module} module uses proxy')
            return utils.get_random_proxy()
        if module in setting.proxy_partial_module:
            logger.log('TRACE', f'{module} module uses proxy')
            return utils.get_random_proxy()
        else:
            logger.log('TRACE', f'{module} module does not use proxy')
            return self.proxy

    def match_subdomains(self, html, distinct=True, fuzzy=True):
        return utils.match_subdomains(self.domain, html, distinct, fuzzy)

    def save_json(self):
        """
        Save the results of each module as a json file

        :return bool: whether saved successfully
        """
        if not setting.save_module_result:
            return False
        logger.log('TRACE', f'Save the subdomain results found by '
                            f'{self.source} module as a json file')
        path = setting.result_save_dir.joinpath(self.domain, self.module)
        path.mkdir(parents=True, exist_ok=True)
        name = self.source + '.json'
        path = path.joinpath(name)
        with open(path, mode='w', errors='ignore') as file:
            result = {'domain': self.domain,
                      'name': self.module,
                      'source': self.source,
                      'elapse': self.elapse,
                      'find': len(self.subdomains),
                      'subdomains': list(self.subdomains),
                      'records': self.records}
            json.dump(result, file, ensure_ascii=False, indent=4)
        return True

    def gen_record(self, subdomains, record):
        """
        Generate record dictionary
        """
        item = dict()
        item['content'] = record
        for subdomain in subdomains:
            self.records[subdomain] = item

    def gen_result(self, find=0, brute=None, valid=0):
        """
        Generate results
        """
        logger.log('DEBUG', f'Generating final results')
        if not len(self.subdomains):  # 该模块一个子域都没有发现的情况
            logger.log('DEBUG', f'{self.source} module result is empty')
            result = {'id': None,
                      'type': self.type,
                      'alive': None,
                      'request': None,
                      'resolve': None,
                      'new': None,
                      'url': None,
                      'subdomain': None,
                      'port': None,
                      'level': None,
                      'cname': None,
                      'content': None,
                      'public': None,
                      'cdn': None,
                      'status': None,
                      'reason': None,
                      'title': None,
                      'banner': None,
                      'header': None,
                      'response': None,
                      'times': None,
                      'ttl': None,
                      'cidr': None,
                      'asn': None,
                      'org': None,
                      'ip2region': None,
                      'ip2location': None,
                      'resolver': None,
                      'module': self.module,
                      'source': self.source,
                      'elapse': self.elapse,
                      'find': find,
                      'brute': brute,
                      'valid': valid}
            self.results.append(result)
        else:
            for subdomain in self.subdomains:
                url = 'http://' + subdomain
                level = subdomain.count('.') - self.domain.count('.')
                record = self.records.get(subdomain)
                if record is None:
                    record = dict()
                resolve = record.get('resolve')
                request = record.get('request')
                alive = record.get('alive')
                if self.type != 'A':  # 不是利用的DNS记录的A记录查询子域默认都有效
                    resolve = 1
                    request = 1
                    alive = 1
                reason = record.get('reason')
                resolver = record.get('resolver')
                cname = record.get('cname')
                content = record.get('content')
                times = record.get('times')
                ttl = record.get('ttl')
                public = record.get('public')
                cdn = record.get('cdn')
                cidr = record.get('cidr')
                asn = record.get('asn')
                org = record.get('org')
                ip2region = record.get('ip2region')
                ip2location = record.get('ip2location')
                if isinstance(cname, list):
                    cname = ','.join(cname)
                    content = ','.join(content)
                    times = ','.join([str(num) for num in times])
                    ttl = ','.join([str(num) for num in ttl])
                    public = ','.join([str(num) for num in public])
                result = {'id': None,
                          'type': self.type,
                          'alive': alive,
                          'request': request,
                          'resolve': resolve,
                          'new': None,
                          'url': url,
                          'subdomain': subdomain,
                          'port': 80,
                          'level': level,
                          'cname': cname,
                          'content': content,
                          'public': public,
                          'cdn': cdn,
                          'status': None,
                          'reason': reason,
                          'title': None,
                          'banner': None,
                          'header': None,
                          'response': None,
                          'times': times,
                          'ttl': ttl,
                          'cidr': cidr,
                          'asn': asn,
                          'org': org,
                          'ip2region': ip2region,
                          'ip2location': ip2location,
                          'resolver': resolver,
                          'module': self.module,
                          'source': self.source,
                          'elapse': self.elapse,
                          'find': find,
                          'brute': brute,
                          'valid': valid}
                self.results.append(result)

    def save_db(self):
        """
        Save module results into the database
        """
        logger.log('DEBUG', f'Saving results to database')
        lock.acquire()
        db = Database()
        db.create_table(self.domain)
        db.save_db(self.domain, self.results, self.source)
        db.close()
        lock.release()
