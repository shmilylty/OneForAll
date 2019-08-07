# coding=utf-8
import requests
import config
from .module import Module
from . import utils


class Search(Module):
    """
    搜索基类
    """
    def __init__(self):
        Module.__init__(self)
        self.page_num = 0  # 要显示搜索起始条数
        self.per_page_num = 50  # 每页显示搜索条数
        self.recursive_search = config.enable_recursive_search
        self.recursive_times = config.search_recursive_times

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
                                  config.subdomains_common))
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
        resp = requests.head(url, headers=self.header, proxies=self.proxy,
                             timeout=self.timeout, allow_redirects=False)
        location = resp.headers.get('location')
        return set(utils.match_subdomain(domain, location))
