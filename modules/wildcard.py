import secrets

import tenacity
from dns.exception import Timeout
from dns.resolver import NXDOMAIN, YXDOMAIN, NoAnswer, NoNameservers

from common import utils
from config import settings
from common import similarity
from config.log import logger


def gen_random_subdomains(domain, count):
    """
    生成指定数量的随机子域域名列表

    :param domain: 主域
    :param count: 数量
    """
    subdomains = set()
    if count < 1:
        return subdomains
    for _ in range(count):
        token = secrets.token_hex(4)
        subdomains.add(f'{token}.{domain}')
    return subdomains


def query_a_record(subdomain, resolver):
    """
    查询子域A记录

    :param subdomain: 子域
    :param resolver: DNS解析器
    """
    try:
        answer = resolver.query(subdomain, 'A')
    except Exception as e:
        logger.log('DEBUG', f'Query {subdomain} wildcard dns record error')
        logger.log('DEBUG', e.args)
        return False
    if answer.rrset is None:
        return False
    ttl = answer.ttl
    name = answer.name
    ips = {item.address for item in answer}
    logger.log('ALERT', f'{subdomain} resolve to: {name} '
                        f'IP: {ips} TTL: {ttl}')
    return True


def all_resolve_success(subdomains):
    """
    判断是否所有子域都解析成功

    :param subdomains: 子域列表
    """
    resolver = utils.dns_resolver()
    resolver.cache = None  # 不使用DNS缓存
    status = set()
    for subdomain in subdomains:
        status.add(query_a_record(subdomain, resolver))
    return all(status)


def all_request_success(subdomains):
    """
    判断是否所有子域都请求成功

    :param subdomains: 子域列表
    """
    result = list()
    for subdomain in subdomains:
        url = f'http://{subdomain}'
        resp = utils.get_url_resp(url)
        if resp:
            logger.log('ALERT', f'Request: {url} Status: {resp.status_code} '
                                f'Size: {len(resp.content)}')
            result.append(resp.text)
        else:
            result.append(resp)
    return all(result), result


def any_similar_html(resp_list):
    """
    判断是否有一组HTML页面结构相似

    :param resp_list: 响应HTML页面
    """
    html_doc1, html_doc2, html_doc3 = resp_list
    if similarity.is_similar(html_doc1, html_doc2):
        return True
    if similarity.is_similar(html_doc1, html_doc3):
        return True
    if similarity.is_similar(html_doc2, html_doc3):
        return True
    return False


def to_detect_wildcard(domain):
    """
    Detect use wildcard dns record or not

    :param  str  domain:  domain
    :return bool use wildcard dns record or not
    """
    logger.log('INFOR', f'Detecting {domain} use wildcard dns record or not')
    random_subdomains = gen_random_subdomains(domain, 3)
    if not all_resolve_success(random_subdomains):
        return False
    is_all_success, all_request_resp = all_request_success(random_subdomains)
    if not is_all_success:
        return True
    return any_similar_html(all_request_resp)


def detect_wildcard(domain):
    is_enable = to_detect_wildcard(domain)
    if is_enable:
        logger.log('ALERT', f'The domain {domain} enables wildcard')
    else:
        logger.log('ALERT', f'The domain {domain} disables wildcard')
    return is_enable


@tenacity.retry(stop=tenacity.stop_after_attempt(2))
def get_wildcard_record(domain, resolver):
    logger.log('INFOR', f"Query {domain} 's wildcard dns record "
                        f"in authoritative name server")
    try:
        answer = resolver.query(domain, 'A')

    except Timeout as e:
        logger.log('ALERT', f'Query timeout, retrying')
        logger.log('DEBUG', e.args)
        return None, None
    except (NXDOMAIN, YXDOMAIN, NoAnswer, NoNameservers) as e:
        logger.log('DEBUG', e.args)
        logger.log('DEBUG', f'{domain} dont have A record on authoritative name server')
        return None, None
    except Exception as e:
        logger.log('ERROR', e.args)
        logger.log('ERROR', f'Query {domain} wildcard dns record in '
                            f'authoritative name server error')
        exit(1)
    else:
        if answer.rrset is None:
            logger.log('DEBUG', f'No record of query result')
            return None, None
        name = answer.name
        ip = {item.address for item in answer}
        ttl = answer.ttl
        logger.log('INFOR', f'{domain} results on authoritative name server: {name} '
                            f'IP: {ip} TTL: {ttl}')
        return ip, ttl


