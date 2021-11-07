import re
import time
from urllib import parse
from requests import Response

from common import utils
from common import resolve
from common import request
from common.module import Module
from common.database import Database
from config import settings
from config.log import logger


class Finder(Module):
    def __init__(self):
        Module.__init__(self)
        self.module = 'Finder'
        self.source = 'Finder'
        self.start = time.time()  # 模块开始执行时间

    def run(self, domain, data, port):
        logger.log('INFOR', f'Start Finder module')
        existing_subdomains = set(map(lambda x: x.get('subdomain'), data))  # 已有的子域
        found_subdomains = find_subdomains(domain, data)
        new_subdomains = found_subdomains - existing_subdomains
        if not len(new_subdomains):
            self.finish()  # 未发现新的子域就直接返回
        self.subdomains = new_subdomains
        self.finish()
        self.gen_result()
        resolved_data = resolve.run_resolve(domain, self.results)
        request.run_request(domain, resolved_data, port)


file_path = settings.data_storage_dir.joinpath('common_js_library.json')
black_name = utils.load_json(file_path)
# Regular expression comes from https://github.com/GerbenJavado/LinkFinder
expression = r"""
    (?:"|')                               # Start newline delimiter
    (
        ((?:[a-zA-Z]{1,10}://|//)           # Match a scheme [a-Z]*1-10 or //
        [^"'/]{1,}\.                        # Match a domain name (any character + dot)
        [a-zA-Z]{2,}[^"']{0,})              # The domain extension and/or path
        |
        ((?:/|\.\./|\./)                    # Start with /,../,./
        [^"'><,;| *()(%%$^/\\\[\]]          # Next character can't be...
        [^"'><,;|()]{1,})                   # Rest of the characters can't be
        |
        ([a-zA-Z0-9_\-/]{1,}/               # Relative endpoint with /
        [a-zA-Z0-9_\-/]{1,}                 # Resource name
        \.(?:[a-zA-Z]{1,4}|action)          # Rest + extension (length 1-4 or action)
        (?:[\?|/][^"|']{0,}|))              # ? mark with parameters
        |
        ([a-zA-Z0-9_\-]{1,}                 # filename
        \.(?:js)                            # . + extension
        (?:\?[^"|']{0,}|))                  # ? mark with parameters
    )
    (?:"|')                                 # End newline delimiter
    """
url_pattern = re.compile(expression, re.VERBOSE)


def find_new_urls(html):
    result = re.finditer(url_pattern, html)
    if result is None:
        return None
    urls = set()
    for match in result:
        url = match.group().strip('"').strip("'")
        urls.add(url)
    return urls


def convert_url(req_url, rel_url):
    black_url = ["javascript:"]  # Add some keyword for filter url.
    raw_url = parse.urlparse(req_url)
    netloc = raw_url.netloc
    scheme = raw_url.scheme
    if rel_url[0:2] == "//":
        result = scheme + ":" + rel_url
    elif rel_url[0:4] == "http":
        result = rel_url
    elif rel_url[0:2] != "//" and rel_url not in black_url:
        if rel_url[0:1] == "/":
            result = scheme + "://" + netloc + rel_url
        else:
            if rel_url[0:1] == ".":
                if rel_url[0:2] == "..":
                    result = scheme + "://" + netloc + rel_url[2:]
                else:
                    result = scheme + "://" + netloc + rel_url[1:]
            else:
                result = scheme + "://" + netloc + "/" + rel_url
    else:
        result = req_url
    return result


def filter_name(path):
    for name in black_name:
        if path.endswith(name):
            return True
    black_ext = ['io.js', 'ui.js', 'fp.js', 'en.js', 'en-us,js', 'zh.js', 'zh-cn.js',
                 'zh_cn.js', 'dev.js', 'min.js', 'umd.js', 'esm.js', 'all.js', 'cjs.js',
                 'prod.js', 'slim.js', 'core.js', 'global.js', 'bundle.js', 'browser.js',
                 'brands.js', 'simple.js', 'common.js', 'development.js', 'banner.js',
                 'production.js']
    for ext in black_ext:
        if path.endswith(ext):
            return True
    r = re.compile(r'\d+.\d+.\d+')
    if r.search(path):
        return True
    return False


def filter_url(domain, url):
    try:
        raw_url = parse.urlparse(url)
    except Exception as e:  # 解析失败则跳过该URL
        logger.log('DEBUG', e.args)
        return True
    scheme = raw_url.scheme.lower()
    if not scheme:
        return True
    if scheme not in ['http', 'https']:
        return True
    netloc = raw_url.netloc.lower()
    if not netloc:
        return True
    if not netloc.endswith(domain):
        return True
    path = raw_url.path.lower()
    if not path:
        return True
    if not path.endswith('.js'):
        return True
    if path.endswith('min.js'):
        return True
    return filter_name(path)


def match_subdomains(domain, text):
    if isinstance(text, str):
        subdomains = utils.match_subdomains(domain, text, fuzzy=False)
    else:
        logger.log('DEBUG', f'abnormal object: {type(text)}')
        subdomains = set()
    logger.log('TRACE', f'matched subdomains: {subdomains}')
    return subdomains


def find_in_resp(domain, url, html):
    logger.log('TRACE', f'matching subdomains from response of {url}')
    return match_subdomains(domain, html)


def find_in_history(domain, url, history):
    logger.log('TRACE', f'matching subdomains from history of {url}')
    return match_subdomains(domain, history)


def find_js_urls(domain, req_url, rsp_html):
    js_urls = set()
    new_urls = find_new_urls(rsp_html)
    if not new_urls:
        return js_urls
    for rel_url in new_urls:
        url = convert_url(req_url, rel_url)
        if not filter_url(domain, url):
            js_urls.add(url)
    return js_urls


def convert_to_dict(url_list):
    url_dict = []
    for url in url_list:
        url_dict.append({'url': url})
    return url_dict

def find_subdomains(domain, data):
    subdomains = set()
    js_urls = set()
    db = Database()
    for infos in data:
        jump_history = infos.get('history')
        req_url = infos.get('url')
        subdomains.update(find_in_history(domain, req_url, jump_history))
        rsp_html = db.get_resp_by_url(domain, req_url)
        if not rsp_html:
            logger.log('DEBUG', f'an abnormal response occurred in the request {req_url}')
            continue
        subdomains.update(find_in_resp(domain, req_url, rsp_html))
        js_urls.update(find_js_urls(domain, req_url, rsp_html))

    req_data = convert_to_dict(js_urls)
    resp_data = request.bulk_request(domain, req_data, ret=True)
    while not resp_data.empty():
        _, resp = resp_data.get()
        if not isinstance(resp, Response):
            continue
        text = utils.decode_resp_text(resp)
        subdomains.update(find_in_resp(domain, resp.url, text))
    return subdomains
