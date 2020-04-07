import socket
import asyncio
import functools
import sys
from multiprocessing import Manager

import tqdm
import aiomultiprocess as aiomp
from dns.resolver import Resolver

import config
from config import logger
from common import utils
from common.database import Database

socket.setdefaulttimeout(20)


def dns_resolver():
    """
    dns解析器
    """
    resolver = Resolver()
    resolver.nameservers = config.resolver_nameservers
    resolver.timeout = config.resolver_timeout
    resolver.lifetime = config.resolver_lifetime
    return resolver


async def aio_resolve_a(hostname, loop=None):
    """
    异步解析A记录

    :param str hostname: 主机名
    :param loop: 事件循环
    :return: 查询结果
    """
    if loop is None:
        loop = asyncio.get_event_loop()
    try:
        answer = await loop.run_in_executor(None,
                                            socket.gethostbyname_ex,
                                            hostname)
    except BaseException as e:
        logger.log('TRACE', e.args)
        answer = e
    return hostname, answer


def convert_results(result_list):
    """
    将结果列表类型转换为结果字典类型

    :param result_list: 待转换的结果列表
    :return: 转换后的结果字典
    """
    result_dict = {}
    for result in result_list:
        hostname, answer = result
        value_dict = {'content': None, 'reason': None, 'resolve': None,
                      'public': None, 'valid': None}
        if isinstance(answer, tuple):
            ip_list = answer[2]
            value_dict['content'] = ','.join(ip_list)
            value_dict['public'] = utils.check_ip_public(ip_list)
            value_dict['resolve'] = 1
            result_dict[hostname] = value_dict
        elif isinstance(answer, Exception):
            value_dict['reason'] = str(answer.args)
            value_dict['resolve'] = 0
            result_dict[hostname] = value_dict
        else:
            value_dict['resolve'] = 0
            result_dict[hostname] = value_dict
    return result_dict


def filter_subdomain(data_list):
    """
    过滤出无解析内容的子域到新的子域列表

    :param list data_list: 待过滤的数据列表
    :return: 符合条件的子域列表
    """
    subdomains = []
    for data in data_list:
        if not data.get('content'):
            subdomain = data.get('subdomain')
            subdomains.append(subdomain)
    return subdomains


def update_data(data_list, results_dict):
    """
    更新解析结果

    :param list data_list: 待更新的数据列表
    :param dict results_dict: 解析结果字典
    :return: 更新后的数据列表
    """
    for index, data in enumerate(data_list):
        if not data.get('content'):
            subdomain = data.get('subdomain')
            value_dict = results_dict.get(subdomain)
            data.update(value_dict)
            data_list[index] = data
    return data_list


def save_data(name, data):
    """
    保存解析结果到数据库

    :param str name: 保存表名
    :param list data: 待保存的数据
    """
    db = Database()
    db.drop_table(name)
    db.create_table(name)
    db.save_db(name, data, 'resolve')
    db.close()


def resolve_progress_func(done_obj, total_num):
    """
    解析进度函数

    :param done_obj: 进程间共享的Value对象
    :param int total_num: 待解析的子域个数
    """
    bar = tqdm.tqdm()
    bar.total = total_num
    bar.desc = 'Resolve Progress'
    bar.ncols = 80
    bar.smoothing = 0
    while True:
        done_num = done_obj.value
        bar.n = done_num
        bar.update()
        if done_num == total_num:
            break
    bar.close()


async def do_resolve(done_obj, hostname):
    """
    异步解析主机名的A记录

    :param done_obj: 进程间共享的Value对象
    :param str hostname: 主机名
    :return: 查询结果
    """
    loop = asyncio.get_event_loop()
    result = await aio_resolve_a(hostname, loop)
    done_obj.value += 1
    return result


async def aio_resolve(subdomain_list, process_num, coroutine_num):
    """
    异步解析子域A记录

    :param list subdomain_list: 待解析的子域列表
    :param int process_num: 解析进程数
    :param int coroutine_num: 每个解析进程下的协程数
    :return: 解析结果
    """
    m = Manager()
    done_obj = m.Value('done', 0)  # 创建一个进程间可以共享的值
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, resolve_progress_func,
                         done_obj, len(subdomain_list))
    wrapped_resolve_func = functools.partial(do_resolve, done_obj)
    result_list = list()
    # macOS上队列大小不能超过2**15 - 1 = 32767
    # https://stackoverflow.com/questions/5900985/multiprocessing-queue-maxsize-limit-is-32767
    if sys.platform == 'darwin':
        split_subdomain_list = utils.split_list(subdomain_list, 32767)
        for current_subdomain_list in split_subdomain_list:
            async with aiomp.Pool(processes=process_num,
                                  childconcurrency=coroutine_num) as pool:
                result = await pool.map(wrapped_resolve_func,
                                        current_subdomain_list)
                result_list.extend(result)
        return result_list
    async with aiomp.Pool(processes=process_num,
                          childconcurrency=coroutine_num) as pool:
        result_list = await pool.map(wrapped_resolve_func, subdomain_list)
        return result_list


async def run_aio_resolve(subdomain_list):
    """
    异步解析子域A记录

    :param list subdomain_list: 待解析的子域列表
    :return: 解析得到的结果列表
    """
    process_num = utils.get_process_num()
    coroutine_num = utils.get_coroutine_num()
    logger.log('INFOR', '正在异步查询子域的A记录')
    result_list = await aio_resolve(subdomain_list, process_num, coroutine_num)
    logger.log('INFOR', '完成异步查询子域的A记录')
    return result_list


def run_resolve(data):
    """
    调用子域解析入口函数

    :param list data: 待解析的子域数据列表
    :return: 解析得到的结果列表
    :rtype: list
    """
    loop = asyncio.get_event_loop()
    asyncio.set_event_loop(loop)
    need_resolve_subdomains = filter_subdomain(data)
    if not need_resolve_subdomains:
        return data
    resolve_coroutine = run_aio_resolve(need_resolve_subdomains)
    results_list = loop.run_until_complete(resolve_coroutine)
    results_dict = convert_results(results_list)
    resolved_data = update_data(data, results_dict)
    return resolved_data
