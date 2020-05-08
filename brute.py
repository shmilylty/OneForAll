#!/usr/bin/python3
# coding=utf-8

"""
OneForAll子域爆破模块

:copyright: Copyright (c) 2019, Jing Ling. All rights reserved.
:license: GNU General Public License v3.0, see LICENSE for more details.
"""
import gc
import json
import time
import random
import secrets

import exrex
import fire
import tenacity
from dns.exception import Timeout
from dns.resolver import NXDOMAIN, YXDOMAIN, NoAnswer, NoNameservers

import dbexport
from common import utils
from config import setting
from common.module import Module
from config.log import logger


@tenacity.retry(stop=tenacity.stop_after_attempt(3))
def do_query_a(domain, resolver):
    try:
        answer = resolver.query(domain, 'A')
    # 如果查询随机域名A记录时抛出Timeout异常则重新探测
    except Timeout as e:
        logger.log('ALERT', f'探测超时重新探测中')
        logger.log('DEBUG', e.args)
        raise tenacity.TryAgain
    # 如果查询随机域名A记录时抛出NXDOMAIN异常
    # 则说明不存在随机子域的A记录 即没有开启泛解析
    except (NXDOMAIN, YXDOMAIN, NoAnswer, NoNameservers) as e:
        logger.log('DEBUG', e.args)
        logger.log('INFOR', f'{domain}没有使用泛解析')
        return False
    except Exception as e:
        logger.log('ALERT', f'探测{domain}是否使用泛解析出错')
        logger.log('FATAL', e.args)
        exit(1)
    else:
        if answer.rrset is None:
            logger.log('ALERT', f'结果无记录重新探测中')
            raise tenacity.TryAgain
        ttl = answer.ttl
        name = answer.name
        ips = {item.address for item in answer}
        logger.log('ALERT', f'{domain}使用了泛解析')
        logger.log('ALERT', f'{domain} 解析到域名: {name} '
                            f'IP: {ips} TTL: {ttl}')
        return True


def detect_wildcard(domain, authoritative_ns):
    """
    探测域名是否使用泛解析

    :param str domain: 域名
    :param list authoritative_ns: 权威DNS
    :return: 是否使用泛解析
    """
    logger.log('INFOR', f'正在探测{domain}是否使用泛解析')
    token = secrets.token_hex(4)
    random_subdomain = f'{token}.{domain}'
    resolver = utils.dns_resolver()
    resolver.nameservers = authoritative_ns
    resolver.rotate = True
    resolver.cache = None
    try:
        wildcard = do_query_a(random_subdomain, resolver)
    except Exception as e:
        logger.log('DEBUG', e.args)
        logger.log('ALERT', f'多次探测出错暂且认为{domain}没有使用泛解析')
        return False
    else:
        return wildcard


def gen_fuzz_subdomains(expression, rule):
    """
    生成基于fuzz模式的爆破子域

    :param str expression: 子域域名生成表达式
    :param str rule: 生成子域所需的正则规则
    :return: 用于爆破的子域
    """
    subdomains = list()
    fuzz_count = exrex.count(rule)
    if fuzz_count > 10000000:
        logger.log('ALERT', f'请注意该规则生成的字典太大：{fuzz_count} > 10000000')
    logger.log('DEBUG', f'fuzz模式下生成的字典大小：{fuzz_count}')
    for fuzz_string in exrex.generate(rule):
        fuzz_string = fuzz_string.lower()
        if not fuzz_string.isalnum():
            continue
        fuzz_domain = expression.replace('*', fuzz_string)
        subdomains.append(fuzz_domain)
    random_domain = random.choice(subdomains)
    logger.log('ALERT', f'请注意检查基于fuzz模式生成的{random_domain}是否正确')
    return subdomains


def gen_word_subdomains(expression, path):
    """
    生成基于word模式的爆破子域

    :param str expression: 子域域名生成表达式
    :param str path: 字典路径
    :return: 用于爆破的子域
    """
    subdomains = list()
    with open(path, encoding='utf-8', errors='ignore') as fd:
        for line in fd:
            word = line.strip().lower()
            if not word.isalnum():
                continue
            if word.endswith('.'):
                word = word[:-1]
            subdomain = expression.replace('*', word)
            subdomains.append(subdomain)
    random_domain = random.choice(subdomains)
    logger.log('DEBUG', f'fuzz模式下生成的字典大小：{len(subdomains)}')
    logger.log('ALERT', f'请注意检查基于word模式生成的{random_domain}是否正确')
    return subdomains


