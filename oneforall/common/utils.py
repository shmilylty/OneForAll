# coding=utf-8
import re
import pathlib
import random
import ipaddress
import platform
import config
from fake_useragent import UserAgent
from common.domain import Domain
from config import logger


def match_subdomain(domain, text, distinct=True):
    """
    匹配text中domain的子域名

    :param str domain: 域名
    :param str text: 响应文本
    :param bool distinct: 结果去重
    :return: 匹配结果
    :rtype: set or list
    """
    regexp = r'(?:[a-z0-9](?:[a-z0-9\-]{0,61}[a-z0-9])?\.){0,}' + domain.replace('.', r'\.')
    result = re.findall(regexp, text, re.I)
    if not result:
        return set()
    deal = map(lambda s: s.lower(), result)
    if distinct:
        return set(deal)
    else:
        return list(deal)


def gen_random_ip():
    """
    生成随机的点分十进制的IP字符串
    """
    while True:
        ip = ipaddress.IPv4Address(random.randint(0, 2 ** 32 - 1))
        if ip.is_global:
            return ip.exploded


def gen_fake_header():
    """
    生成伪造请求头
    """
    ua = UserAgent()
    ip = gen_random_ip()
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Referer': 'https://www.google.com/',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': ua.random,
        'X-Forwarded-For': ip,
        'X-Real-IP': ip
    }
    return headers


def get_random_proxy():
    """
    获取随机代理
    """
    try:
        return random.choice(config.proxy_pool)
    except IndexError:
        return None


def split_list(ls, size):
    """
    将ls列表按size大小划分并返回新的划分结果列表

    :param list ls: 要划分的列表
    :param int size: 划分大小
    :return 划分结果

    >>> split_list([1, 2, 3, 4], 3)
    [[1, 2, 3], [4]]
    """
    if size == 0:
        return ls
    return [ls[i:i+size] for i in range(0, len(ls), size)]


def get_domains(target):
    """
    获取域名

    :param set or str target:
    :return: 域名集合
    """
    domains = set()
    logger.log('INFOR', f'正在获取域名')
    if isinstance(target, set):
        domains = target
    elif isinstance(target, str):
        path = pathlib.Path(target)
        if path.is_file():
            with open(target) as file:
                for line in file:
                    domain = Domain(line.strip()).match()
                    if domain:
                        domains.add(domain)
        if Domain(target).match():
            domains = {target}
    logger.log('INFOR', f'获取到{len(domains)}个域名')
    return domains


def get_semaphore():
    """
    获取查询并发值

    :return: 并发整型值
    """
    system = platform.system()
    if system == 'Windows':
        return 500
    elif system == 'Linux':
        return 1000
    elif system == 'Darwin':
        return 1000

