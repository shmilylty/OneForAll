import re

from config import setting
from config.log import logger
from common.module import Module


class Search(Module):
    """
    Search base class
    """
    def __init__(self):
        Module.__init__(self)
        self.page_num = 0  # 要显示搜索起始条数
        self.per_page_num = 50  # 每页显示搜索条数
        self.recursive_search = setting.enable_recursive_search
        self.recursive_times = setting.search_recursive_times

    @staticmethod
    def filter(domain, subdomain):
        """
        生成搜索过滤语句
        使用搜索引擎支持的-site:语法过滤掉搜索页面较多的子域以发现新域

        :param str domain: 域名
        :param set subdomain: 子域名集合
        :return: 过滤语句
        :rtype: str
        """
        statements_list = []
        subdomains_temp = set(map(lambda x: x + '.' + domain,
                                  setting.subdomains_common))
        subdomains_temp = list(subdomain.intersection(subdomains_temp))
        for i in range(0, len(subdomains_temp), 2):  # 同时排除2个子域
            statements_list.append(''.join(set(map(lambda s: ' -site:' + s,
                                                   subdomains_temp[i:i + 2]))))
        return statements_list

    def match_location(self, domain, url):
        """
        匹配跳转之后的url
        针对部分搜索引擎(如百度搜索)搜索展示url时有显示不全的情况
        此函数会向每条结果的链接发送head请求获取响应头的location值并做子域匹配

        :param str domain: 域名
        :param str url: 展示结果的url链接
        :return: 匹配的子域
        :rtype set
        """
        resp = self.head(url, check=False, allow_redirects=False)
        if not resp:
            return set()
        location = resp.headers.get('location')
        if not location:
            return set()
        return set(self.match_subdomains(domain, location))

    @staticmethod
    def match_subdomains(domain, html, distinct=True):
        """
        Use regexp to match subdomains

        :param  str domain: domain
        :param  str html: response html text
        :param  bool distinct: deduplicate results or not (default True)
        :return set/list: result set or list
        """
        logger.log('TRACE', f'Use regexp to match subdomains in the response body')
        regexp = r'(?:\>|\"|\'|\=|\,)(?:http\:\/\/|https\:\/\/)?' \
                 r'(?:[a-z0-9](?:[a-z0-9\-]{0,61}[a-z0-9])?\.){0,}' \
                 + domain.replace('.', r'\.')
        result = re.findall(regexp, html, re.I)
        if not result:
            return set()
        regexp = r'(?:http://|https://)'
        deal = map(lambda s: re.sub(regexp, '', s[1:].lower()), result)
        if distinct:
            return set(deal)
        else:
            return list(deal)
