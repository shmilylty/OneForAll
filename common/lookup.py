from common.module import Module
from common import utils
from config.log import logger


class Lookup(Module):
    """
    DNS query base class
    """

    def __init__(self):
        Module.__init__(self)
        self.qtype = ''

    def query(self):
        """
        Query the TXT record of domain
        :return: query result
        """
        answer = utils.dns_query(self.domain, self.qtype)
        if answer is None:
            return None
        for item in answer:
            record = item.to_text()
            subdomains = self.match_subdomains(record)
            self.subdomains.update(subdomains)
            logger.log('DEBUG', record)
        return self.subdomains
