# 使用帮助

oneforall.py是主程序入口，oneforall.py里有调用aiobrute.py和dbexport.py，为了方便进行子域爆破和数据库导出独立出了aiobrute.py和dbexport.py，这两个文件可以单独运行，并且所接受参数要更丰富一点。

1. oneforall.py使用帮助

   ```bash
   python oneforall.py --help
   ```
   ```bash
   NAME
       oneforall.py - OneForAll是一款功能强大的子域收集工具
   
   SYNOPSIS
       oneforall.py --target=TARGET <flags>
   
   DESCRIPTION
       Version: 0.0.4
       Project: https://git.io/fjHT1
   
       Example:
           python3 oneforall.py --target example.com run
           python3 oneforall.py --target ./domains.txt run
           python3 oneforall.py --target example.com --brute True run
           python3 oneforall.py --target example.com --verify False run
           python3 oneforall.py --target example.com --valid None run
           python3 oneforall.py --target example.com --port medium run
           python3 oneforall.py --target example.com --format csv run
           python3 oneforall.py --target example.com --show True run
   
       Note:
           参数valid可选值1，0，None分别表示导出有效，无效，全部子域
           参数verify为True会尝试解析和请求子域并根据结果给子域有效性打上标签
           参数port可选值有'small', 'medium', 'large', 'xlarge'，详见config.py配置
           参数format可选格式有'csv', 'tsv', 'json', 'yaml', 'html', 'xls', 'xlsx',
                             'dbf', 'latex', 'ods'
           参数path为None会根据format参数和域名名称在项目结果目录生成相应文件
   
   ARGUMENTS
       TARGET
           单个域名或者每行一个域名的文件路径(必需参数)
   
   FLAGS
       --brute=BRUTE
           使用爆破模块(默认False)
       --verify=VERIFY
           验证子域有效性(默认True)
       --port=PORT
           请求验证的端口范围(默认medium)
       --valid=VALID
           导出子域的有效性(默认1)
       --path=PATH
           导出路径(默认None)
       --format=FORMAT
           导出格式(默认xlsx)
       --show=SHOW
           终端显示导出数据(默认False)
   ```

2. aiobrute.py使用帮助

   关于泛解析问题处理程序首先会访问一个随机的子域判断是否泛解析，如果使用了泛解析则是通过以下判断处理：
   - 一是主要是与泛解析的IP集合和TTL值做对比，可以参考[这篇文章](http://sh3ll.me/archives/201704041222.txt)。
   - 二是多次解析到同一IP集合次数（默认设置为10，可以在config.py设置大小）
   - 考虑爆破效率问题目前还没有加上HTTP响应体相似度对比和响应体内容判断
   经过测试在16核心的CPU，使用16进程64协程，100M带宽的环境下，设置任务分割为50000，跑两百万字典大概10分钟左右跑完，大概3333个子域每秒。

   ```bash
   python aiobrute.py --help
   ```

   ```bash
   NAME
       aiobrute.py - OneForAll多进程多协程异步子域爆破模块
   
   SYNOPSIS
       aiobrute.py --target=TARGET <flags>
   
   DESCRIPTION
       Example：
           python3 aiobrute.py --target example.com run
           python3 aiobrute.py --target ./domains.txt run
           python3 aiobrute.py --target example.com --process 4 --coroutine 64 run
           python3 aiobrute.py --target example.com --wordlist subdomains.txt run
           python3 aiobrute.py --target example.com --recursive True --depth 2 run
           python3 aiobrute.py --target m.{fuzz}.a.bz --fuzz True --rule [a-z] run
   
       Note:
           参数segment的设置受CPU性能，网络带宽，运营商限制等问题影响，默认设置500个子域为任务组，
           当你觉得你的环境不受以上因素影响，当前爆破速度较慢，那么强烈建议根据字典大小调整大小：
           十万字典建议设置为5000，百万字典设置为50000
           参数valid可选值1，0，None，分别表示导出有效，无效，全部子域
           参数format可选格式：'csv', 'tsv', 'json', 'yaml', 'html', 'xls', 'xlsx',
                             'dbf', 'latex', 'ods'
           参数path为None会根据format参数和域名名称在项目结果目录生成相应文件
   
   ARGUMENTS
       TARGET
           单个域名或者每行一个域名的文件路径
   
   FLAGS
       --process=PROCESS
           爆破的进程数(默认CPU核心数)
       --coroutine=COROUTINE
           每个爆破进程下的协程数(默认64)
       --wordlist=WORDLIST
           指定爆破所使用的字典路径(默认使用config.py配置)
       --segment=SEGMENT
           爆破任务分割(默认500)
       --recursive=RECURSIVE
           是否使用递归爆破(默认False)
       --depth=DEPTH
           递归爆破的深度(默认2)
       --namelist=NAMELIST
           指定递归爆破所使用的字典路径(默认使用config.py配置)
       --fuzz=FUZZ
           是否使用fuzz模式进行爆破(默认False，开启须指定fuzz正则规则)
       --rule=RULE
           fuzz模式使用的正则规则(默认使用config.py配置)
       --export=EXPORT
           是否导出爆破结果(默认True)
       --valid=VALID
           导出子域的有效性(默认None)
       --format=FORMAT
           导出格式(默认xlsx)
       --path=PATH
           导出路径(默认None)
       --show=SHOW
           终端显示导出数据(默认False)
   
   ```


3. takeover.py使用帮助

   ```bash
   python takeover.py --help
   ```
   
   ```bash
   NAME
    takeover.py - OneForAll多线程子域接管风险检查模块
   
   
    SYNOPSIS
        takeover.py COMMAND | --target=TARGET <flags>
   
    DESCRIPTION
        Example:
            python3 takeover.py --target www.example.com  --format csv run
            python3 takeover.py --target ./subdomains.txt --thread 10 run
   
        Note:
            参数format可选格式有'txt', 'rst', 'csv', 'tsv', 'json', 'yaml', 'html',
                              'jira', 'xls', 'xlsx', 'dbf', 'latex', 'ods'
            参数dpath为None默认使用OneForAll结果目录
   
    ARGUMENTS
        TARGET
            单个子域或者每行一个子域的文件路径(必需参数)
   
    FLAGS
        --thread=THREAD
            线程数(默认100)
        --dpath=DPATH
            导出目录(默认None)
        --format=FORMAT
            导出格式(默认xls)
   
   ```


4. dbexport.py使用帮助

   ```bash
   python dbexport.py --help
   ```

   ```bash
   NAME
       dbexport.py - OneForAll数据库导出模块
   
   SYNOPSIS
       dbexport.py TABLE <flags>
   
   DESCRIPTION
       Example:
           python3 dbexport.py --table name --format csv --path= ./result.csv
           python3 dbexport.py --db result.db --table name --show False
   
       Note:
           参数port可选值有'small', 'medium', 'large', 'xlarge'，详见config.py配置
           参数format可选格式有'csv', 'tsv', 'json', 'yaml', 'html', 'xls', 'xlsx',
                             'dbf', 'latex', 'ods'
           参数path为None会根据format参数和域名名称在项目结果目录生成相应文件
   
   POSITIONAL ARGUMENTS
       TABLE
           要导出的表
   
   FLAGS
       --db=DB
           要导出的数据库路径(默认为results/result.sqlite3)
       --valid=VALID
           导出子域的有效性(默认None)
       --path=PATH
           导出路径(默认None)
       --format=FORMAT
           导出格式(默认xlsx)
       --show=SHOW
           终端显示导出数据(默认False)
   ```