# coding=utf-8
"""
OneForAll配置
"""

import pathlib
import urllib3

# 路径设置
relative_directory = pathlib.Path(__file__).parent.parent  # OneForAll代码相对路径
module_dir = relative_directory.joinpath('modules')  # OneForAll模块目录
third_party_dir = relative_directory.joinpath('thirdparty')  # 三方工具目录
data_storage_dir = relative_directory.joinpath('data')  # 数据存放目录
result_save_dir = relative_directory.joinpath('results')  # 结果保存目录


# OneForAll入口参数设置
enable_dns_resolve = True  # 使用DNS解析子域(默认True)
enable_http_request = True  # 使用HTTP请求子域(默认True)
enable_takeover_check = False  # 开启子域接管风险检查(默认False)
# 参数port可选值有'default', 'small', 'large'
http_request_port = 'default'  # HTTP请求子域(默认'default'，探测80端口)
# 参数alive可选值True，False分别表示导出存活，全部子域结果
result_export_alive = False  # 只导出存活的子域结果(默认False)
# 参数format可选格式有'rst', 'csv', 'tsv', 'json', 'yaml', 'html',
# 'jira', 'xls', 'xlsx', 'dbf', 'latex', 'ods'
result_save_format = 'csv'  # 子域结果保存文件格式(默认csv)
# 参数path默认None使用OneForAll结果目录自动生成路径
result_save_path = None  # 子域结果保存文件路径(默认None)


# 收集模块设置
save_module_result = False  # 保存各模块发现结果为json文件(默认False)
enable_all_module = True  # 启用所有模块(默认True)
enable_partial_module = []  # 启用部分模块 必须禁用enable_all_module才能生效
# 只使用ask和baidu搜索引擎收集子域的示例
# enable_partial_module = [('modules.search', 'ask')
#                          ('modules.search', 'baidu')]
module_thread_timeout = 180.0  # 每个收集模块线程超时时间(默认3分钟)

# 爆破模块设置
enable_brute_module = False  # 使用爆破模块(默认False)
enable_wildcard_check = True  # 开启泛解析检测(默认True)
enable_wildcard_deal = True  # 开启泛解析处理(默认True)
brute_massdns_path = None  # 默认None自动选择 如需填写请填写绝对路径
brute_status_format = 'ansi'  # 爆破时状态输出格式（默认asni，可选json）
# 爆破时使用的进程数(根据计算机中CPU数量情况设置 不宜大于逻辑CPU个数)
brute_process_num = 1  # 默认1
brute_concurrent_num = 10000  # 并发查询数量(默认10000)
brute_socket_num = 1  # 爆破时每个进程下的socket数量
brute_resolve_num = 50  # 解析失败时尝试换名称服务器重查次数
# 爆破所使用的字典路径 默认data/subdomains.txt
brute_wordlist_path = data_storage_dir.joinpath('subnames.txt')
brute_nameservers_path = data_storage_dir.joinpath('cn_nameservers.txt')
# 域名的权威DNS名称服务器的保存路径 当域名开启了泛解析时会使用该名称服务器来进行A记录查询
authoritative_dns_path = data_storage_dir.joinpath('authoritative_dns.txt')
enable_recursive_brute = False  # 是否使用递归爆破(默认False)
brute_recursive_depth = 2  # 递归爆破深度(默认2层)
# 爆破下一层子域所使用的字典路径 默认data/next_subdomains.txt
recursive_nextlist_path = data_storage_dir.joinpath('next_subnames.txt')
enable_check_dict = False  # 是否开启字典配置检查提示(默认False)
delete_generated_dict = True  # 是否删除爆破时临时生成的字典(默认True)
# 是否删除爆破时massdns输出的解析结果 (默认True)
#  massdns输出的结果中包含更详细解析结果
#  注意: 当爆破的字典较大或使用递归爆破或目标域名存在泛解析时生成的文件可能会很大
delete_massdns_result = True
only_save_valid = True  # 是否在处理爆破结果时只存入解析成功的子域
check_time = 10  # 检查字典配置停留时间(默认10秒)
enable_fuzz = False  # 是否使用fuzz模式枚举域名
fuzz_place = None  # 指定爆破的位置 指定的位置用`@`表示 示例：www.@.example.com
fuzz_rule = None  # fuzz域名的正则 示例：'[a-z][0-9]' 表示第一位是字母 第二位是数字
brute_ip_blacklist = {'0.0.0.0', '0.0.0.1'}  # IP黑名单 子域解析到IP黑名单则标记为非法子域
ip_appear_maximum = 100  # 多个子域解析到同一IP次数超过100次则标记为非法(泛解析)子域

# 代理设置
enable_proxy = False  # 是否使用代理(全局开关)
proxy_all_module = False  # 代理所有模块
proxy_partial_module = ['GoogleQuery', 'AskSearch', 'DuckDuckGoSearch',
                        'GoogleAPISearch', 'GoogleSearch', 'YahooSearch',
                        'YandexSearch', 'CrossDomainXml',
                        'ContentSecurityPolicy']  # 代理自定义的模块
