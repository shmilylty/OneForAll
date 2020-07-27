import json
import ipaddress

from config import setting
from common import utils
from config.log import logger

data_dir = setting.data_storage_dir

# from https://github.com/al0ne/Vxscan/blob/master/lib/iscdn.py
cdn_ip_cidr = utils.load_json(data_dir.joinpath('cdn_ip_cidr.json'))
cdn_asn_list = utils.load_json(data_dir.joinpath('cdn_asn_list.json'))

# from https://github.com/Qclover/CDNCheck/blob/master/checkCDN/cdn3_check.py
cdn_cname_keyword = utils.load_json(data_dir.joinpath('cdn_cname_keywords.json'))

cdn_header_key = utils.load_json(data_dir.joinpath('cdn_header_keys.json'))


def check_cname_count(cnames):
    if len(cnames) > 1:
        return True


def check_cname_keyword(cname):
    names = cname.lower().split(',')
    for name in names:
        for keyword in cdn_cname_keyword.keys():
            if keyword in name:
                return True


def check_header_key(header):
    header = set(map(lambda x: x.lower(), header.keys()))
    for key in cdn_header_key:
        if key in header:
            return True


def check_cdn_cidr(content):
    ips = set(content.split(','))
    for ip in ips:
        ip = ipaddress.ip_address(ip)
        for cidr in cdn_ip_cidr:
            if ip in ipaddress.ip_network(cidr):
                return True


def check_cdn_asn(asn):
    if str(asn) in cdn_asn_list:
        return True


def check_cdn(data):
    for index, item in enumerate(data):
        cname = item.get('cname')
        if cname:
            if check_cname_keyword(cname):
                data[index]['cdn'] = 1
                continue
        header = item.get('header')
        if header:
            header = json.loads(header)
            if check_header_key(header):
                data[index]['cdn'] = 1
                continue
        kind = item.get('type')
        content = item.get('content')
        if kind == 'A' and content:
            if check_cdn_cidr(content):
                data[index]['cdn'] = 1
                continue
        asn = item.get('asn')
        if asn:
            asn = asn[2:]  # 去除AS
            if check_cdn_asn(asn):
                data[index]['cdn'] = 1
                continue
        data[index]['cdn'] = 0
    return data


def save_db(name, data):
    logger.log('INFOR', f'Saving cdn check results')
    utils.save_db(name, data, 'cdn')