def query_domain_ns_a(ns_list):
    logger.log('INFOR', f'正在查询权威DNS名称服务器{ns_list}的A记录')
    if not isinstance(ns_list, list):
        return list()
    ns_ip_list = []
    resolver = utils.dns_resolver()
    for ns in ns_list:
        try:
            answer = resolver.query(ns, 'A')
        except Exception as e:
            logger.log('ERROR', e.args)
            logger.log('ERROR', f'查询权威DNS名称服务器{ns}的A记录出错')
            continue
        if answer:
            for item in answer:
                ns_ip_list.append(item.address)
    logger.log('INFOR', f'权威DNS名称服务器对应A记录 {ns_ip_list}')
    return ns_ip_list


def query_domain_ns(domain):
    logger.log('INFOR', f'正在查询{domain}的NS记录')
    domain = utils.get_maindomain(domain)
    resolver = utils.dns_resolver()
    try:
        answer = resolver.query(domain, 'NS')
    except Exception as e:
        logger.log('ERROR', e.args)
        logger.log('ERROR', f'查询{domain}的NS记录出错')
        return list()
    ns = [item.to_text() for item in answer]
    logger.log('INFOR', f'{domain}的权威DNS名称服务器 {ns}')
    return ns


@tenacity.retry(stop=tenacity.stop_after_attempt(2))
def get_wildcard_record(domain, resolver):
    logger.log('INFOR', f'查询{domain}在权威DNS名称服务器的泛解析记录')
    try:
        answer = resolver.query(domain, 'A')
    # 如果查询随机域名A记录时抛出Timeout异常则重新查询
    except Timeout as e:
        logger.log('ALERT', f'查询超时重新查询中')
        logger.log('DEBUG', e.args)
        raise tenacity.TryAgain
    except (NXDOMAIN, YXDOMAIN, NoAnswer, NoNameservers) as e:
        logger.log('DEBUG', e.args)
        logger.log('INFOR', f'{domain}在权威DNS名称服务器上没有A记录')
        return None, None
    except Exception as e:
        logger.log('ERROR', e.args)
        logger.log('ERROR', f'查询{domain}在权威DNS名称服务器泛解析记录出错')
        exit(1)
    else:
        if answer.rrset is None:
            logger.log('DEBUG', f'查询结果无记录')
            return None, None
        name = answer.name
        ip = {item.address for item in answer}
        ttl = answer.ttl
        logger.log('INFOR', f'{domain} 在权威DNS上解析到域名: {name} '
                            f'IP: {ip} TTL: {ttl}')
        return ip, ttl


def collect_wildcard_record(domain, authoritative_ns):
    logger.log('INFOR', f'正在收集{domain}的泛解析记录')
    if not authoritative_ns:
        return list(), int()
    resolver = utils.dns_resolver()
    resolver.nameservers = authoritative_ns
    resolver.rotate = True
    resolver.cache = None
    ips = set()
    ttl = int()
    ips_stat = dict()
    while True:
        token = secrets.token_hex(4)
        random_subdomain = f'{token}.{domain}'
        try:
            ip, ttl = get_wildcard_record(random_subdomain, resolver)
        except Exception as e:
            logger.log('DEBUG', e.args)
            logger.log('ALERT', f'多次查询出错将尝试查询新的随机子域')
            continue
        if ip is None:
            continue
        ips = ips.union(ip)
        # 统计每个泛解析IP出现次数
        for addr in ip:
            count = ips_stat.setdefault(addr, 0)
            ips_stat[addr] = count + 1
        # 筛选出出现次数2次以上的IP地址
        addrs = list()
        for addr, times in ips_stat.items():
            if times >= 2:
                addrs.append(addr)
        # 大部分的IP地址出现次数大于2次停止收集泛解析IP记录
        if len(addrs) / len(ips) >= 0.8:
            break
    logger.log('DEBUG', f'收集到{domain}的泛解析记录\n{ips}\n{ttl}')
    return ips, ttl


