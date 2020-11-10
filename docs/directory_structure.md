```
D:.
|   .gitignore
|   .travis.yml
|   brute.py        可以单独运行的子域爆破模块
|   collect.py      各个收集模块上层调用
|   dbexport.py     可以单独运行的数据库导出模块
|   Dockerfile
|   LICENSE
|   oneforall.py    OneForAll主入口
|   Pipfile
|   Pipfile.lock
|   README.en.md
|   README.md
|   requirements.txt
|   takeover.py     可以单独运行的子域接口风险检查模块
|   _config.yml
|
+---.github
|   +---ISSUE_TEMPLATE
|   |       bug_report.md
|   |       bug_report_zh.md
|   |       custom.md
|   |       feature_request.md
|   |
|   \---workflows
|           test.yml
|
|
+---common 公共调用模块
|       crawl.py
|       database.py
|       domain.py
|       lookup.py
|       module.py
|       query.py
|       request.py
|       resolve.py
|       search.py
|       utils.py
|       __init__.py
|
+---config 配置目录
|       api.py      部分收集模块的API配置文件
|       log.py      日志模块配置文件
|       setting.py  OneForAll主要配置文件
|
+---data 存放一些所需数据
|       authoritative_dns.txt   临时存放开启了泛解析域名的权威DNS名称服务器IP地址
|       subnames_big.7z        子域爆破超大字典
|       nameservers_cn.txt      中国主流名称服务器IP地址
|       fingerprints.json       检查子域接管风险的指纹
|       nameservers.txt         全球主流名称服务器IP地址
|       subnames_next.txt       下一层子域字典
|       public_suffix_list.dat  顶级域名后缀
|       srv_prefixes.json       常见SRV记录前缀名
|       subnames.txt            子域爆破常见字典
|
+---docs 有关文档
|       changes.md
|       collection_modules.md
|       contributors.md
|       installation_dependency.md
|       todo.md
|       troubleshooting.md
|       usage_example.svg
|       usage_help.en.md
|       usage_help.md
|
+---images
|       Database.png
|       Donate.png
|       Result.png
|
+---modules
|   +---autotake 自动接管模块
|   |       github.py
|   |
|   +---certificates 利用证书透明度收集子域模块
|   |       censys_api.py
|   |       certspotter.py
|   |       crtsh.py
|   |       entrust.py
|   |       google.py
|   |       spyse_api.py
|   |
|   +---check 常规检查收集子域模块
|   |       axfr.py
|   |       cdx.py
|   |       cert.py
|   |       csp.py
|   |       robots.py
|   |       sitemap.py
|   |
|   +---crawl 利用网上爬虫档案收集子域模块
|   |       archivecrawl.py
|   |       commoncrawl.py
|   |
|   +---datasets 利用DNS数据集收集子域模块
|   |       binaryedge_api.py
|   |       bufferover.py
|   |       cebaidu.py
|   |       chinaz.py
|   |       chinaz_api.py
|   |       circl_api.py
|   |       dnsdb_api.py
|   |       dnsdumpster.py
|   |       hackertarget.py
|   |       ip138.py
|   |       ipv4info_api.py
|   |       netcraft.py
|   |       passivedns_api.py
|   |       ptrarchive.py
|   |       qianxun.py
|   |       rapiddns.py
|   |       riddler.py
|   |       robtex.py
|   |       securitytrails_api.py
|   |       sitedossier.py
|   |       threatcrowd.py
|   |       wzpc.py
|   |       ximcx.py
|   |
|   +---dnsquery 利用DNS查询收集子域模块
|   |       mx.py
|   |       ns.py
|   |       soa.py
|   |       srv.py
|   |       txt.py
|   |
|   +---intelligence 利用威胁情报平台数据收集子域模块
|   |       alienvault.py
|   |       riskiq_api.py
|   |       threatbook_api.py
|   |       threatminer.py
|   |       virustotal.py
|   |       virustotal_api.py
|   |
|   \---search 利用搜索引擎发现子域模块
|           ask.py
|           baidu.py
|           bing.py
|           bing_api.py
|           exalead.py
|           fofa_api.py
|           gitee.py
|           github_api.py
|           google.py
|           google_api.py
|           shodan_api.py
|           so.py
|           sogou.py
|           yahoo.py
|           yandex.py
|           zoomeye_api.py
|
+---results 结果目录
+---test 测试目录
|       example.py
|
\---thirdparty 存放要调用的三方工具
    \---massdns
        |   LICENSE
        |   massdns_darwin_x86_64
        |   massdns_linux_i686
        |   massdns_linux_x86_64
        |   README.md
        |
        \---windows
            +---x64
            |       cygwin1.dll
            |       massdns_windows_amd64.exe
            |
            \---x86
                    cyggcc_s-1.dll
                    cygwin1.dll
                    massdns_windows_i686.exe
```
