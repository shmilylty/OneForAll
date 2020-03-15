#!/usr/bin/python3
# coding=utf-8

"""
OneForAll多进程多协程异步子域爆破模块

:copyright: Copyright (c) 2019, Jing Ling. All rights reserved.
:license: GNU General Public License v3.0, see LICENSE for more details.
"""

import time
import queue
import asyncio
import secrets

import exrex
import fire

import config
import dbexport
from common import resolve, utils
from common.module import Module
from common.database import Database
from config import logger


def detect_wildcard(domain):
    """
    探测域名是否使用泛解析

    :param str domain: 域名
    :return: 如果没有使用泛解析返回False 反之返回泛解析的IP集合和ttl整型值
    """
    logger.log('INFOR', f'正在探测{domain}是否使用泛解析')
    token = secrets.token_hex(4)
    random_subdomain = f'{token}.{domain}'
    try:
        resolver = resolve.dns_resolver()
        answers = resolver.query(random_subdomain, 'A')
    # 如果查询随机域名A记录出错 说明不存在随机子域的A记录 即没有开启泛解析
    except Exception as e:
        logger.log('DEBUG', e)
        logger.log('INFOR', f'{domain}没有使用泛解析')
        return False, None, None
    ttl = answers.ttl
    name = answers.name
    ips = {item.address for item in answers}
    logger.log('ALERT', f'{domain}使用了泛解析')
    logger.log('ALERT', f'{random_subdomain} 解析到域名: {name} '
                        f'IP: {ips} TTL: {ttl}')
    return True, ips, ttl


def wildcard_by_compare(ips, ttl, wildcard_ips, wildcard_ttl):
    """
    通过与泛解析返回的IP集合和返回的TTL值进行对比判断发现的子域是否是泛解析子域

    :param set ips: 子域A记录查询出的IP集合
    :param int ttl: 子域A记录查询出的TTL整型值
    :param set wildcard_ips: 泛解析的IP集合
    :param int wildcard_ttl: 泛解析的TTL整型值
    :return: 判断结果
    :rtype bool
    """
    # 参考：http://sh3ll.me/archives/201704041222.txt
    if not ips.issubset(wildcard_ips):
        return False
    if ttl != wildcard_ttl and ttl % 60 == 0 and wildcard_ttl % 60 == 0:
        return False
    return True


def wildcard_by_times(ips, ips_times):
    """
    对ips出现次数进行判断泛解析

    :param set ips: 发现子域的IP集合
    :param ips_times: 子域IP集合出现次数统计字典
    :return: 判断结果
    """
    times = ips_times.get(str(ips))
    if times > config.ips_appear_maximum:
        return True
    return False


def gen_fuzz_domains(domain, rule):
    """
    生成fuzz模式下即将用于爆破的子域集合

    :param str domain: 待爆破的主域
    :param str rule: 用于爆破的正则规则
    :return: 用于爆破的子域集合
    """
    domains = set()
    if '[fuzz]' not in domain:
        logger.log('FATAL', f'没有指定fuzz位置')
        return domains
    if not rule:
        logger.log('FATAL', f'没有指定fuzz规则')
        return domains
    fuzz_count = exrex.count(rule)
    if fuzz_count > 2000000:
        logger.log('FATAL', f'fuzz规则范围太大：{fuzz_count} > 2000000')
        return domains
    logger.log('INFOR', f'fuzz字典大小：{fuzz_count}')
    for i in range(3):
        random_domain = domain.replace('[fuzz]', exrex.getone(rule))
        logger.log('ALERT', f'请注意检查随机生成的{random_domain}是否正确')
    logger.log('ALERT', f'你有6秒检查时间退出使用`CTRL+C`')
    try:
        time.sleep(6)
    except KeyboardInterrupt:
        logger.log('INFOR', '爆破终止')
        exit(0)
    parts = domain.split('[fuzz]')
    for fuzz in exrex.generate(rule):
        fuzz_domain = parts[0] + fuzz + parts[1]
        domains.add(fuzz_domain)
    return domains


def gen_brute_domains(domain, path):
    """
    生成基于字典爆破的子域数据

    :param str domain: 待爆破的主域
    :param str path: 字典路径
    :return: 用于爆破的子域集合
    """
    domains = set()
    with open(path, encoding='utf-8', errors='ignore') as file:
        for line in file:
            brute_domain = line.strip() + '.' + domain
            domains.add(brute_domain)
    logger.log('INFOR', f'爆破字典大小：{len(domains)}')
    return domains


