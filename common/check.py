import requests
from config.log import logger
from common.module import Module


class Check(Module):
    """
    Check base class
    """

    def __init__(self):
        Module.__init__(self)
        self.request_status = 1

    def to_check(self, filenames):
        urls = set()
        urls_www = set()
        for filename in filenames:
            urls.update((
                f'http://{self.domain}/{filename}',
                f'https://{self.domain}/{filename}',
            ))
            urls_www.update((
                f'http://www.{self.domain}/{filename}',
                f'https://www.{self.domain}/{filename}'
            ))
        self.check_loop(urls)
        self.check_loop(urls_www)

    def check_loop(self, urls):
        for url in urls:
            self.header = self.get_header()
            self.proxy = self.get_proxy(self.source)
            try:
                resp = self.get(url, check=False, ignore=True, raise_error=True)
            except requests.exceptions.ConnectTimeout:
                logger.log('DEBUG', f'Connection to {url} timed out, so break check')
                break
            self.subdomains = self.collect_subdomains(resp)
            if self.subdomains:
                break
