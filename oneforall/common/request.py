import asyncio
import functools

import aiohttp
import tqdm
from aiohttp import ClientSession
from bs4 import BeautifulSoup
import config
from common import utils
from config import logger


def get_limit_conn():
    limit_open_conn = config.limit_open_conn
    if limit_open_conn is None:  # 默认情况
        limit_open_conn = utils.get_semaphore()
    elif not isinstance(limit_open_conn, int):  # 如果传入不是数字的情况
        limit_open_conn = utils.get_semaphore()
    return limit_open_conn


def get_ports(port):
    logger.log('DEBUG', f'正在获取请求探测端口范围')
    ports = set()
    if isinstance(port, (set, list, tuple)):
        ports = port
    elif isinstance(port, int):
        if 0 <= port <= 65535:
            ports = {port}
    elif port in {'default', 'small', 'large'}:
        logger.log('DEBUG', f'探测{port}等端口范围')
        ports = config.ports.get(port)
    if not ports:  # 意外情况
        logger.log('ERROR', f'指定探测端口范围有误')
        ports = {80}
    logger.log('INFOR', f'探测端口范围：{ports}')
    return set(ports)


def gen_new_datas(datas, ports):
    logger.log('INFOR', f'正在生成请求地址')
    new_datas = []
    protocols = ['http://', 'https://']
    for data in datas:
        valid = data.get('valid')
        if valid is None:  # 子域有效性未知的才进行http请求探测
            subdomain = data.get('subdomain')
            for port in ports:
                if str(port).endswith('443'):
                    url = f'https://{subdomain}:{port}'
                    data['id'] = None
                    data['url'] = url
                    data['port'] = port
                    new_datas.append(data)
                    data = dict(data)  # 需要生成一个新的字典对象
                else:
                    url = f'http://{subdomain}:{port}'
                    data['id'] = None
                    data['url'] = url
                    data['port'] = port
                    new_datas.append(data)
                    data = dict(data)  # 需要生成一个新的字典对象
    return new_datas


async def fetch(session, url):
    """
    请求

    :param session: session对象
    :param url: url地址
    :return: 响应对象和响应文本
    """
    timeout = aiohttp.ClientTimeout(total=None,
                                    connect=None,
                                    sock_read=config.sockread_timeout,
                                    sock_connect=config.sockconn_timeout)
    try:
        async with session.get(url,
                               ssl=config.verify_ssl,
                               allow_redirects=config.allow_redirects,
                               timeout=timeout,
                               proxy=config.aiohttp_proxy) as resp:

            try:
                # 先尝试用utf-8解码
                text = await resp.text(encoding='utf-8', errors='replace')
            except UnicodeError:
                text = await resp.text(encoding='gb18030', errors='replace')
        return resp, text
    except Exception as e:
        return e


def get_title(markup):
    """
    获取标题

    :param markup: html标签
    :return: 标题
    """
    soup = BeautifulSoup(markup, 'lxml')

    title = soup.title
    if title:
        return title.text

    h1 = soup.h1
    if h1:
        return h1.text

    h2 = soup.h2
    if h2:
        return h2.text

    h3 = soup.h3
    if h2:
        return h3.text

    desc = soup.find('meta', attrs={'name': 'description'})
    if desc:
        return desc['content']

    word = soup.find('meta', attrs={'name': 'keywords'})
    if word:
        return word['content']

    text = soup.text
    if len(text) <= 200:
        return text

    return 'None'


def request_callback(future, index, datas):
    result = future.result()
    if isinstance(result, BaseException):
        logger.log('TRACE', result.args)
        name = utils.get_classname(result)
        datas[index]['reason'] = name + ' ' + str(result)
        datas[index]['valid'] = 0
    elif isinstance(result, tuple):
        resp, text = result
        datas[index]['reason'] = resp.reason
        datas[index]['status'] = resp.status
        if resp.status == 400 or resp.status >= 500:
            datas[index]['valid'] = 0
        else:
            datas[index]['valid'] = 1
            headers = resp.headers
            banner = str({'Server': headers.get('Server'),
                          'Via': headers.get('Via'),
                          'X-Powered-By': headers.get('X-Powered-By')})
            datas[index]['banner'] = banner[1:-1]
            title = get_title(text).strip()
            datas[index]['title'] = utils.remove_string(title)
            datas[index]['header'] = str(dict(headers))[1:-1]
            datas[index]['response'] = utils.remove_string(text)


def get_connector():
    limit_open_conn = get_limit_conn()
    return aiohttp.TCPConnector(ttl_dns_cache=300,
                                ssl=config.verify_ssl,
                                limit=limit_open_conn,
                                limit_per_host=config.limit_per_host)


def get_header():
    header = None
    if config.fake_header:
        header = utils.gen_fake_header()
    return header


async def bulk_get_request(datas, port):
    ports = get_ports(port)
    new_datas = gen_new_datas(datas, ports)
    logger.log('INFOR', f'正在异步进行子域的GET请求')
    connector = get_connector()
    header = get_header()
    async with ClientSession(connector=connector, headers=header) as session:
        tasks = []
        for i, data in enumerate(new_datas):
            url = data.get('url')
            task = asyncio.ensure_future(fetch(session, url))
            task.add_done_callback(functools.partial(request_callback,
                                                     index=i,
                                                     datas=new_datas))
            tasks.append(task)
        # 任务列表里有任务不空时才进行解析
        if tasks:
            # 等待所有task完成 错误聚合到结果列表里
            futures = asyncio.as_completed(tasks)
            for future in tqdm.tqdm(futures,
                                    total=len(tasks),
                                    desc='Progress',
                                    ncols=60):
                await future

    logger.log('INFOR', f'完成异步进行子域的GET请求')
    return new_datas


def run_bulk_query(datas, port):
    new_datas = asyncio.run(bulk_get_request(datas, port))
    return new_datas
