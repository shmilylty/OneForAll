# coding=utf-8

import asyncio
import functools
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
    protocols = ['http://', 'https://']
    for data in datas:
        if data.get('valid'):  # 有效的子域才进行http请求探测
            subdomain = data.get('subdomain')
            for port in ports:
                for protocol in protocols:
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
    :param semaphore: 同步对象(控制并发量)
    :return: 响应对象和响应文本
    """
    timeout = aiohttp.ClientTimeout(total=config.get_timeout)
    async with semaphore:
        async with session.get(url, allow_redirects=config.get_redirects,
                               timeout=timeout, proxy=config.get_proxy) as resp:
            text = await resp.text()
            return resp, text


def request_callback(future, index, datas):
    try:
        resp, text = future.result()
    except Exception as e:
        logger.log('DEBUG', e.args)
        datas[index]['reason'] = str(e.args)
        datas[index]['valid'] = 0
    else:
        datas[index]['reason'] = resp.reason
        datas[index]['status'] = resp.status
        if resp.status == 400 or resp.status >= 500:
            datas[index]['valid'] = 0
        else:
            headers = resp.headers
            banner = str({'Server': headers.get('Server'), 'Via': headers.get('Via'),
                          'X-Powered-By': headers.get('X-Powered-By')})
            datas[index]['banner'] = banner
            soup = BeautifulSoup(text, 'lxml')
            title = soup.title
            head = soup.head
            if title:
                datas[index]['title'] = title.text
            elif head:
                datas[index]['title'] = head.text
            else:
                datas[index]['title'] = text


async def bulk_get_request(datas, port):
    logger.log('INFOR', f'正在异步进行子域的GET请求')
    ports = get_ports(port)
    new_datas = gen_new_datas(datas, ports)
    header = None
    if config.fake_header:
        header = utils.gen_fake_header()
    resolver = AsyncResolver(nameservers=config.resolver_nameservers)  # 使用异步域名解析器 自定义域名服务器
    conn = aiohttp.TCPConnector(verify_ssl=config.verify_ssl, ssl=config.verify_ssl, limit=config.limit_open_conn,
                                limit_per_host=config.limit_per_host, resolver=resolver)
    semaphore = asyncio.Semaphore(utils.get_semaphore())
    async with ClientSession(connector=conn, headers=header) as session:
        tasks = []
        for i, data in enumerate(new_datas):
            url = data.get('url')
            task = asyncio.ensure_future(fetch(session, url, semaphore))
            task.add_done_callback(functools.partial(request_callback, index=i, datas=new_datas))
            tasks.append(task)
        if tasks:  # 任务列表里有任务不空时才进行解析
            await asyncio.wait(tasks)  # 等待所有task完成
    logger.log('INFOR', f'完成异步进行子域的GET请求')
    return new_datas
