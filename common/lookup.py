from .module import Module
from common import utils


class Lookup(Module):
    """
    DNS查询基类
    """
    def __init__(self):
        Module.__init__(self)

    def query(self):
        """
        查询域名的TXT记录
        :return: 查询结果
        """
        answer = utils.dns_query(self.domain, self.type)
        if answer is None:
            return None
        for item in answer:
            record = item.to_text()
            subdomains = utils.match_subdomain(self.domain, record)
            self.subdomains = self.subdomains.union(subdomains)
            self.gen_record(subdomains, record)
        return self.subdomains
