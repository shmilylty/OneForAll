# coding=utf-8

import asyncio
import aiohttp
from aiohttp import ClientSession
from aiohttp.resolver import AsyncResolver
from bs4 import BeautifulSoup
import config
from common import utils
from config import logger


def get_ports(port):
    logger.log('INFOR', f'正在获取请求端口范围')
    ports = set()
    if isinstance(port, set):
        ports = port
    elif isinstance(port, str):
        if port not in {'small', 'medium', 'large', 'xlarge'}:
            logger.log('ERROR', f'不存在{port}等端口范围')
            port = 'medium'
        ports = config.ports.get(port)
        logger.log('INFOR', f'使用{port}等端口范围')
    if not ports:  # 意外情况 ports_range为空使用使用中等端口范围
        logger.log('ALERT', f'使用medium等端口范围')
        ports = config.ports.get('medium')
    return ports


def gen_new_datas(datas, ports):
    logger.log('INFOR', f'正在生成请求地址')
    new_datas = []
    protocols = ['http://']
    for data in datas:
        valid = data.get('valid')
        if valid is None:  # 子域有效性未知的才进行http请求探测
            subdomain = data.get('subdomain')
            for port in ports:
                for protocol in protocols:
                    if port == 443:
                        url = f'https://{subdomain}:{port}'
                    else:
                        url = f'{protocol}{subdomain}:{port}'
                    data['id'] = None
                    data['url'] = url
                    data['port'] = port
                    new_datas.append(data)
                    data = dict(data)  # 需要生成一个新的字典对象
    return new_datas


async def fetch(session, url, semaphore):
    """
    请求

    :param session: session对象
    :param url: url地址
    :param semaphore: 并发信号量
    :return: 响应对象和响应文本
    """
    timeout = aiohttp.ClientTimeout(total=config.get_timeout)
    async with semaphore:
        async with session.get(url,
                               ssl=config.verify_ssl,
                               allow_redirects=config.get_redirects,
                               timeout=timeout,
                               proxy=config.get_proxy) as resp:
            text = await resp.text()
        return resp, text


def deal_results(datas, results):
    for index, result in enumerate(results):
        if isinstance(result, Exception):
            logger.log('DEBUG', result.args)
            datas[index]['reason'] = str(result.args)
            datas[index]['valid'] = 0
            continue
        if isinstance(result, tuple):
            resp, text = result
            datas[index]['reason'] = resp.reason
            datas[index]['status'] = resp.status
            if resp.status >= 500:
                datas[index]['valid'] = 0
            else:
                datas[index]['valid'] = 1
                headers = resp.headers
                banner = str({'Server': headers.get('Server'),
                              'Via': headers.get('Via'),
                              'X-Powered-By': headers.get('X-Powered-By')})
                datas[index]['banner'] = banner
                soup = BeautifulSoup(text, 'lxml')
                title = soup.title
                head = soup.head
                if title:
                    datas[index]['title'] = title.text
                elif head:
                    datas[index]['title'] = head.text
                elif len(text) <= 200:
                    datas[index]['title'] = text
    return datas


async def bulk_get_request(datas, port):
    ports = get_ports(port)
    new_datas = gen_new_datas(datas, ports)
    logger.log('INFOR', f'正在异步进行子域的GET请求')

    limit_open_conn = config.limit_open_conn
    if not limit_open_conn:
        limit_open_conn = utils.get_semaphore()
    # 使用异步域名解析器 自定义域名服务器
    resolver = AsyncResolver(nameservers=config.resolver_nameservers)
    conn = aiohttp.TCPConnector(ssl=config.verify_ssl,
                                limit=limit_open_conn,
                                limit_per_host=config.limit_per_host,
                                resolver=resolver)

    semaphore = asyncio.Semaphore(limit_open_conn)
    header = None
    if config.fake_header:
        header = utils.gen_fake_header()
    async with ClientSession(connector=conn, headers=header) as session:
        tasks = []
        for i, data in enumerate(new_datas):
            url = data.get('url')
            task = asyncio.ensure_future(fetch(session, url, semaphore))
            tasks.append(task)
        if tasks:  # 任务列表里有任务不空时才进行解析
            # 等待所有task完成 错误聚合到结果列表里
            results = await asyncio.gather(*tasks, return_exceptions=True)
            new_datas = deal_results(new_datas, results)

    logger.log('INFOR', f'完成异步进行子域的GET请求')
    return new_datas
