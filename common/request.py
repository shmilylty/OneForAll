import asyncio
import functools

import aiohttp
import tqdm
from aiohttp import ClientSession
from bs4 import BeautifulSoup

from common import utils
from config.log import logger
from config import setting
from common.database import Database


def get_limit_conn():
    limit_open_conn = setting.limit_open_conn
    if limit_open_conn is None:  # 默认情况
        limit_open_conn = utils.get_semaphore()
    elif not isinstance(limit_open_conn, int):  # 如果传入不是数字的情况
        limit_open_conn = utils.get_semaphore()
    return limit_open_conn


def get_ports(port):
    logger.log('DEBUG', f'正在获取请求端口范围')
    ports = set()
    if isinstance(port, (set, list, tuple)):
        ports = port
    elif isinstance(port, int):
        if 0 <= port <= 65535:
            ports = {port}
    elif port in {'default', 'small', 'large'}:
        logger.log('DEBUG', f'请求{port}等端口范围')
        ports = setting.ports.get(port)
    if not ports:  # 意外情况
        logger.log('ERROR', f'指定请求端口范围有误')
        ports = {80}
    logger.log('INFOR', f'请求端口范围：{ports}')
    return set(ports)


def gen_req_data(data, ports):
    logger.log('INFOR', f'正在生成请求地址')
    new_data = []
    for data in data:
        resolve = data.get('resolve')
        # 解析失败(0)的子域不进行http请求探测
        if resolve == 0:
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


async def fetch(session, url):
    """
    请求

    :param session: session对象
    :param str url: url地址
    :return: 响应对象和响应文本
    """
    method = setting.request_method.upper()
    timeout = aiohttp.ClientTimeout(total=None,
                                    connect=None,
                                    sock_read=setting.sockread_timeout,
                                    sock_connect=setting.sockconn_timeout)
    try:
        if method == 'HEAD':
            async with session.head(url,
                                    ssl=setting.verify_ssl,
                                    allow_redirects=setting.allow_redirects,
                                    timeout=timeout,
                                    proxy=setting.aiohttp_proxy) as resp:
                text = await resp.text()
        else:
            async with session.get(url,
                                   ssl=setting.verify_ssl,
                                   allow_redirects=setting.allow_redirects,
                                   timeout=timeout,
                                   proxy=setting.aiohttp_proxy) as resp:

                try:
                    # 先尝试用utf-8解码
                    text = await resp.text(encoding='utf-8', errors='strict')
                except UnicodeError:
                    try:
                        # 再尝试用gb18030解码
                        text = await resp.text(encoding='gb18030',
                                               errors='strict')
                    except UnicodeError:
                        # 最后尝试自动解码
                        text = await resp.text(encoding=None,
                                               errors='ignore')
        return resp, text
    except Exception as e:
        return e


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
        return text

    return 'None'


def request_callback(future, index, datas):
    result = future.result()
    if isinstance(result, BaseException):
        logger.log('TRACE', result.args)
        name = utils.get_classname(result)
        datas[index]['reason'] = name + ' ' + str(result)
        datas[index]['request'] = 0
        datas[index]['alive'] = 0
    elif isinstance(result, tuple):
        resp, text = result
        datas[index]['reason'] = resp.reason
        datas[index]['status'] = resp.status
        if resp.status == 400 or resp.status >= 500:
            datas[index]['request'] = 0
            datas[index]['alive'] = 0
        else:
            datas[index]['request'] = 1
            datas[index]['alive'] = 1
            headers = resp.headers
            datas[index]['banner'] = utils.get_sample_banner(headers)
            datas[index]['header'] = str(dict(headers))[1:-1]
            if isinstance(text, str):
                title = get_title(text).strip()
                datas[index]['title'] = utils.remove_invalid_string(title)
                datas[index]['response'] = utils.remove_invalid_string(text)


def get_connector():
    limit_open_conn = get_limit_conn()
    return aiohttp.TCPConnector(ttl_dns_cache=300,
                                ssl=setting.verify_ssl,
                                limit=limit_open_conn,
                                limit_per_host=setting.limit_per_host)


def get_header():
    header = None
    if setting.fake_header:
        header = utils.gen_fake_header()
    return header


async def bulk_request(data, port):
    ports = get_ports(port)
    no_req_data = utils.get_filtered_data(data)
    to_req_data = gen_req_data(data, ports)
    method = setting.request_method
    logger.log('INFOR', f'请求使用{method}方法')
    logger.log('INFOR', f'正在进行异步子域请求')
    connector = get_connector()
    header = get_header()
    async with ClientSession(connector=connector, headers=header) as session:
        tasks = []
        for i, data in enumerate(to_req_data):
            url = data.get('url')
            task = asyncio.ensure_future(fetch(session, url))
            task.add_done_callback(functools.partial(request_callback,
                                                     index=i,
                                                     datas=to_req_data))
            tasks.append(task)
        # 任务列表里有任务不空时才进行解析
        if tasks:
            # 等待所有task完成 错误聚合到结果列表里
            futures = asyncio.as_completed(tasks)
            for future in tqdm.tqdm(futures,
                                    total=len(tasks),
                                    desc='Request Progress',
                                    ncols=80):
                await future
    return to_req_data + no_req_data


def set_loop_policy():
    try:
        import uvloop
    except ImportError:
        pass
    else:
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


def run_request(domain, data, port):
    """
    调用子域请求入口函数

    :param str domain: 待请求的主域
    :param list data: 待请求的子域数据
    :param str port: 待请求的端口范围
    :return: 请求后得到的结果列表
    :rtype: list
    """
    logger.log('INFOR', f'开始执行子域请求模块')
    set_loop_policy()
    loop = asyncio.get_event_loop()
    asyncio.set_event_loop(loop)
    data = utils.set_id_none(data)
    request_coroutine = bulk_request(data, port)
    data = loop.run_until_complete(request_coroutine)
    # 在关闭事件循环前加入一小段延迟让底层连接得到关闭的缓冲时间
    loop.run_until_complete(asyncio.sleep(0.25))
    count = utils.count_alive(data)
    logger.log('INFOR', f'经验证{domain}存活子域{count}个')
    return data


def save_data(name, data):
    """
    保存请求结果到数据库

    :param str name: 保存表名
    :param list data: 待保存的数据
    """
    db = Database()
    db.drop_table(name)
    db.create_table(name)
    db.save_db(name, data, 'request')
    db.close()
