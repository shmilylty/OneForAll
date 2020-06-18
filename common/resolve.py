import gc
import json

from config.log import logger
from config import setting
from common import utils
from common.database import Database
from common.ipasn import IPAsnInfo
from common.ipgeo import IpGeoInfo
from common.ipreg import IpRegInfo


def filter_subdomain(data):
    """
    过滤出无解析内容的子域到新的子域列表

    :param list data: 待过滤的数据列表
    :return: 符合条件的子域列表
    """
    logger.log('DEBUG', f'Filtering subdomains to be resolved')
    subdomains = []
    for data in data:
        if not data.get('content'):
            subdomain = data.get('subdomain')
            subdomains.append(subdomain)
    return subdomains


def update_data(data, records):
    """
    更新解析结果

    :param list data: 待更新的数据列表
    :param dict records: 解析结果字典
    :return: 更新后的数据列表
    """
    logger.log('DEBUG', f'Updating resolved results')
    if not records:
        logger.log('ERROR', f'No valid resolved result')
        return data
    for index, items in enumerate(data):
        if not items.get('content'):
            subdomain = items.get('subdomain')
            record = records.get(subdomain)
            if record:
                items.update(record)
            data[index] = items
    return data


def save_data(name, data):
    """
    保存解析结果到数据库

    :param str name: 保存表名
    :param list data: 待保存的数据
    """
    logger.log('INFOR', f'Saving resolved results')
    db = Database()
    db.drop_table(name)
    db.create_table(name)
    db.save_db(name, data, 'resolve')
    db.close()


def save_subdomains(save_path, subdomain_list):
    logger.log('DEBUG', f'Saving resolved subdomain')
    subdomain_data = '\n'.join(subdomain_list)
    if not utils.save_data(save_path, subdomain_data):
        logger.log('FATAL', 'Save resolved subdomain error')
        exit(1)


def deal_output(output_path):
    logger.log('INFOR', f'Processing resolved results')
    records = dict()  # 用来记录所有域名解析数据
    ip_asn = IPAsnInfo()
    ip_geo = IpGeoInfo
    db_path = setting.data_storage_dir.joinpath('ip2region.db')
    ip_reg = IpRegInfo(db_path)
    with open(output_path) as fd:
        for line in fd:
            line = line.strip()
            try:
                items = json.loads(line)
            except Exception as e:
                logger.log('ERROR', e.args)
                logger.log('ERROR', f'Error resolve line {line}, skip this line')
                continue
            record = dict()
            record['resolver'] = items.get('resolver')
            qname = items.get('name')[:-1]  # 去除最右边的`.`点号
            status = items.get('status')
            if status != 'NOERROR':
                record['alive'] = 0
                record['resolve'] = 0
                record['reason'] = status
                records[qname] = record
                continue
            data = items.get('data')
            if 'answers' not in data:
                record['alive'] = 0
                record['resolve'] = 0
                record['reason'] = 'NOANSWER'
                records[qname] = record
                continue
            flag = False
            cname = list()
            ips = list()
            public = list()
            ttls = list()
            cidrs = list()
            asns = list()
            locs = list()
            regs = list()
            answers = data.get('answers')
            for answer in answers:
                if answer.get('type') == 'A':
                    flag = True
                    cname.append(answer.get('name')[:-1])  # 去除最右边的`.`点号
                    ip = answer.get('data')
                    ips.append(ip)
                    ttl = answer.get('ttl')
                    ttls.append(str(ttl))
                    is_public = utils.ip_is_public(ip)
                    public.append(str(is_public))
                    asn_info = ip_asn.find(ip)
                    cidrs.append(asn_info.get('cidr'))
                    asns.append(asn_info.get('asn'))
                    loc = f'{ip_geo.get_country_long(ip)} ' \
                          f'{ip_geo.get_region(ip)} ' \
                          f'{ip_geo.get_city(ip)}'
                    locs.append(loc)
                    reg = ip_reg.memory_search(ip).get('region').decode('utf-8')
                    regs.append(reg)
                    record['resolve'] = 1
                    record['reason'] = status
                    record['cname'] = ','.join(cname)
                    record['content'] = ','.join(ips)
                    record['public'] = ','.join(public)
                    record['ttl'] = ','.join(ttls)
                    record['cidr'] = ','.join(cidrs)
                    record['asn'] = ','.join(asns)
                    record['ip2location'] = ','.join(locs)
                    record['ip2region'] = ','.join(regs)
                    records[qname] = record
            if not flag:
                record['alive'] = 0
                record['resolve'] = 0
                record['reason'] = 'NOARECORD'
                records[qname] = record
    return records


def run_resolve(domain, data):
    """
    调用子域解析入口函数

    :param str domain: 待解析的主域
    :param list data: 待解析的子域数据列表
    :return: 解析得到的结果列表
    :rtype: list
    """
    logger.log('INFOR', f'Start resolve subdomains of {domain}')
    subdomains = filter_subdomain(data)
    if not subdomains:
        return data

    massdns_dir = setting.third_party_dir.joinpath('massdns')
    result_dir = setting.result_save_dir
    temp_dir = result_dir.joinpath('temp')
    utils.check_dir(temp_dir)
    massdns_path = utils.get_massdns_path(massdns_dir)
    timestring = utils.get_timestring()

    save_name = f'collected_subdomains_{domain}_{timestring}.txt'
    save_path = temp_dir.joinpath(save_name)
    save_subdomains(save_path, subdomains)
    del subdomains
    gc.collect()

    output_name = f'resolved_result_{domain}_{timestring}.json'
    output_path = temp_dir.joinpath(output_name)
    log_path = result_dir.joinpath('massdns.log')

    ns_path = setting.brute_nameservers_path

    logger.log('INFOR', f'Running massdns to resolve subdomains')
    utils.call_massdns(massdns_path, save_path, ns_path,
                       output_path, log_path, quiet_mode=True)

    records = deal_output(output_path)
    data = update_data(data, records)
    logger.log('INFOR', f'Finished resolve subdomains of {domain}')
    return data
