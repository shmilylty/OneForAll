# 使用帮助

命令行参数只提供了一些常用参数，更多详细的参数配置请见[config.py](https://github.com/shmilylty/OneForAll/tree/master/oneforall/config/setting.py)，如果你认为有些参数是命令界面经常使用到的或缺少了什么参数等问题非常欢迎反馈。由于众所周知的原因，如果要使用一些被墙的收集接口请先到[config.py](https://github.com/shmilylty/OneForAll/tree/master/oneforall/config/setting.py)配置代理，有些收集模块需要提供API（大多都是可以注册账号免费获取），如果需要使用请到[api.py](https://github.com/shmilylty/OneForAll/tree/master/oneforall/config/api.py)配置API信息，如果不使用请忽略有关报错提示。（详细模块请阅读[收集模块说明](https://github.com/shmilylty/OneForAll/tree/master/docs/collection_modules.md)）

OneForAll命令行界面基于[Fire](https://github.com/google/python-fire/)实现，有关Fire更高级使用方法请参阅[使用Fire CLI](https://github.com/google/python-fire/blob/master/docs/using-cli.md)。

[oneforall.py](https://github.com/shmilylty/OneForAll/tree/master/oneforall/oneforall.py)是主程序入口，oneforall.py可以调用[aiobrute.py](https://github.com/shmilylty/OneForAll/tree/master/oneforall/aiobrute.py)，[takerover.py](https://github.com/shmilylty/OneForAll/tree/master/oneforall/takerover.py)及[dbexport.py](https://github.com/shmilylty/OneForAll/tree/master/oneforall/dbexport.py)等模块，为了方便进行子域爆破独立出了aiobrute.py，为了方便进行子域接管风险检查独立出了takerover.py，为了方便数据库导出独立出了dbexport.py，这些模块都可以单独运行，并且所接受参数要更丰富一点。

❗注意：当你在使用过程中遇到一些问题或者疑惑时，请先到[Issues](https://github.com/shmilylty/OneForAll/issues)里使用搜索找找答案，还可以参阅[常见问题与回答](https://github.com/shmilylty/OneForAll/tree/master/docs/Q&A.md)。

1. oneforall.py使用帮助

   ```bash
   python oneforall.py --help
   ```
   ```bash
   NAME
       oneforall.py - OneForAll使用帮助
   
   SYNOPSIS
       oneforall.py COMMAND | <flags>
   
   DESCRIPTION
       OneForAll是一款功能强大的子域收集工具
   
       Example:
           python3 oneforall.py version
           python3 oneforall.py check
           python3 oneforall.py --target example.com run
           python3 oneforall.py --targets ./domains.txt run
           python3 oneforall.py --target example.com --alive False run
           python3 oneforall.py --target example.com --brute True run
           python3 oneforall.py --target example.com --port medium run
           python3 oneforall.py --target example.com --format csv run
           python3 oneforall.py --target example.com --dns False run
           python3 oneforall.py --target example.com --req False run
           python3 oneforall.py --target example.com --takeover False run
           python3 oneforall.py --target example.com --show True run
   
       Note:
           --port   small/medium/large  详见./config/setting.py(默认small)
           --format csv/json (结果格式，默认CSV)
           --path   结果路径(默认None，自动生成)

   FLAGS
       --target=TARGET
           单个域名(必须提供target或targets参数)
       --targets=TARGETS
           每行一个域名的文件路径
       --brute=BRUTE
           使用爆破模块(默认True)
       --dns=DNS
           开启子域解析(默认True)
       --req=REQ
           开启子域请求(默认True)
       --port=PORT
           请求验证的端口范围(默认medium)
       --alive=ALIVE
           只导出存活子域(默认False)
       --format=FORMAT
           结果格式(默认csv)
       --path=PATH
           结果路径(默认None，自动生成)
       --takeover=TAKEOVER
           开启子域接管检查(默认False)

   COMMANDS
       COMMAND is one of the following:

       check
         检查新版本并退出

       version
         打印版本信息并退出
   ```

2. aiobrute.py使用帮助

   关于泛解析问题处理程序首先会访问一个随机的子域判断是否泛解析，如果使用了泛解析则是通过以下判断处理：
   - 一是主要是与泛解析的IP集合和TTL值做对比，可以参考[这篇文章](http://sh3ll.me/archives/201704041222.txt)。
   
   - 二是多次解析到同一IP集合次数（默认设置为10，可以在config.py设置大小）
   
   - 考虑爆破效率问题目前还没有加上HTTP响应体相似度对比和响应体内容判断

   ```bash
   python aiobrute.py --help
   ```

   ```bash
   NAME
       brute.py - OneForAll子域爆破模块
   
   SYNOPSIS
       brute.py <flags>
   
   DESCRIPTION
       Example：
            brute.py --target domain.com --word True run
            brute.py --targets ./domains.txt --word True run
            brute.py --target domain.com --word True --coroutine 2000 run
            brute.py --target domain.com --word True --wordlist subnames.txt run
            brute.py --target domain.com --word True --recursive True --depth 2 run
            brute.py --target d.com --fuzz True --place m.*.d.com --rule '[a-z]' run
            brute.py --target d.com --fuzz True --place m.*.d.com --fuzzlist subnames.txt run

       Note:
           --format rst/csv/tsv/json/yaml/html/jira/xls/xlsx/dbf/latex/ods (结果格式，默认CSV)
           --path   导出路径(默认None，自动生成)

       FLAGS
           --target=TARGET
               单个域名(必须提供target或targets参数)
           --targets=TARGETS
               每行一个域名的文件路径
           --process=PROCESS
               爆破的进程数(默认CPU核心数)
           --coroutine=COROUTINE
               每个爆破进程下的协程数(默认2000)
           --wordlist=WORDLIST
               指定爆破所使用的字典路径(默认使用config.py配置)
           --recursive=RECURSIVE
               是否使用递归爆破(默认False)
           --depth=DEPTH
               递归爆破的深度(默认2)
           --nextlist=NEXTLIST
               指定递归爆破所使用的字典路径(默认使用config.py配置)
           --fuzz=FUZZ
               是否使用fuzz模式进行爆破(默认False)
           --rule=RULE
               fuzz模式使用的正则规则(默认使用config.py配置)
           --fuzzlist=FUZZLIST
               指定fuzz模式所使用的字典路径(默认使用config.py配置)
           --export=EXPORT
               是否导出爆破结果(默认True)
           --alive=ALIVE
               只导出存活子域(默认False)
           --format=FORMAT
               导出格式(默认csv)
           --path=PATH
               导出路径(默认None)
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
       dbexport.py TARGET <flags>
   
   DESCRIPTION
       Example:
           python3 dbexport.py --target name --format csv --dir= ./result.csv
           python3 dbexport.py --db result.db --target name --show False
           python3 dbexport.py --target table_name --tb True --show False
   
       Note:
           --type   target/table        要导出的目标类型(默认target)
           --format rst/csv/tsv/json/yaml/html/jira/xls/xlsx/dbf/latex/ods (结果格式，默认CSV)
           --path   结果路径(默认None，自动生成)
   
   POSITIONAL ARGUMENTS
       TARGET
           要导出的目标类型
   
   FLAGS
       --type=TYPE
           要导出的目标类型(默认target)
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
