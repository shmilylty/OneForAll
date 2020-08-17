import json
import asyncio
import functools

import aiohttp
import tqdm
from aiohttp import ClientSession
from bs4 import BeautifulSoup

from common import utils
from config.log import logger
from config import settings


def get_limit_conn():
    count = settings.limit_open_conn
    if isinstance(count, int):
        count = max(16, count)
    else:
        count = utils.get_coroutine_count()
    logger.log('DEBUG', f'Request coroutine {count}')
    return count


def get_ports(port):
    logger.log('DEBUG', 'Getting port range')
    ports = set()
    if isinstance(port, (set, list, tuple)):
        ports = port
    elif isinstance(port, int):
        if 0 <= port <= 65535:
            ports = {port}
    elif port in {'small', 'medium', 'large'}:
        logger.log('DEBUG', f'{port} port range')
        ports = settings.ports.get(port)
    if not ports:  # 意外情况
        logger.log('ERROR', 'The specified request port range is incorrect')
        ports = {80}
    logger.log('INFOR', f'Port range:{ports}')
    return set(ports)


def gen_req_data(data, ports):
    logger.log('INFOR', 'Generating request urls')
    new_data = []
    for data in data:
        resolve = data.get('resolve')
        # 解析不成功的子域不进行http请求探测
        if resolve != 1:
            continue
        subdomain = data.get('subdomain')
        for port in ports:
            if str(port).endswith('443'):
                url = f'https://{subdomain}:{port}'
                if port == 443:
                    url = f'https://{subdomain}'
                data['id'] = None
                data['url'] = url
                data['port'] = port
                new_data.append(data)
                data = dict(data)  # 需要生成一个新的字典对象
            else:
                url = f'http://{subdomain}:{port}'
                if port == 80:
                    url = f'http://{subdomain}'
                data['id'] = None
                data['url'] = url
                data['port'] = port
                new_data.append(data)
                data = dict(data)  # 需要生成一个新的字典对象
    return new_data


async def fetch(session, method, url):
    """
    请求

    :param session: session对象
    :param method: 请求方法
    :param str url: url地址
    :return: 响应对象和响应文本
    """
    timeout = aiohttp.ClientTimeout(total=None,
                                    connect=5.0,
                                    sock_read=settings.sockread_timeout,
                                    sock_connect=settings.sockconn_timeout)
    try:
        if method == 'HEAD':
            async with session.head(url,
                                    ssl=settings.verify_ssl,
                                    allow_redirects=settings.allow_redirects,
                                    timeout=timeout,
                                    proxy=settings.aiohttp_proxy) as resp:
                text = await resp.text()
        else:
            async with session.get(url,
                                   ssl=settings.verify_ssl,
                                   allow_redirects=settings.allow_redirects,
                                   timeout=timeout,
                                   proxy=settings.aiohttp_proxy) as resp:

                try:
                    # 先尝试用utf-8解码
                    text = await resp.text(encoding='utf-8', errors='strict')
                except UnicodeError:
                    try:
                        # 再尝试用gb18030解码
                        text = await resp.text(encoding='gb18030', errors='strict')
                    except UnicodeError:
                        # 最后尝试自动解码
                        text = await resp.text(encoding=None, errors='ignore')
        return resp, text
    except Exception as e:
        return e, None


def get_title(markup):
    """
    获取标题

    :param markup: html标签
    :return: 标题
    """
    soup = BeautifulSoup(markup, 'html.parser')

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
        return repr(text)

    return 'None'


def request_callback(future, index, datas):
    resp, text = future.result()
    if isinstance(resp, BaseException):
        exception = resp
        logger.log('TRACE', exception.args)
        name = utils.get_classname(exception)
        datas[index]['reason'] = name + ' ' + str(exception)
        datas[index]['request'] = 0
        datas[index]['alive'] = 0
    else:
        datas[index]['reason'] = resp.reason
        datas[index]['status'] = resp.status
        datas[index]['request'] = 1
        if resp.status == 400 or resp.status >= 500:
            datas[index]['alive'] = 0
        else:
            datas[index]['alive'] = 1
        headers = resp.headers
        # 采用webanalyzer的指纹识别 原banner识别弃用
        # datas[index]['banner'] = utils.get_sample_banner(headers)
        datas[index]['header'] = json.dumps(dict(headers))
        if isinstance(text, str):
            title = get_title(text).strip()
            datas[index]['title'] = utils.remove_invalid_string(title)
            datas[index]['response'] = utils.remove_invalid_string(text)


def get_connector():
    count = get_limit_conn()
    return aiohttp.TCPConnector(ttl_dns_cache=300,
                                ssl=settings.verify_ssl,
                                limit=count,
                                limit_per_host=settings.limit_per_host)


async def async_request(urls):
    results = list()
    connector = get_connector()
    headers = utils.get_random_header()
    session = ClientSession(connector=connector, headers=headers)
    tasks = []
    for i, url in enumerate(urls):
        task = asyncio.ensure_future(fetch(session, 'GET', url))
        tasks.append(task)
    if tasks:
        futures = asyncio.as_completed(tasks)
        for future in tqdm.tqdm(futures,
                                total=len(tasks),
                                desc='Request Progress',
                                ncols=80):
            result = await future
            results.append(result)
    await session.close()
    return results


async def bulk_request(data, port):
    ports = get_ports(port)
    no_req_data = utils.get_filtered_data(data)
    to_req_data = gen_req_data(data, ports)
    method = settings.request_method.upper()
    logger.log('INFOR', f'Use {method} method to request')
    logger.log('INFOR', 'Async subdomains request in progress')
    connector = get_connector()
    headers = utils.get_random_header()
    session = ClientSession(connector=connector, headers=headers)
    tasks = []
    for num, data in enumerate(to_req_data):
        url = data.get('url')
        task = asyncio.ensure_future(fetch(session, method, url))
        task.add_done_callback(functools.partial(request_callback,
                                                 index=num,
                                                 datas=to_req_data))
        tasks.append(task)
    if tasks:
        futures = asyncio.as_completed(tasks, timeout=1*60)
        for future in tqdm.tqdm(futures,
                                total=len(tasks),
                                desc='Request Progress',
                                ncols=80):
            await future
    await session.close()
    return to_req_data + no_req_data


def set_loop_policy():
    try:
        import uvloop
    except ImportError:
        pass
    else:
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


def set_loop():
    set_loop_policy()
    loop = asyncio.get_event_loop()
    asyncio.set_event_loop(loop)
    return loop


def run_request(domain, data, port):
    """
    HTTP request entrance

    :param  str domain: domain to be requested
    :param  list data: subdomains data to be requested
    :param  any port: range of ports to be requested
    :return list: result
    """
    logger.log('INFOR', f'Start requesting subdomains of {domain}')
    loop = set_loop()
    data = utils.set_id_none(data)
    request_coroutine = bulk_request(data, port)
    data = loop.run_until_complete(request_coroutine)
    loop.run_until_complete(asyncio.sleep(0.25))
    count = utils.count_alive(data)
    logger.log('INFOR', f'Found that {domain} has {count} alive subdomains')
    return data


def urls_request(urls):
    logger.log('INFOR', 'Start urls request module')
    loop = set_loop()
    request_coroutine = async_request(urls)
    data = loop.run_until_complete(request_coroutine)
    loop.run_until_complete(asyncio.sleep(0.25))
    return data


def save_db(name, data):
    """
    Save request results to database

    :param str  name: table name
    :param list data: data to be saved
    """
    logger.log('INFOR', f'Saving requested results')
    utils.save_db(name, data, 'request')