proxy_pool = [{'http': 'http://127.0.0.1:1080',
               'https': 'https://127.0.0.1:1080'}]  # 代理池
# proxy_pool = [{'http': 'socks5h://127.0.0.1:10808',
#                'https': 'socks5h://127.0.0.1:10808'}]  # 代理池


# 网络请求设置
enable_fake_header = True  # 启用伪造请求头
request_delay = 1  # 请求时延
request_timeout = 60  # 请求超时
request_verify = False  # 请求SSL验证
# 禁用安全警告信息
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 搜索模块设置
enable_recursive_search = False  # 递归搜索子域
search_recursive_times = 2  # 递归搜索层数

# DNS解析设置
resolve_coroutine_num = 64
resolver_nameservers = [
    '223.5.5.5',  # AliDNS
    '119.29.29.29',  # DNSPod
    '114.114.114.114',  # 114DNS
    '8.8.8.8',   # Google DNS
    '1.1.1.1'  # CloudFlare DNS
]  # 指定查询的DNS域名服务器
resolver_timeout = 5.0  # 解析超时时间
resolver_lifetime = 60.0  # 解析存活时间
limit_resolve_conn = 500  # 限制同一时间解析的数量(默认500)

# 请求端口探测设置
# 你可以在端口列表添加自定义端口
default_ports = [80]  # 默认使用
small_ports = [80, 443, 8000, 8080, 8443]
# 注意：建议大厂的域名尽量不使用大端口范围，因为大厂的子域太多，加上使用大端口范围会导致生成的
# 请求上十万，百万，千万级，可能会导致内存不足程序奔溃，另外这样级别的请求量等待时间也是漫长的。
# OneForAll不是一个端口扫描工具，如果要扫端口建议使用nmap,zmap之类的工具。
large_ports = [80, 81, 280, 300, 443, 591, 593, 832, 888, 901, 981, 1010, 1080,
               1100, 1241, 1311, 1352, 1434, 1521, 1527, 1582, 1583, 1944, 2082,
               2082, 2086, 2087, 2095, 2096, 2222, 2301, 2480, 3000, 3128, 3333,
               4000, 4001, 4002, 4100, 4125, 4243, 4443, 4444, 4567, 4711, 4712,
               4848, 4849, 4993, 5000, 5104, 5108, 5432, 5555, 5800, 5801, 5802,
               5984, 5985, 5986, 6082, 6225, 6346, 6347, 6443, 6480, 6543, 6789,
               7000, 7001, 7002, 7396, 7474, 7674, 7675, 7777, 7778, 8000, 8001,
               8002, 8003, 8004, 8005, 8006, 8008, 8009, 8010, 8014, 8042, 8069,
               8075, 8080, 8081, 8083, 8088, 8090, 8091, 8092, 8093, 8016, 8118,
               8123, 8172, 8181, 8200, 8222, 8243, 8280, 8281, 8333, 8384, 8403,
               8443, 8500, 8530, 8531, 8800, 8806, 8834, 8880, 8887, 8888, 8910,
               8983, 8989, 8990, 8991, 9000, 9043, 9060, 9080, 9090, 9091, 9200,
               9294, 9295, 9443, 9444, 9800, 9981, 9988, 9990, 9999, 10000,
               10880, 11371, 12043, 12046, 12443, 15672, 16225, 16080, 18091,
               18092, 20000, 20720, 24465, 28017, 28080, 30821, 43110, 61600]
ports = {'default': default_ports, 'small': small_ports, 'large': large_ports}

# aiohttp有关配置
verify_ssl = False
# aiohttp 支持 HTTP/HTTPS形式的代理
aiohttp_proxy = None  # proxy="http://user:pass@some.proxy.com"
allow_redirects = True  # 允许请求跳转
fake_header = True  # 使用伪造请求头
# 为了保证请求质量 请谨慎更改以下设置
# request_method只能是HEAD或GET,HEAD请求方法更快，但是不能获取响应体并提取从中提取
request_method = 'GET'  # 使用请求方法，默认GET
sockread_timeout = 10  # 每个请求socket读取超时时间，默认5秒
sockconn_timeout = 10  # 每个请求socket连接超时时间，默认5秒
# 限制同一时间打开的连接总数
limit_open_conn = 100  # 默认100
# 限制同一时间在同一个端点((host, port, is_ssl) 3者都一样的情况)打开的连接数
limit_per_host = 10  # 0表示不限制,默认10

subdomains_common = {'i', 'w', 'm', 'en', 'us', 'zh', 'w3', 'app', 'bbs',
                     'web', 'www', 'job', 'docs', 'news', 'blog', 'data',
                     'help', 'live', 'mall', 'blogs', 'files', 'forum',
                     'store', 'mobile'}