class AIOBrute(Module):
    """
    OneForAll多进程多协程异步子域爆破模块

    Example：
        python3 aiobrute.py --target subdomain.com run
        python3 aiobrute.py --target ./subdomains.txt run
        python3 aiobrute.py --target example.com --process 4 --coroutine 64 run
        python3 aiobrute.py --target example.com --wordlist subnames.txt run
        python3 aiobrute.py --target example.com --recursive True --depth 2 run
        python3 aiobrute.py --target m.[fuzz].bz --fuzz True --rule '[a-z]' run

    Note:
        参数segment的设置受CPU性能，网络带宽，运营商限制等限制，默认500个子域为任务组，
        当你的环境不受以上因素影响，当前爆破速度较慢，那么强烈建议根据字典大小调整大小：
        十万字典建议设置为5000，百万字典设置为50000
        参数valid可选值1，0，None，分别表示导出有效，无效，全部子域
        参数format可选格式有'txt', 'rst', 'csv', 'tsv', 'json', 'yaml', 'html',
                          'jira', 'xls', 'xlsx', 'dbf', 'latex', 'ods'
        参数path默认None使用OneForAll结果目录自动生成路径

    :param str target:       单个域名或者每行一个域名的文件路径
    :param int process:      爆破的进程数(默认CPU核心数)
    :param int coroutine:    每个爆破进程下的协程数(默认64)
    :param str wordlist:     指定爆破所使用的字典路径(默认使用config.py配置)
    :param bool recursive:   是否使用递归爆破(默认False)
    :param int depth:        递归爆破的深度(默认2)
    :param str namelist:     指定递归爆破所使用的字典路径(默认使用config.py配置)
    :param bool fuzz:        是否使用fuzz模式进行爆破(默认False，开启须指定fuzz正则规则)
    :param str rule:         fuzz模式使用的正则规则(默认使用config.py配置)
    :param bool export:      是否导出爆破结果(默认True)
    :param bool valid:       只导出有效的子域结果(默认False)
    :param str format:       导出格式(默认csv)
    :param str path:         导出路径(默认None)
    :param bool show:        终端显示导出数据(默认False)
    """

    def __init__(self, target, process=None, coroutine=None, wordlist=None,
                 recursive=False, depth=None, namelist=None, fuzz=False,
                 rule=None, export=True, valid=None, format='csv', path=None,
                 show=False):
        Module.__init__(self)
        self.domains = set()
        self.domain = str()
        self.module = 'Brute'
        self.source = 'AIOBrute'
        self.target = target
        self.process = process or utils.get_process_num()
        self.coroutine = coroutine or utils.get_coroutine_num()
        self.wordlist = wordlist or config.brute_wordlist_path
        self.recursive_brute = recursive or config.enable_recursive_brute
        self.recursive_depth = depth or config.brute_recursive_depth
        self.recursive_namelist = namelist or config.recursive_namelist_path
        self.fuzz = fuzz or config.enable_fuzz
        self.rule = rule or config.fuzz_rule
        self.export = export
        self.valid = valid
        self.format = format
        self.path = path
        self.show = show
        self.nameservers = config.resolver_nameservers
        self.ips_times = dict()  # IP集合出现次数
        self.enable_wildcard = False  # 当前域名是否使用泛解析
        self.wildcard_check = config.enable_wildcard_check
        self.wildcard_deal = config.enable_wildcard_deal
        self.wildcard_ips = set()  # 泛解析IP集合
        self.wildcard_ttl = int()  # 泛解析TTL整型值

    def gen_tasks(self, domain):
        # 如果domain不是self.subdomain，而是self.domain的子域 生成递归爆破字典
        if self.domain != domain:
            logger.log('INFOR', f'使用{self.recursive_namelist}字典')
            domains = gen_brute_domains(domain, self.recursive_namelist)
        elif self.fuzz and self.rule:  # 开启fuzz模式并指定了fuzz正则规则
            logger.log('INFOR', f'正在生成{domain}的fuzz字典')
            domains = gen_fuzz_domains(domain, self.rule)
        else:
            logger.log('INFOR', f'使用{self.wordlist}字典')
            domains = gen_brute_domains(domain, self.wordlist)
        domains = list(domains)
        return domains

    def deal_results(self, results):
        for result in results:
            hostname, answer = result
            if answer is None:
                continue
            if isinstance(answer, Exception):
                # logger.log('DEBUG', f'爆破{subdomain}时出错 {str(answers)}')
                continue
            name, alias, ips = answer
            if name.endswith('.'):
                name = name[0:-1]
            # 取值 如果是首次出现的IP集合 出现次数先赋值0
            value = self.ips_times.setdefault(str(ips), 0)
            self.ips_times[str(ips)] = value + 1
            # 目前域名开启了泛解析
            if self.enable_wildcard and self.wildcard_deal:
                # 通过对比查询的子域和响应的子域来判断真实子域
                # 去掉解析到CDN的情况
                if 'cdn' in name or 'waf' in name:
                    continue
                if not name.endswith(self.domain):
                    continue
                # 通过对比解析到的IP集合的次数来判断真实子域
                if wildcard_by_times(ips, self.ips_times):
                    continue
            # 只添加没有出现过的子域
            if hostname not in self.subdomains:
                logger.log('INFOR', f'发现{self.domain}的子域: {hostname} '
                                    f'解析到: {name} IP: {ips}')
                self.subdomains.add(hostname)
                self.records[hostname] = ','.join(ips)

    async def main(self, domain, rx_queue):
        if not self.fuzz:  # fuzz模式不探测域名是否使用泛解析
            if self.wildcard_check:
                self.enable_wildcard, self.wildcard_ips, self.wildcard_ttl \
                    = detect_wildcard(domain)
        tasks = self.gen_tasks(domain)
        logger.log('INFOR', f'正在爆破{domain}的域名')
        results = await resolve.aio_resolve(tasks, self.process, self.coroutine)
        self.deal_results(results)
        self.save_json()
        self.gen_result()
        rx_queue.put(self.results)

    def run(self, rx_queue=None):
        self.domains = utils.get_domains(self.target)
        loop = asyncio.get_event_loop()
        asyncio.set_event_loop(loop)
        for self.domain in self.domains:
            start = time.time()
            db = Database()
            db.create_table(self.domain)
            if not rx_queue:
                rx_queue = queue.Queue()
            logger.log('INFOR', f'开始执行{self.source}模块爆破域名{self.domain}')
            logger.log('INFOR', f'使用{self.process}进程乘{self.coroutine}协程')
            # fuzz模式不使用递归爆破
            if self.recursive_brute and not self.fuzz:
                logger.log('INFOR', f'开始递归爆破{self.domain}的第1层子域')
            loop.run_until_complete(self.main(self.domain, rx_queue))

            # 递归爆破下一层的子域
            # fuzz模式不使用递归爆破
            if self.recursive_brute and not self.fuzz:
                for layer_num in range(1, self.recursive_depth):
                    # 之前已经做过1层子域爆破 当前实际递归层数是layer+1
                    logger.log('INFOR', f'开始递归爆破{self.domain}的'
                                        f'第{layer_num + 1}层子域')
                    for subdomain in self.subdomains.copy():
                        # 进行下一层子域爆破的限制条件
                        if subdomain.count('.') - self.domain.count('.') \
                                == layer_num:
                            loop.run_until_complete(self.main(subdomain,
                                                              rx_queue))
            # 队列不空就一直取数据存数据库
            while not rx_queue.empty():
                results = rx_queue.get()
                # 将结果存入数据库中
                db.save_db(self.domain, results, self.source)

            end = time.time()
            self.elapse = round(end - start, 1)
            logger.log('INFOR', f'结束执行{self.source}模块爆破域名{self.domain}')
            length = len(self.subdomains)
            logger.log('INFOR', f'{self.source}模块耗时{self.elapse}秒'
                                f'发现{self.domain}的域名{length}个')
            logger.log('DEBUG', f'{self.source}模块发现{self.domain}的域名:\n'
                                f'{self.subdomains}')
            if not self.path:
                name = f'{self.domain}_brute_result.{self.format}'
                self.path = config.result_save_dir.joinpath(name)
            # 数据库导出
            if self.export:
                dbexport.export(self.domain,
                                valid=self.valid,
                                path=self.path,
                                format=self.format,
                                show=self.show)


if __name__ == '__main__':
    fire.Fire(AIOBrute)
    # domain = 'example.com'
    # result = queue.Queue()
    # brute = AIOBrute(domain)
    # brute.run(result)
