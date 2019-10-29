# coding=utf-8
import re
import random
import ipaddress
import platform
import config
from pathlib import Path
from common.domain import Domain
from config import logger

user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/68.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:61.0) '
    'Gecko/20100101 Firefox/68.0',
    'Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/68.0']


def match_subdomain(domain, text, distinct=True):
    """
    匹配text中domain的子域名

    :param str domain: 域名
    :param str text: 响应文本
    :param bool distinct: 结果去重
    :return: 匹配结果
    :rtype: set or list
    """
    regexp = r'(?:[a-z0-9](?:[a-z0-9\-]{0,61}[a-z0-9])?\.){0,}' \
             + domain.replace('.', r'\.')
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
    ua = random.choice(user_agents)
    ip = gen_random_ip()
    headers = {
        'Accept': 'text/html,application/xhtml+xml,'
                  'application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Referer': 'https://www.google.com/',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': ua,
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
    return [ls[i:i + size] for i in range(0, len(ls), size)]


def get_domains(target):
    """
    获取域名

    :param set or str target:
    :return: 域名集合
    """
    domains = list()
    logger.log('DEBUG', f'正在获取域名')
    if isinstance(target, (set, tuple)):
        domains = list(target)
    elif isinstance(target, list):
        domains = target
    elif isinstance(target, str):
        path = Path(target)
        if path.is_file():
            with open(target) as file:
                for line in file:
                    domain = Domain(line.strip()).match()
                    if domain:
                        domains.append(domain)
        elif Domain(target).match():
            domains = [target]
    logger.log('INFOR', f'获取到{len(domains)}个域名')
    return domains


def get_semaphore():
    """
    获取查询并发值

    :return: 并发整型值
    """
    system = platform.system()
    if system == 'Windows':
        return 800
    elif system == 'Linux':
        return 800
    elif system == 'Darwin':
        return 800


def check_dpath(dpath):
    """
    检查目录路径

    :param dpath: 传入的目录路径
    :return: 目录路径
    """
    if isinstance(dpath, str):
        dpath = Path(dpath)
    else:
        dpath = config.result_save_path
    if not dpath.is_dir():
        logger.log('FATAL', f'{dpath}不是目录')
    if not dpath.exists():
        logger.log('ALERT', f'不存在{dpath}将会新建此目录')
        dpath.mkdir(parents=True, exist_ok=True)
    return dpath


def check_format(format):
    """
    检查导出格式

    :param format: 传入的导出格式
    :return: 导出格式
    """
    formats = ['txt', 'rst', 'csv', 'tsv', 'json', 'yaml', 'html',
               'jira', 'xls', 'xlsx', 'dbf', 'latex', 'ods']
    if format in formats:
        return format
    else:
        logger.log('ALERT', f'不支持{format}格式导出')
        logger.log('ALERT', '默认使用csv格式导出')
        return 'xls'


def save_data(fpath, data):
    try:
        with open(fpath, 'w', encoding="utf-8", newline='') as file:
            file.write(data)
            logger.log('ALERT', fpath)
    except TypeError:
        with open(fpath, 'wb') as file:
            file.write(data)
            logger.log('ALERT', fpath)
    except Exception as e:
        logger.log('ERROR', e)


def check_response(method, resp):
    if resp.status_code == 200 and resp.content:
        return True
    logger.log('ALERT', f'{method} {resp.url} {resp.status_code} - '
                        f'{resp.reason} {len(resp.content)}')
    content_type = resp.headers.get('Content-Type')
    if content_type and 'json' in content_type and resp.content:
        try:
            msg = resp.json()
        except Exception as e:
            logger.log('DEBUG', e.args)
        else:
            logger.log('ALERT', msg)
    return False


def mark_subdomain(old_data, new_data):
    """
    标记新增子域并返回新的数据集

    :param old_data: 之前数据集
    :param new_data: 现在数据集
    :return: 已标记的新的数据集
    """
    # 第一次收集子域的情况
    if not old_data:
        for index, item in enumerate(new_data):
            item['new'] = 1
            new_data[index] = item
        return new_data
    # 非第一次收集子域的情况
    old_subdomains = {item.get('subdomain') for item in old_data}
    for index, item in enumerate(new_data):
        subdomain = item.get('subdomain')
        if subdomain in old_subdomains:
            item['new'] = 0
        else:
            item['new'] = 1
        new_data[index] = item
    return new_data