def get_nameservers_path(enable_wildcard, ns_ip_list):
    path = setting.brute_nameservers_path
    if not enable_wildcard:
        return path
    if not ns_ip_list:
        return path
    path = setting.authoritative_dns_path
    ns_data = '\n'.join(ns_ip_list)
    utils.save_data(path, ns_data)
    return path


def check_dict():
    if not setting.enable_check_dict:
        return
    sec = setting.check_time
    logger.log('ALERT', f'你有{sec}秒时间检查爆破配置是否正确')
    logger.log('ALERT', f'退出爆破请使用`Ctrl+C`')
    try:
        time.sleep(sec)
    except KeyboardInterrupt:
        logger.log('INFOR', '爆破配置有误退出爆破')
        exit(0)


def gen_records(items, records, subdomains, ip_times, wc_ips, wc_ttl):
    qname = items.get('name')[:-1]  # 去出最右边的`.`点号
    reason = items.get('status')
    resolver = items.get('resolver')
    data = items.get('data')
    answers = data.get('answers')
    record = dict()
    cname = list()
    ips = list()
    public = list()
    times = list()
    ttls = list()
    is_valid_flags = list()
    have_a_record = False
    for answer in answers:
        if answer.get('type') != 'A':
            logger.log('TRACE', f'查询{qname}返回的应答没有A记录\n{answer}')
            continue
        logger.log('TRACE', f'查询{qname}返回的应答具有A记录\n{answer}')
        have_a_record = True
        ttl = answer.get('ttl')
        ttls.append(ttl)
        cname.append(answer.get('name')[:-1])  # 去出最右边的`.`点号
        ip = answer.get('data')
        ips.append(ip)
        public.append(utils.ip_is_public(ip))
        num = ip_times.get(ip)
        times.append(num)
        isvalid, reason = is_valid_subdomain(ip, ttl, num, wc_ips, wc_ttl)
        logger.log('TRACE', f'{ip}是否有效:{isvalid} 原因:{reason}')
        is_valid_flags.append(isvalid)
    if not have_a_record:
        logger.log('TRACE', f'查询{qname}返回的所有应答都中没有A记录{answers}')
    # 为了优化内存 只添加有A记录且通过判断的子域到记录中
    if have_a_record and all(is_valid_flags):
        record['resolve'] = 1
        record['reason'] = reason
        record['ttl'] = ttls
        record['cname'] = cname
        record['content'] = ips
        record['public'] = public
        record['times'] = times
        record['resolver'] = resolver
        records[qname] = record
        subdomains.append(qname)
    return records, subdomains


def stat_ip_times(result_paths):
    logger.log('INFOR', f'正在统计IP次数')
    times = dict()
    for result_path in result_paths:
        logger.log('DEBUG', f'正在读取{result_path}')
        with open(result_path) as fd:
            for line in fd:
                line = line.strip()
                try:
                    items = json.loads(line)
                except Exception as e:
                    logger.log('ERROR', e.args)
                    logger.log('ERROR', f'解析{result_path}行{line}出错跳过解析该行')
                    continue
                status = items.get('status')
                if status != 'NOERROR':
                    continue
                data = items.get('data')
                if 'answers' not in data:
                    continue
                answers = data.get('answers')
                for answer in answers:
                    if answer.get('type') == 'A':
                        ip = answer.get('data')
                        # 取值 如果是首次出现的IP集合 出现次数先赋值0
                        value = times.setdefault(ip, 0)
                        times[ip] = value + 1
    return times


