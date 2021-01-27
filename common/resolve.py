import gc
import json

from config.log import logger
from config import settings
from common import utils


def filter_subdomain(data):
    """
    过滤出无解析内容的子域到新的子域列表

    :param list data: 待过滤的数据列表
    :return: 符合条件的子域列表
    """
    logger.log('DEBUG', f'Filtering subdomains to be resolved')
    subdomains = []
    for infos in data:
        if not infos.get('ip'):
            subdomain = infos.get('subdomain')
            if subdomain:
                subdomains.append(subdomain)
    return subdomains


def update_data(data, infos):
    """
    更新解析结果

    :param list data: 待更新的数据列表
    :param dict infos: 子域有关结果信息
    :return: 更新后的数据列表
    """
    logger.log('DEBUG', f'Updating resolved results')
    if not infos:
        logger.log('ALERT', f'No valid resolved result')
        return data
    new_data = list()
    for index, items in enumerate(data):
        if items.get('ip'):
            new_data.append(items)
            continue
        subdomain = items.get('subdomain')
        record = infos.get(subdomain)
        if record:
            items.update(record)
            new_data.append(items)
        else:
            subdomain = items.get('subdomain')
            logger.log('DEBUG', f'{subdomain} resolution has no result')
    return new_data


def save_db(name, data):
    """
    Save resolved results to database

    :param str  name: table name
    :param list data: data to be saved
    """
    logger.log('INFOR', f'Saving resolved results')
    utils.save_to_db(name, data, 'resolve')


def save_subdomains(save_path, subdomain_list):
    logger.log('DEBUG', f'Saving resolved subdomain')
    subdomain_data = '\n'.join(subdomain_list)
    if not utils.save_to_file(save_path, subdomain_data):
        logger.log('FATAL', 'Save resolved subdomain error')
        exit(1)


def gen_infos(data, qname, info, infos):
    flag = False
    cnames = list()
    ips = list()
    ttl = list()
    answers = data.get('answers')
    for answer in answers:
        if answer.get('type') == 'A':
            flag = True
            name = answer.get('name')
            cname = name[:-1].lower()  # 去除最右边的`.`点号
            cnames.append(cname)
            ip = answer.get('data')
            ips.append(ip)
            ttl.append(str(answer.get('ttl')))
            info['resolve'] = 1
            info['reason'] = 'OK'
            info['cname'] = ','.join(cnames)
            info['ip'] = ','.join(ips)
            info['ttl'] = ','.join(ttl)
            infos[qname] = info
    if not flag:
        logger.log('DEBUG', f'Resolving {qname} have not a record')
        info['alive'] = 0
        info['resolve'] = 0
        info['reason'] = 'NoARecord'
        infos[qname] = info
    return infos


def deal_output(output_path):
    logger.log('INFOR', f'Processing resolved results')
    infos = dict()  # 用来记录所有域名有关信息
    with open(output_path) as fd:
        for line in fd:
            line = line.strip()
            try:
                items = json.loads(line)
            except Exception as e:
                logger.log('ERROR', e.args)
                logger.log('ERROR', f'Error resolve line {line}, skip this line')
                continue
            info = dict()
            info['resolver'] = items.get('resolver')
            qname = items.get('name')[:-1]  # 去除最右边的`.`点号
            status = items.get('status')
            if status != 'NOERROR':
                logger.log('DEBUG', f'Resolving {qname}: {status}')
                continue
            data = items.get('data')
            if 'answers' not in data:
                logger.log('DEBUG', f'Resolving {qname} have not any answers')
                info['alive'] = 0
                info['resolve'] = 0
                info['reason'] = 'NoAnswer'
                infos[qname] = info
                continue
            infos = gen_infos(data, qname, info, infos)
    return infos


def run_resolve(domain, data):
    """
    调用子域解析入口函数

    :param str domain: 待解析的主域
    :param list data: 待解析的子域数据列表
    :return: 解析得到的结果列表
    :rtype: list
    """
    logger.log('INFOR', f'Start resolving subdomains of {domain}')
    subdomains = filter_subdomain(data)
    if not subdomains:
        return data

    massdns_dir = settings.third_party_dir.joinpath('massdns')
    result_dir = settings.result_save_dir
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
    ns_path = utils.get_ns_path()

    logger.log('INFOR', f'Running massdns to resolve subdomains')
    utils.call_massdns(massdns_path, save_path, ns_path,
                       output_path, log_path, quiet_mode=True)

    infos = deal_output(output_path)
    data = update_data(data, infos)
    logger.log('INFOR', f'Finished resolve subdomains of {domain}')
    return data
