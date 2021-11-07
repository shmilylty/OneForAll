from modules import iscdn
from common import utils
from common.database import Database
from common.ipasn import IPAsnInfo
from common.ipreg import IpRegData


def get_ips(info):
    ip = info.get('ip')
    if not ip:
        return None
    ips = ip.split(',')
    return ips


def enrich_info(data):
    ip_asn = IPAsnInfo()
    ip_reg = IpRegData()
    for index, info in enumerate(data):
        ips = get_ips(info)
        if not ips:
            continue
        public = list()
        cidr = list()
        asn = list()
        org = list()
        addr = list()
        isp = list()
        for ip in ips:
            public.append(str(utils.ip_is_public(ip)))
            asn_info = ip_asn.find(ip)
            cidr.append(asn_info.get('cidr'))
            asn.append(asn_info.get('asn'))
            org.append(asn_info.get('org'))
            ip_info = ip_reg.query(ip)
            addr.append(ip_info.get('addr'))
            isp.append(ip_info.get('isp'))
        data[index]['public'] = ','.join(public)
        data[index]['cidr'] = ','.join(cidr)
        data[index]['asn'] = ','.join(asn)
        data[index]['org'] = ','.join(org)
        data[index]['addr'] = ','.join(addr)
        data[index]['isp'] = ','.join(isp)
    return data


class Enrich(object):
    def __init__(self, domain):
        self.domain = domain

    def get_data(self):
        db = Database()
        fields = ['url', 'cname', 'ip', 'public', 'cdn', 'header',
                  'cidr', 'asn', 'org', 'addr', 'isp']
        results = db.get_data_by_fields(self.domain, fields)
        return results.as_dict()

    def save_db(self, data):
        db = Database()
        for info in data:
            url = info.pop('url')
            info.pop('cname')
            info.pop('ip')
            info.pop('header')
            db.update_data_by_url(self.domain, info, url)
        db.close()

    def run(self):
        data = self.get_data()
        data = enrich_info(data)
        data = iscdn.do_check(data)
        self.save_db(data)