def deal_output(output_paths, ip_times, wildcard_ips, wildcard_ttl):
    logger.log('INFOR', f'正在处理解析结果')
    records = dict()  # 用来记录所有域名解析数据
    subdomains = list()  # 用来保存所有通过有效性检查的子域
    for output_path in output_paths:
        logger.log('DEBUG', f'正在处理{output_path}')
        with open(output_path) as fd:
            for line in fd:
                line = line.strip()
                try:
                    items = json.loads(line)
                except Exception as e:
                    logger.log('ERROR', e.args)
                    logger.log('ERROR', f'解析行{line}出错跳过解析该行')
                    continue
                qname = items.get('name')[:-1]  # 去出最右边的`.`点号
                status = items.get('status')
                if status != 'NOERROR':
                    logger.log('TRACE', f'处理{line}时发现{qname}查询结果状态{status}')
                    continue
                data = items.get('data')
                if 'answers' not in data:
                    logger.log('TRACE', f'处理{line}时发现{qname}返回的结果无应答')
                    continue
                records, subdomains = gen_records(items, records, subdomains,
                                                  ip_times, wildcard_ips,
                                                  wildcard_ttl)
    return records, subdomains


def check_by_compare(ip, ttl, wc_ips, wc_ttl):
    """
    通过与泛解析返回的IP集合和返回的TTL值进行对比判断发现的子域是否是泛解析子域

    :param set ip: 子域A记录查询出的IP
    :param int ttl: 子域A记录查询出的TTL
    :param set wc_ips: 泛解析的IP集合
    :param int wc_ttl: 泛解析的TTL
    :return: 判断结果
    """
    # 参考：http://sh3ll.me/archives/201704041222.txt
    if ip not in wc_ips:
        return False  # 子域IP不在泛解析IP集合则不是泛解析
    if ttl != wc_ttl and ttl % 60 == 0 and wc_ttl % 60 == 0:
        return False
    return True


def check_ip_times(times):
    """
    根据ip出现次数判断是否为泛解析

    :param times: 子域IP出现次数
    :return: 判断结果
    """
    if times > setting.ip_appear_maximum:
        return True
    return False


def is_valid_subdomain(ip, ttl, times, wc_ips, wc_ttl):
    ip_blacklist = setting.brute_ip_blacklist
    if ip in ip_blacklist:  # 解析ip在黑名单ip则为非法子域
        return 0, 'IP blacklist'
    if all([wc_ips, wc_ttl]):  # 有泛解析记录才进行对比
        if check_by_compare(ip, ttl, wc_ips, wc_ttl):
            return 0, 'IP wildcard'
    if check_ip_times(times):
        return 0, 'IP exceeded'
    return 1, 'OK'


def save_brute_dict(dict_path, dict_set):
    dict_data = '\n'.join(dict_set)
    if not utils.save_data(dict_path, dict_data):
        logger.log('FATAL', '保存生成的字典出错')
        exit(1)


def delete_file(dict_path, output_paths):
    if setting.delete_generated_dict:
        dict_path.unlink()
    if setting.delete_massdns_result:
        for output_path in output_paths:
            output_path.unlink()


