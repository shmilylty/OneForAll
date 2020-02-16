import signal
import socket
import asyncio
import functools
from multiprocessing import Manager

import tqdm
import aiomultiprocess as aiomp
from dns.resolver import Resolver

import config
from config import logger


def dns_resolver():
    """
    dns解析器
    """
    resolver = Resolver()
    resolver.nameservers = config.resolver_nameservers
    resolver.timeout = config.resolver_timeout
    resolver.lifetime = config.resolver_lifetime
    return resolver


async def aiodns_query_a(hostname):
    """
    异步查询A记录

    :param str hostname: 主机名
    :return: 查询结果
    """
    try:
        loop = asyncio.get_event_loop()
        socket.setdefaulttimeout(20)
        # answer = await loop.getaddrinfo(hostname, 80)
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
        value_dict = {'ips': None, 'reason': None, 'valid': None}
        if isinstance(answer, tuple):
            value_dict['ips'] = str(answer[2])[1:-1]
            result_dict[hostname] = value_dict
        elif isinstance(answer, Exception):
            value_dict['reason'] = str(answer.args)
            value_dict['valid'] = 0
            result_dict[hostname] = value_dict
        else:
            value_dict['valid'] = 0
            result_dict[hostname] = value_dict
    return result_dict


def filter_subdomain(data_list):
    """
    过滤出无IPS值的子域到新的子域列表

    :param list data_list: 待过滤的数据列表
    :return: 符合条件的子域列表
    """
    subdomains = []
    for data in data_list:
        if not data.get('ips'):
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
        if not data.get('ips'):
            subdomain = data.get('subdomain')
            value_dict = results_dict.get(subdomain)
            data.update(value_dict)
            data_list[index] = data
    return data_list


def init_worker():
    signal.signal(signal.SIGINT, signal.SIG_IGN)


def query_progress(pr_queue, total):
    bar = tqdm.tqdm()
    bar.total = total
    bar.desc = 'Resolve Progress'
    bar.ncols = 60
    bar.smoothing = 0
    while True:
        done = pr_queue.qsize()
        bar.n = done
        bar.update()
        if done == total:
            break
    bar.close()


async def aio_query(pr_queue, hostname):
    """
    异步查询主机名的A记录

    :param pr_queue: 进度队列
    :param str hostname: 主机名
    :return: 查询结果
    """
    results = await aiodns_query_a(hostname)
    pr_queue.put(1)
    return results


async def aio_resolve(subdomain_list, process_num, coroutine_num):
    """
    异步解析子域A记录

    :param list subdomain_list: 待解析的子域列表
    :param int process_num: 解析进程数
    :param int coroutine_num: 每个解析进程下的协程数
    :return: 解析结果
    """
    m = Manager()
    pr_queue = m.Queue()
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, query_progress, pr_queue, len(subdomain_list))
    wrapped_query = functools.partial(aio_query, pr_queue)
    async with aiomp.Pool(processes=process_num,
                          initializer=init_worker,
                          childconcurrency=coroutine_num) as pool:
        results = await pool.map(wrapped_query, subdomain_list)
        return results


async def bulk_resolve(data_list):
    """
    批量解析A记录并返回解析结果

    :param list data_list: 待查的数据列表
    :return: 查询过得到的结果列表
    """
    logger.log('INFOR', '正在异步查询子域的A记录')
    # semaphore = asyncio.Semaphore(config.limit_resolve_conn)
    query_subdomains = filter_subdomain(data_list)
    process_num = config.brute_process_num
    coroutine_num = config.brute_coroutine_num
    results = await aio_resolve(query_subdomains, process_num, coroutine_num)
    results_dict = convert_results(results)
    data_list = update_data(data_list, results_dict)
    logger.log('INFOR', '完成异步查询子域的A记录')
    return data_list
