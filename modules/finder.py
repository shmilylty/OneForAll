import re
from urllib import parse

from common import utils
from common import request
from common.module import Module
from config import setting


class Finder(Module):
    def __init__(self, domain):
        Module.__init__(self)
        self.module = 'Finder'
        self.source = ''
        self.domain = domain
        self.ts = utils.get_timestring()
        self.name = f'found_subdomains_{self.domain}_{self.ts}'
        self.path = setting.temp_save_dir.joinpath(self.name)

    def save_subdomain(self, data, path):
        if not path:
            path = self.path
        utils.save_data(path, data)

    def remove_subdomain(self, path):
        if not path:
            path = self.path
        utils.remove_data(path)

    def find_url(self):
        pass

    def batch_find_url(self):
        pass

    def find_subdomain(self, html):
        subdomains = self.match_subdomains(html, fuzzy=False)
        self.subdomains.add(subdomains)

    def find_js(self):
        pass

    def filter_js(self):
        pass


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


def filter_url(urs):
    pass


def run_finder(domain, data):
    existing_subdomains = set(map(lambda x: x.get('subdomain'), data))  # 已有的子域
    found_subdomains = set()
    found_urls = set()
    finder = Finder(domain)
    for item in data:
        req_url = item.get('url')
        rsp_html = item.get('response')
        found_subdomains.add(finder.match_subdomains(rsp_html))
        urls = find_url(rsp_html)
        if not urls:
            continue
        for rel_url in urls:
            found_url = process_url(req_url, rel_url)
            found_urls.add(found_url)

    resp_data = request.urls_request(found_urls)
    new_subdomains = found_subdomains - existing_subdomains


def save_db(domain, data):
    pass
