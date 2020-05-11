from common.module import Module
from common import utils


class Lookup(Module):
    """
    DNS query base class
    """

    def __init__(self):
        Module.__init__(self)

    def query(self):
        """
        Query the TXT record of domain
        :return: query result
        """
        answer = utils.dns_query(self.domain, self.type)
        if answer is None:
            return None
        for item in answer:
            record = item.to_text()
            subdomains = self.match_subdomains(self.domain, record)
            self.subdomains = self.subdomains.union(subdomains)
            self.gen_record(subdomains, record)
        return self.subdomains
