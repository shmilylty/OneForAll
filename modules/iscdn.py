import json
import ipaddress

from config import settings
from common import utils
from common.database import Database
from config.log import logger

data_dir = settings.data_storage_dir

# from https://github.com/al0ne/Vxscan/blob/master/lib/iscdn.py
cdn_ip_cidr = utils.load_json(data_dir.joinpath('cdn_ip_cidr.json'))
cdn_asn_list = utils.load_json(data_dir.joinpath('cdn_asn_list.json'))

# from https://github.com/Qclover/CDNCheck/blob/master/checkCDN/cdn3_check.py
cdn_cname_keyword = utils.load_json(data_dir.joinpath('cdn_cname_keywords.json'))

cdn_header_key = utils.load_json(data_dir.joinpath('cdn_header_keys.json'))


def check_cname_keyword(cname):
    if not cname:
        return False
    names = cname.lower().split(',')
    for name in names:
        for keyword in cdn_cname_keyword.keys():
            if keyword in name:
                return True


def check_header_key(header):
    if isinstance(header, str):
        header = json.loads(header)
    if isinstance(header, dict):
        header = set(map(lambda x: x.lower(), header.keys()))
        for key in cdn_header_key:
            if key in header:
                return True
    else:
        return False


def check_cdn_cidr(ips):
    if isinstance(ips, str):
        ips = set(ips.split(','))
    else:
        return False
    for ip in ips:
        try:
            ip = ipaddress.ip_address(ip)
        except Exception as e:
            logger.log('DEBUG', e.args)
            return False
        for cidr in cdn_ip_cidr:
            if ip in ipaddress.ip_network(cidr):
                return True


def check_cdn_asn(asn):
    if isinstance(asn, str):
        if asn in cdn_asn_list:
            return True
    return False


def do_check(data):
    logger.log('DEBUG', f'Checking cdn')
    for index, item in enumerate(data):
        cname = item.get('cname')
        if check_cname_keyword(cname):
            data[index]['cdn'] = 1
            continue
        header = item.get('header')
        if check_header_key(header):
            data[index]['cdn'] = 1
            continue
        ip = item.get('ip')
        if check_cdn_cidr(ip):
            data[index]['cdn'] = 1
            continue
        asn = item.get('asn')
        if check_cdn_asn(asn):
            data[index]['cdn'] = 1
            continue
        data[index]['cdn'] = 0
    return data
