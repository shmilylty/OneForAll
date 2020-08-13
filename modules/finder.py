import re
import json
import time
from urllib import parse

from common import utils
from common import resolve
from common import request
from common.module import Module
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
            return data
        self.subdomains = new_subdomains
        self.gen_result()
        temp_data = resolve.run_resolve(domain, self.results)
        fina_data = request.run_request(domain, temp_data, port)
        data = data + fina_data
        self.finish()
        logger.log('INFOR', f'Saving finder results')
        utils.save_db(domain, data, 'finder')
        return data


# Regular expression comes from https://github.com/GerbenJavado/LinkFinder
def find_url(html):
    pattern_raw = r"""
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
    pattern = re.compile(pattern_raw, re.VERBOSE)
    result = re.finditer(pattern, html)
    if result is None:
        return None
    urls = set()
    for match in result:
        url = match.group().strip('"').strip("'")
        urls.add(url)
    return urls


def process_url(req_url, rel_url):
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


def filter_name(path, black_name):
    for name in black_name:
        if path.endswith(name):
            return True
    black_ext = ['io.js', 'ui.js', 'fp.js', 'en.js', 'en-us,js', 'zh.js', 'zh-cn.js',
                 'zh_cn.js', 'dev.js', 'min.js', 'umd.js', 'esm.js', 'all.js', 'cjs.js', 'prod.js',
                 'slim.js', 'core.js', 'global.js', 'bundle.js', 'browser.js',
                 'brands.js', 'simple.js', 'common.js', 'development.js', 'banner.js',
                 'production.js']
    for ext in black_ext:
        if path.endswith(ext):
            return True
    r = re.compile(r'\d+.\d+.\d+')
    if r.search(path):
        return True
    return False


def filter_url(domain, url, black_name):
    try:
        raw_url = parse.urlparse(url)
    except Exception as e:  # 解析失败则跳过该URL
        logger.log('DEBUG', url, e.args)
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
    return filter_name(path, black_name)


def get_black_name():
    path = settings.data_storage_dir.joinpath('common_js_library.json')
    with open(path) as fp:
        return json.load(fp)


def match_subdomains(domain, text):
    subdomains = utils.match_subdomains(domain, text, fuzzy=False)
    logger.log('DEBUG', f'matched subdomains: {subdomains}')
    return subdomains


def find_subdomains(domain, data):
    subdomains = set()
    js_urls = set()
    black_name = get_black_name()
    for item in data:
        req_url = item.get('url')
        rsp_html = item.get('response')
        if not rsp_html:
            continue
        logger.log('DEBUG', f'matching subdomains from response of {req_url}')
        subdomains = subdomains.union(match_subdomains(domain, rsp_html))
        urls = find_url(rsp_html)
        if not urls:
            continue
        for rel_url in urls:
            url = process_url(req_url, rel_url)
            if not filter_url(domain, url, black_name):
                js_urls.add(url)
    resp_data = request.urls_request(js_urls)
    for resp, text in resp_data:
        if text:
            logger.log('DEBUG', f'matching subdomains from response of {resp.url}')
            subdomains = subdomains.union(match_subdomains(domain, text))
    return subdomains