class Brute(Module):
    """
    OneForAll子域爆破模块

    Example：
        brute.py --target domain.com --word True run
        brute.py --target ./domains.txt --word True run
        brute.py --target domain.com --word True --process 1 run
        brute.py --target domain.com --word True --wordlist subnames.txt run
        brute.py --target domain.com --word True --recursive True --depth 2 run
        brute.py --target d.com --fuzz True --place m.*.d.com --rule '[a-z]' run

    Note:
        参数alive可选值True，False分别表示导出存活，全部子域结果
        参数format可选格式有'txt', 'rst', 'csv', 'tsv', 'json', 'yaml', 'html',
                          'jira', 'xls', 'xlsx', 'dbf', 'latex', 'ods'
        参数path默认None使用OneForAll结果目录自动生成路径

    :param str target:       单个域名或者每行一个域名的文件路径
    :param int process:      爆破进程数(默认1)
    :param int concurrent:   并发爆破数量(默认10000)
    :param bool word:        是否使用word模式进行爆破(默认False)
    :param str wordlist:     word模式爆破使用的字典路径(默认使用setting.py配置)
    :param bool recursive:   是否使用递归进行爆破(默认False)
    :param int depth:        递归爆破的深度(默认2)
    :param str nextlist:     递归爆破所使用的字典路径(默认使用setting.py配置)
    :param bool fuzz:        是否使用fuzz模式进行爆破(默认False)
    :param str place:        指定爆破位置(开启fuzz模式时必需指定此参数)
    :param str rule:         指定fuzz模式爆破使用的正则规则(开启fuzz模式时必需指定此参数)
    :param bool export:      是否导出爆破结果(默认True)
    :param bool alive:       只导出存活的子域结果(默认True)
    :param str format:       结果导出格式(默认csv)
    :param str path:         结果导出路径(默认None)
    """

    def __init__(self, target, process=None, concurrent=None, word=False,
                 wordlist=None, recursive=False, depth=None, nextlist=None,
                 fuzz=False, place=None, rule=None, export=True, alive=True,
                 format='csv', path=None):
        Module.__init__(self)
        self.module = 'Brute'
        self.source = 'Brute'
        self.target = target
        self.process_num = process or utils.get_process_num()
        self.concurrent_num = concurrent or setting.brute_concurrent_num
        self.word = word
        self.wordlist = wordlist or setting.brute_wordlist_path
        self.recursive_brute = recursive or setting.enable_recursive_brute
        self.recursive_depth = depth or setting.brute_recursive_depth
        self.recursive_nextlist = nextlist or setting.recursive_nextlist_path
        self.fuzz = fuzz or setting.enable_fuzz
        self.place = place or setting.fuzz_place
        self.rule = rule or setting.fuzz_rule
        self.export = export
        self.alive = alive
        self.format = format
        self.path = path
        self.bulk = False  # 是否是批量爆破场景
        self.domains = list()  # 待爆破的所有域名集合
        self.domain = str()  # 当前正在进行爆破的域名
        self.ips_times = dict()  # IP集合出现次数
        self.enable_wildcard = False  # 当前域名是否使用泛解析
        self.wildcard_check = setting.enable_wildcard_check
        self.wildcard_deal = setting.enable_wildcard_deal
        self.check_env = True

    def gen_brute_dict(self, domain):
        logger.log('INFOR', f'正在为{domain}生成爆破字典')
        dict_set = set()
        # 如果domain不是self.subdomain 而是self.domain的子域则生成递归爆破字典
        if self.place is None:
            self.place = '*.' + domain
        wordlist = self.wordlist
        main_domain = self.register(domain)
        if domain != main_domain:
            wordlist = self.recursive_nextlist
        if self.word:
            word_subdomains = gen_word_subdomains(self.place, wordlist)
            # set可以合并list
            dict_set = dict_set.union(word_subdomains)
        if self.fuzz:
            fuzz_subdomains = gen_fuzz_subdomains(self.place, self.rule)
            dict_set = dict_set.union(fuzz_subdomains)
        # logger.log('INFOR', f'正在去重爆破字典')
        # dict_set = utils.uniq_dict_list(dict_set)
        count = len(dict_set)
        logger.log('INFOR', f'生成的爆破字典大小为{count}')
        if count > 10000000:
            logger.log('ALERT', f'注意生成的爆破字典太大：{count} > 10000000')
        return dict_set

    def check_brute_params(self):
        if not (self.word or self.fuzz):
            logger.log('FATAL', f'请至少指定一种爆破模式')
            exit(1)
        if len(self.domains) > 1:
            self.bulk = True
        if self.fuzz:
            if self.place is None or self.rule is None:
                logger.log('FATAL', f'没有指定fuzz位置或规则')
                exit(1)
            if self.bulk:
                logger.log('FATAL', f'批量爆破的场景下不能使用fuzz模式')
                exit(1)
            if self.recursive_brute:
                logger.log('FATAL', f'使用fuzz模式下不能使用递归爆破')
                exit(1)
            fuzz_count = self.place.count('*')
            if fuzz_count < 1:
                logger.log('FATAL', f'没有指定fuzz位置')
                exit(1)
            if fuzz_count > 1:
                logger.log('FATAL', f'只能指定1个fuzz位置')
                exit(1)
            if self.domain not in self.place:
                logger.log('FATAL', f'指定fuzz的域名有误')
                exit(1)

    def main(self, domain):
        start = time.time()
        logger.log('INFOR', f'正在爆破域名{domain}')
        massdns_dir = setting.third_party_dir.joinpath('massdns')
        result_dir = setting.result_save_dir
        temp_dir = result_dir.joinpath('temp')
        utils.check_dir(temp_dir)
        massdns_path = utils.get_massdns_path(massdns_dir)
        timestring = utils.get_timestring()

        wildcard_ips = list()  # 泛解析IP列表
        wildcard_ttl = int()  # 泛解析TTL整型值
        ns_list = query_domain_ns(self.domain)
        ns_ip_list = query_domain_ns_a(ns_list)  # DNS权威名称服务器对应A记录列表
        self.enable_wildcard = detect_wildcard(domain, ns_ip_list)

        if self.enable_wildcard:
            wildcard_ips, wildcard_ttl = collect_wildcard_record(domain,
                                                                 ns_ip_list)
        ns_path = get_nameservers_path(self.enable_wildcard, ns_ip_list)

        dict_set = self.gen_brute_dict(domain)
        dict_len = len(dict_set)

        dict_name = f'generated_subdomains_{domain}_{timestring}.txt'
        dict_path = temp_dir.joinpath(dict_name)
        save_brute_dict(dict_path, dict_set)
        del dict_set
        gc.collect()

        output_name = f'resolved_result_{domain}_{timestring}.json'
        output_path = temp_dir.joinpath(output_name)
        log_path = result_dir.joinpath('massdns.log')
        check_dict()

        utils.call_massdns(massdns_path, dict_path, ns_path, output_path,
                           log_path, process_num=self.process_num,
                           concurrent_num=self.concurrent_num)

        output_paths = []
        if self.process_num == 1:
            output_paths.append(output_path)
        else:
            for i in range(self.process_num):
                output_name = f'resolved_result_{domain}_{timestring}.json{i}'
                output_path = temp_dir.joinpath(output_name)
                output_paths.append(output_path)
        ip_times = stat_ip_times(output_paths)
        self.records, self.subdomains = deal_output(output_paths, ip_times,
                                                    wildcard_ips, wildcard_ttl)
        delete_file(dict_path, output_paths)
        end = time.time()
        self.elapse = round(end - start, 1)
        logger.log('INFOR', f'{self.source}模块耗时{self.elapse}秒'
                            f'发现{domain}的子域{len(self.subdomains)}个')
        logger.log('DEBUG', f'{self.source}模块发现{domain}的子域:\n'
                            f'{self.subdomains}')
        self.gen_result(brute=dict_len, valid=len(self.subdomains))
        self.save_db()
        return self.subdomains

    def run(self):
        logger.log('INFOR', f'开始执行{self.source}模块')
        if self.check_env:
            utils.check_env()
        self.domains = utils.get_domains(self.target)
        all_subdomains = list()
        for self.domain in self.domains:
            self.check_brute_params()
            if self.recursive_brute:
                logger.log('INFOR', f'开始递归爆破{self.domain}的第1层子域')
            valid_subdomains = self.main(self.domain)
            all_subdomains.extend(valid_subdomains)

            # 递归爆破下一层的子域
            # fuzz模式不使用递归爆破
            if self.recursive_brute:
                for layer_num in range(1, self.recursive_depth):
                    # 之前已经做过1层子域爆破 当前实际递归层数是layer+1
                    logger.log('INFOR', f'开始递归爆破{self.domain}的'
                                        f'第{layer_num + 1}层子域')
                    for subdomain in all_subdomains:
                        self.place = '*.' + subdomain
                        # 进行下一层子域爆破的限制条件
                        num = subdomain.count('.') - self.domain.count('.')
                        if num == layer_num:
                            valid_subdomains = self.main(subdomain)
                            all_subdomains.extend(valid_subdomains)

            logger.log('INFOR', f'结束执行{self.source}模块爆破域名{self.domain}')
            if not self.path:
                name = f'{self.domain}_brute_result.{self.format}'
                self.path = setting.result_save_dir.joinpath(name)
            # 数据库导出
            if self.export:
                dbexport.export(self.domain,
                                alive=self.alive,
                                limit='resolve',
                                path=self.path,
                                format=self.format)


if __name__ == '__main__':
    fire.Fire(Brute)
