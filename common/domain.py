import re
from common import tldextract
from config import settings


class Domain(object):
    """
    Processing domain class

    :param str string: input string
    """
    def __init__(self, string):
        self.string = str(string)
        self.regexp = r'\b((?=[a-z0-9-]{1,63}\.)(xn--)?[a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,63}\b'
        self.domain = None

    def match(self):
        """
        match domain

        :return : result
        """
        result = re.search(self.regexp, self.string, re.I)
        if result:
            return result.group()
        return None

    def extract(self):
        """
        extract domain

        >>> d = Domain('www.example.com')
        <domain.Domain object>
        >>> d.extract()
        ExtractResult(subdomain='www', domain='example', suffix='com')

        :return: extracted domain results
        """
        data_storage_dir = settings.data_storage_dir
        extract_cache_file = data_storage_dir.joinpath('public_suffix_list.dat')
        ext = tldextract.TLDExtract(extract_cache_file)
        result = self.match()
        if result:
            return ext(result)
        return None

    def registered(self):
        """
        registered domain

        >>> d = Domain('www.example.com')
        <domain.Domain object>
        >>> d.registered()
        example.com

        :return: registered domain result
        """
        result = self.extract()
        if result:
            return result.registered_domain
        return None
