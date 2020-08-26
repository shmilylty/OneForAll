import json
from threading import Thread
from queue import Queue


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


def gen_req_urls(data, ports):
    logger.log('INFOR', 'Generating request urls')
    urls = set()
    for info in data:
        resolve = info.get('resolve')
        # 解析不成功的子域不进行http请求探测
        if resolve != 1:
            continue
        subdomain = info.get('subdomain')
        for port in ports:
            urls.add(gen_req_url(subdomain, port))
    return urls


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


def get(url, resp_queue, session):
    timeout = settings.request_timeout_second
    redirect = settings.request_allow_redirect
    proxy = utils.get_proxy()
    try:
        resp = session.get(url, timeout=timeout, allow_redirects=redirect, proxies=proxy)
    except Exception as e:
        logger.log('DEBUG', e.args)
        return
    resp_queue.put(resp)


def request(urls_queue, resp_queue, session):
    while not urls_queue.empty():
        url = urls_queue.get()
        get(url, resp_queue, session)
        urls_queue.task_done()


def progress(urls, resp_queue):
    bar = tqdm.tqdm()
    bar.total = len(urls)
    bar.desc = 'Request Progress'
    bar.ncols = 80
    while True:
        done = resp_queue.qsize()
        bar.n = done
        bar.update()
        if done == bar.total:
            break


def get_session():
    header = utils.gen_fake_header()
    verify = settings.request_ssl_verify
    redirect_limit = settings.request_redirect_limit
    session = requests.Session()
    session.headers = header
    session.verify = verify
    session.max_redirects = redirect_limit
    return session


def bulk_request(urls):
    logger.log('INFOR', 'Requesting urls in bulk')
    resp_list = list()
    urls_queue = Queue()
    resp_queue = Queue()
    for url in urls:
        urls_queue.put(url)
    session = get_session()
    thread_count = req_thread_count()

    progress_thread = Thread(target=progress, args=(urls, resp_queue))
    progress_thread.start()

    for _ in range(thread_count):
        request_thread = Thread(target=request, args=(urls_queue, resp_queue, session))
        request_thread.start()

    urls_queue.join()

    while not resp_queue.empty():
        resp = resp_queue.get()
        resp_list.append(resp)
    return resp_list


def gen_new_info(info, resp):
    port = resp.raw._pool.port
    info['port'] = port
    info['url'] = resp.url
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
    for resp in resp_list:
        subdomain = resp.raw._pool.host
        for info in data:
            if info.get('subdomain') == subdomain:
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
    filtered_data = utils.get_filtered_data(data)
    req_urls = gen_req_urls(data, ports)
    resp_list = bulk_request(req_urls)
    new_data = gen_new_data(data, resp_list)
    data = new_data + filtered_data
    count = utils.count_alive(data)
    logger.log('INFOR', f'Found that {domain} has {count} alive subdomains')
    return data


def save_db(name, data):
    """
    Save request results to database

    :param str  name: table name
    :param list data: data to be saved
    """
    logger.log('INFOR', f'Saving requested results')
    utils.save_db(name, data, 'request')
