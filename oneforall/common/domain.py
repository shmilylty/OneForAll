# coding=utf-8
import re
import tldextract
import config


class Domain(object):
    """
    域名处理类

    :param str string: 传入的字符串
    """
    def __init__(self, string):
        self.string = str(string)
        self.regexp = r'\b((?=[a-z0-9-]{1,63}\.)(xn--)?[a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,63}\b'
        self.domain = None

    def match(self):
        """
        域名匹配

        :return: 匹配结果
        """
        result = re.search(self.regexp, self.string, re.I)
        if result:
            return result.group()
        else:
            return None

    def extract(self):
        """
        域名导出

        >>> d = Domain('www.example.com')
        <domain.Domain object>
        >>> d.extract()
        ExtractResult(subdomain='www', domain='example', suffix='com')

        :return: 导出结果
        """
        extract_cache_file = config.data_storage_path.joinpath('public_suffix_list.dat')
        tldext = tldextract.TLDExtract(extract_cache_file)
        result = self.match()
        if result:
            return tldext(result)
        else:
            return None

    def registered(self):
        """
        获取注册域名

        >>> d = Domain('www.example.com')
        <domain.Domain object>
        >>> d.registered()
        example.com

        :return: 注册域名
        """
        result = self.extract()
        if result:
            return result.registered_domain
        else:
            return None