def collect_wildcard_record(domain, authoritative_ns):
    logger.log('INFOR', f'Collecting wildcard dns record for {domain}')
    if not authoritative_ns:
        return list(), int()
    resolver = utils.dns_resolver()
    resolver.nameservers = authoritative_ns  # 使用权威名称服务器
    resolver.rotate = True  # 随机使用NS
    resolver.cache = None  # 不使用DNS缓存
    ips = set()
    ttl = int()
    ttls_check = list()
    ips_stat = dict()
    ips_check = list()
    while True:
        token = secrets.token_hex(4)
        random_subdomain = f'{token}.{domain}'
        try:
            ip, ttl = get_wildcard_record(random_subdomain, resolver)
        except Exception as e:
            logger.log('DEBUG', e.args)
            logger.log('ALERT', f'Multiple query errors,'
                                f'try to query a new random subdomain')
            continue
        # 每5次查询检查结果列表 如果都没结果则结束查询
        ips_check.append(ip)
        ttls_check.append(ttl)
        if len(ips_check) == 5:
            if not any(ips_check):
                logger.log('ALERT', 'The query ends because there are '
                                    'no results for 5 consecutive queries.')
                break
            ips_check = list()
        if len(ttls_check) == 5 and len(set(ttls_check)) == 5:
            logger.log('ALERT', 'The query ends because there are '
                                '5 different TTL results for 5 consecutive queries.')
            ips, ttl = set(), int()
            break
        if ip is None:
            continue
        ips.update(ip)
        # 统计每个泛解析IP出现次数
        for addr in ip:
            count = ips_stat.setdefault(addr, 0)
            ips_stat[addr] = count + 1
        # 筛选出出现次数2次以上的IP地址
        addrs = list()
        for addr, times in ips_stat.items():
            if times >= 2:
                addrs.append(addr)
        # 大部分的IP地址出现次数大于2次停止收集泛解析IP记录
        if len(addrs) / len(ips) >= 0.8:
            break
    logger.log('DEBUG', f'Collected the wildcard dns record of {domain}\n{ips}\n{ttl}')
    return ips, ttl


def check_by_compare(ip, ttl, wc_ips, wc_ttl):
    """
    Use TTL comparison to detect wildcard dns record

    :param  set ip:     A record IP address set
    :param  int ttl:    A record TTL value
    :param  set wc_ips: wildcard dns record IP address set
    :param  int wc_ttl: wildcard dns record TTL value
    :return bool: result
    """
    # Reference：http://sh3ll.me/archives/201704041222.txt
    if ip not in wc_ips:
        return False  # 子域IP不在泛解析IP集合则不是泛解析
    if ttl != wc_ttl and ttl % 60 == 0 and wc_ttl % 60 == 0:
        return False
    return True


def check_ip_times(times):
    """
    Use IP address times to determine wildcard or not

    :param  times: IP address times
    :return bool:  result
    """
    if times > settings.ip_appear_maximum:
        return True
    return False


def check_cname_times(times):
    """
    Use cname times to determine wildcard or not

    :param  times: cname times
    :return bool:  result
    """
    if times > settings.cname_appear_maximum:
        return True
    return False


def is_valid_subdomain(ip=None, ip_num=None, cname=None, cname_num=None,
                       ttl=None, wc_ttl=None, wc_ips=None):
    ip_blacklist = settings.brute_ip_blacklist
    cname_blacklist = settings.brute_cname_blacklist
    if cname and cname in cname_blacklist:
        return 0, 'cname blacklist'  # 有些泛解析会统一解析到一个cname上
    if ip and ip in ip_blacklist:  # 解析ip在黑名单ip则为非法子域
        return 0, 'IP blacklist'
    if all([wc_ips, wc_ttl]):  # 有泛解析记录才进行对比
        if check_by_compare(ip, ttl, wc_ips, wc_ttl):
            return 0, 'IP wildcard'
    if ip_num and check_ip_times(ip_num):
        return 0, 'IP exceeded'
    if cname_num and check_cname_times(cname_num):
        return 0, 'cname exceeded'
    return 1, 'OK'


def stat_times(data):
    times = dict()
    for info in data:
        ip_str = info.get('ip')
        if isinstance(ip_str, str):
            ips = ip_str.split(',')
            for ip in ips:
                value_one = times.setdefault(ip, 0)
                times[ip] = value_one + 1
        cname_str = info.get('cname')
        if isinstance(cname_str, str):
            cnames = cname_str.split(',')
            for cname in cnames:
                value_two = times.setdefault(cname, 0)
                times[cname] = value_two + 1
    return times


def check_valid_subdomain(appear_times, info):
    ip_str = info.get('ip')
    if ip_str:
        ips = ip_str.split(',')
        for ip in ips:
            ip_num = appear_times.get(ip)
            isvalid, reason = is_valid_subdomain(ip=ip, ip_num=ip_num)
            if not isvalid:
                return False, reason
    cname_str = info.get('cname')
    if cname_str:
        cnames = cname_str.split(',')
        for cname in cnames:
            cname_num = appear_times.get(cname)
            isvalid, reason = is_valid_subdomain(cname=cname, cname_num=cname_num)
            if not isvalid:
                return False, reason
    return True, 'OK'


def deal_wildcard(data):
    new_data = list()
    appear_times = stat_times(data)
    for info in data:
        subdomain = info.get('subdomain')
        isvalid, reason = check_valid_subdomain(appear_times, info)
        logger.log('DEBUG', f'{subdomain} is {isvalid} subdomain reason because {reason}')
        if isvalid:
            new_data.append(info)
    return new_data
