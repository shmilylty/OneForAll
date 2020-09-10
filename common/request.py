import json
from threading import Thread
from queue import Queue
from operator import attrgetter

import tqdm
import requests
from bs4 import BeautifulSoup

from common import utils
from config.log import logger
from config import settings


def req_thread_count():
    count = settings.request_thread_count
    if isinstance(count, int):
        count = max(16, count)
    else:
        count = utils.get_request_count()
    logger.log('DEBUG', f'Number of request threads {count}')
    return count


def get_port_seq(port):
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


def gen_req_url(domain, port):
    if str(port).endswith('443'):
        url = f'https://{domain}:{port}'
        if port == 443:
            url = f'https://{domain}'
        return url
    url = f'http://{domain}:{port}'
    if port == 80:
        url = f'http://{domain}'
    return url


def gen_req_data(data, ports):
    logger.log('INFOR', 'Generating request urls')
    req_data = list()
    req_urls = set()
    for info in data:
        resolve = info.get('resolve')
        # 解析不成功的子域不进行http请求探测
        if resolve != 1:
            continue
        subdomain = info.get('subdomain')
        for port in ports:
            tmp_info = info.copy()
            tmp_info['port'] = port
            url = gen_req_url(subdomain, port)
            tmp_info['url'] = url
            req_data.append(tmp_info)
            req_urls.add(url)
    return req_data, req_urls


def get_html_title(markup):
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


def get_jump_urls(history):
    urls = list()
    for resp in history:
        urls.append(str(resp.url))
    return urls


def get_progress_bar(total):
    bar = tqdm.tqdm()
    bar.total = total
    bar.desc = 'Request Progress'
    bar.ncols = 80
    return bar


def get(url, resp_list, session):
    timeout = settings.request_timeout_second
    redirect = settings.request_allow_redirect
    proxy = utils.get_proxy()
    try:
        resp = session.get(url, timeout=timeout, allow_redirects=redirect, proxies=proxy)
    except Exception as e:
        logger.log('DEBUG', e.args)
        resp = e
    resp_list.append((url, resp))


def request(urls_queue, resp_list, session):
    while not urls_queue.empty():
        url = urls_queue.get()
        get(url, resp_list, session)
        urls_queue.task_done()


def progress(bar, total, urls_queue):
    while True:
        remaining = urls_queue.qsize()
        done = total - remaining
        bar.n = done
        bar.update()
        if remaining == 0:
            break


def get_session():
    header = utils.gen_fake_header()
    verify = settings.request_ssl_verify
    redirect_limit = settings.request_redirect_limit
    session = requests.Session()
    session.trust_env = False
    session.headers = header
    session.verify = verify
    session.max_redirects = redirect_limit
    return session


def bulk_request(urls):
    logger.log('INFOR', 'Requesting urls in bulk')
    resp_list = list()
    urls_queue = Queue()
    for url in urls:
        urls_queue.put(url)
    total = len(urls)
    session = get_session()
    thread_count = req_thread_count()
    bar = get_progress_bar(total)

    progress_thread = Thread(target=progress, name='ProgressThread',
                             args=(bar, total, urls_queue), daemon=True)
    progress_thread.start()

    for i in range(thread_count):
        request_thread = Thread(target=request, name=f'RequestThread-{i}',
                                args=(urls_queue, resp_list, session), daemon=True)
        request_thread.start()

    urls_queue.join()

    return resp_list


def gen_new_info(info, resp):
    if isinstance(resp, Exception):
        info['reason'] = str(resp.args)
        info['request'] = 0
        info['alive'] = 0
        return info
    info['reason'] = resp.reason
    code = resp.status_code
    info['status'] = code
    info['request'] = 1
    if code == 400 or code >= 500:
        info['alive'] = 0
    else:
        info['alive'] = 1
    headers = resp.headers
    if settings.enable_banner_identify:
        info['banner'] = utils.get_sample_banner(headers)
    info['header'] = json.dumps(dict(headers))
    history = resp.history
    info['history'] = json.dumps(get_jump_urls(history))
    text = utils.decode_resp_text(resp)
    title = get_html_title(text).strip()
    info['title'] = utils.remove_invalid_string(title)
    info['response'] = utils.remove_invalid_string(text)
    return info


def gen_new_data(data, resp_list):
    new_data = list()
    for url, resp in resp_list:
        for info in data:
            if info.get('url') == url:
                new_data.append(gen_new_info(info, resp))
    return new_data


def run_request(domain, data, port):
    """
    HTTP request entrance

    :param  str domain: domain to be requested
    :param  list data: subdomains data to be requested
    :param  any port: range of ports to be requested
    :return list: result
    """
    logger.log('INFOR', f'Start requesting subdomains of {domain}')
    data = utils.set_id_none(data)
    ports = get_port_seq(port)
    req_data, req_urls = gen_req_data(data, ports)
    resp_list = bulk_request(req_urls)
    new_data = gen_new_data(req_data, resp_list)
    count = utils.count_alive(new_data)
    logger.log('INFOR', f'Found that {domain} has {count} alive subdomains')
    sorted_data = utils.sort_by_subdomain(new_data)
    return sorted_data


def save_db(name, data):
    """
    Save request results to database

    :param str  name: table name
    :param list data: data to be saved
    """
    logger.log('INFOR', f'Saving requested results')
    utils.save_db(name, data, 'request')
