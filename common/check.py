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
        for filename in filenames:
            urls.update((f'http://{self.domain}/{filename}',
                         f'https://{self.domain}/{filename}',
                         f'http://www.{self.domain}/{filename}',
                         f'https://www.{self.domain}/{filename}'))
        for url in urls:
            self.header = self.get_header()
            self.proxy = self.get_proxy(self.source)
            resp = self.get(url, check=False, ignore=True)
            self.subdomains = self.collect_subdomains(resp)
            if self.subdomains:
                break
