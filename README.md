# OneForAll

[![Build Status](https://travis-ci.org/shmilylty/OneForAll.svg?branch=master)](https://travis-ci.org/shmilylty/OneForAll)
[![codecov](https://codecov.io/gh/shmilylty/OneForAll/branch/master/graph/badge.svg)](https://codecov.io/gh/shmilylty/OneForAll)
[![Maintainability](https://api.codeclimate.com/v1/badges/1287668a6b4c72af683e/maintainability)](https://codeclimate.com/github/shmilylty/OneForAll/maintainability)
[![License](https://img.shields.io/github/license/shmilylty/OneForAll)](./LICENSE)
[![python](https://img.shields.io/badge/python-3.6%20%7C%203.7%20%7C%203.8-blue)](./)
[![python](https://img.shields.io/badge/release-v0.0.4-brightgreen)](https://github.com/shmilylty/OneForAll/releases)

👊**OneForAll是一款功能强大的子域收集工具**  📝[English Document](./README.en.md)

![](./images/All_Might.jpg)

## 🎉项目简介

在渗透测试中信息收集的重要性不言而喻，子域收集是信息收集中必不可少且非常重要的一环，目前网上也开源了许多子域收集的工具，但是总是存在以下部分问题：

* **不够强大**，子域收集的接口不够多，不能做到对批量子域自动收集，没有自动子域解析，验证，FUZZ以及信息拓展等功能。
* **不够友好**，固然命令行模块比较方便，但是当可选的参数很多，要实现的操作复杂，用命令行模式就有点不够友好，如果有交互良好，高可操作的前端那么使用体验就会好很多。

* **缺少维护**，很多工具几年没有更新过一次，issues和PR是啥，不存在的。

* **效率问题**，没有利用多进程，多线程以及异步协程技术，速度较慢。

为了解决以上痛点，此项目应用而生，OneForAll一词是来自我喜欢的一部日漫《[我的英雄学院](https://manhua.fzdm.com/131/)》，它是一种通过一代代的传承不断变强的潜力无穷的顶级个性，目前[番剧](https://www.bilibili.com/bangumi/media/md7452/)也更新到了第三季了，欢迎大佬们入坑😄。正如其名，我希望OneForAll是一款集百家之长，功能强大的全面快速子域收集终极神器🔨。

目前OneForAll还在开发中，肯定有不少问题和需要改进的地方，欢迎大佬们提交[Issues](https://github.com/shmilylty/OneForAll/issues)和[PR](https://github.com/shmilylty/OneForAll/pulls)，用着还行给个小星星✨吧，目前有一个专门用于OneForAll交流和反馈QQ群👨‍👨‍👦‍👦：:[**824414244**](//shang.qq.com/wpa/qunwpa?idkey=125d3689b60445cdbb11e4ddff38036b7f6f2abbf4f7957df5dddba81aa90771)，也可以给我发邮件📧[admin@hackfun.org]。

## 👍功能特性

* **收集能力强大**，详细模块请阅读[收集模块说明](./docs/collection_modules.md)。
  1. 利用证书透明度收集子域（目前有6个模块：`censys_api`，`certdb_api`，`certspotter`，`crtsh`，`entrust`，`google`）

  2. 常规检查收集子域（目前有4个模块：域传送漏洞利用`axfr`，检查跨域策略文件`cdx`，检查HTTPS证书`cert`，检查内容安全策略`csp`，检查robots文件`robots`，检查sitemap文件`sitemap`，后续会添加检查NSEC记录，NSEC3记录等模块）

  3. 利用网上爬虫档案收集子域（目前有2个模块：`archivecrawl`，`commoncrawl`，此模块还在调试，该模块还有待添加和完善）

  4. 利用DNS数据集收集子域（目前有16个模块：`binaryedge_api`, `circl_api`, `hackertarget`, `riddler`, `bufferover`, `dnsdb`, `ipv4info`, `robtex`, `chinaz`, `dnsdb_api`, `netcraft`, `securitytrails_api`, `chinaz_api`, `dnsdumpster`, `ptrarchive`, `sitedossier`）

  5. 利用DNS查询收集子域（目前有1个模块：通过枚举常见的SRV记录并做查询来收集子域`srv`，该模块还有待添加和完善）

  6. 利用威胁情报平台数据收集子域（目前有5个模块：`riskiq_api`，`threatbook_api`，`threatminer`，`virustotal`，`virustotal_api`该模块还有待添加和完善）

  7. 利用搜索引擎发现子域（目前有15个模块：`ask`, `bing_api`, `fofa_api`, `shodan_api`, `yahoo`, `baidu`, `duckduckgo`, `google`, `so`, `yandex`, `bing`, `exalead`, `google_api`, `sogou`, `zoomeye_api`），在搜索模块中除特殊搜索引擎，通用的搜索引擎都支持自动排除搜索，全量搜索，递归搜索。

* **处理功能强大**，发现的子域结果支持自动去除，自动DNS解析，HTTP请求探测，自动移除无效子域，拓展子域的Banner信息，最终支持的导出格式有`csv`, `tsv`, `json`, `yaml`, `html`, `xls`, `xlsx`, `dbf`, `latex`, `ods`。

* **速度极速**，[收集模块](./oneforall/collect.py)使用多线程调用，[爆破模块](./oneforall/aiobrute.py)使用异步多进程多协程，DNS解析和HTTP请求使用异步多协程。

## 🚀上手指南

由于该项目**处于开发中**，会不断进行更新迭代，下载使用最好**克隆**最新项目。

**🐍安装要求**

1. Python 3.6-3.7

**✔安装步骤**

1. 下载更新

   ```bash
   git clone https://github.com/shmilylty/OneForAll.git
   ```

   ❗如果你之前已经克隆了项目运行之前请**备份**自己修改过的文件到项目外的地方（如**config.py**），然后执行以下命令**更新**项目：

   ```bash
   git fetch --all
   git reset --hard origin/master
   git pull
   ```

2. 安装依赖

   * 使用pipenv

     ```bash
     pip3 install pipenv
     cd OneForAll/
     pipenv install --python 3.7
     cd oneforall
     pipenv run python3 oneforall.py --help
     ```

   * 使用pip3
   
     ```bash
     cd OneForAll/
     pip3 install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
     cd oneforall/
     python3 oneforall.py --help
     ```


如果在安装依赖过程中发现编译某个依赖库失败时可以参考[编译失败解决方法](./docs/building_fail_solution.md)，如果还没有解决欢迎加群反馈。

**✨使用演示**

```bash
python3 oneforall.py --target example.com run
```

![Example](./docs/usage_example.svg)

**🤔使用帮助**

命令行参数只提供了一些常用参数，更多详细的参数配置请见[config.py](./oneforall/config.py)，如果你认为有些参数是命令界面经常使用到的或缺少了什么参数等问题非常欢迎反馈。由于众所周知的原因，如果要使用一些被墙的收集接口请先到[config.py](./oneforall/config.py)配置代理，有些收集模块需要提供API（大多都是可以注册账号免费获取），如果需要使用请到[config.py](./oneforall/config.py)配置API信息，如果不使用请忽略有关报错提示。（详细模块请阅读[收集模块说明](./docs/collection_modules.md)）

OneForAll命令行界面基于[Fire](https://github.com/google/python-fire/)实现，有关Fire更高级使用方法请参阅[使用Fire CLI](https://github.com/google/python-fire/blob/master/docs/using-cli.md)，有任何使用疑惑欢迎加群交流。

oneforall.py是主程序入口，oneforall.py里有调用aiobrute.py和dbexport.py，为了方便进行子域爆破和数据库导出独立出了aiobrute.py和dbexport.py，这两个文件可以单独运行，并且所接受参数要更丰富一点。

1. oneforall.py使用帮助

   ```bash
   pipenv run python oneforall.py --help
   ```
   ```bash
   NAME
       oneforall.py - OneForAll是一款功能强大的子域收集工具
   
   SYNOPSIS
       oneforall.py --target=TARGET <flags>
   
   DESCRIPTION
       Version: 0.0.2
       Project: https://github.com/shmilylty/OneForAll/
   
       Example:
           python oneforall.py --target example.com run
           python oneforall.py --target example.com --brute True --port medium --valid 1 run
           python oneforall.py --target ./domains.txt --format csv --path= ./result.csv  --output True run
   
       Note:
           参数valid可选值有1，0，None，分别表示导出有效，无效，全部子域
           参数port可选值有'small', 'medium', 'large', 'xlarge'，详见config.py配置
           参数format可选格式有'csv','tsv','json','yaml','html','xls','xlsx','dbf','latex','ods'
           参数path为None会根据format参数和域名名称在项目结果目录生成相应文件
   
   ARGUMENTS
       TARGET
           单个域名或者每行一个域名的文件路径
   
   FLAGS
       --brute=BRUTE
           是否使用爆破模块（默认禁用）
       --port=PORT
           HTTP请求验证的端口范围（默认medium）
       --valid=VALID
           导出子域的有效性（默认1）
       --path=PATH
           导出路径(默认None)
       --format=FORMAT
           导出格式（默认xlsx）
       --output=OUTPUT
           是否将导出数据输出到终端（默认False）
   ```

2. aiobrute.py使用帮助

   关于泛解析问题处理程序首先会访问一个随机的子域判断是否泛解析，如果使用了泛解析则是通过以下判断处理：
   - 一是主要是与泛解析的IP集合和TTL值做对比，可以参考[这篇文章](http://sh3ll.me/archives/201704041222.txt)。
   - 二是多次解析到同一IP集合次数（默认设置为10，可以在config.py设置大小）
   - 考虑爆破效率问题目前还没有加上HTTP响应体相似度对比和响应体内容判断
   经过测试在16核心的CPU，使用16进程64协程，100M带宽的环境下，设置任务分割为50000，跑两百万字典大概10分钟左右跑完，大概3333个子域每秒。

   ```bash
   pipenv run python aiobrute.py --help
   ```

   ```bash
    NAME
        aiobrute.py - OneForAll多进程多协程异步子域爆破模块

    SYNOPSIS
        aiobrute.py COMMAND | --target=TARGET <flags>

    DESCRIPTION
        Example：
            python aiobrute.py --target example.com run
            python aiobrute.py --target ./domains.txt run
            python aiobrute.py --target example.com --processes 4 --coroutine 64 --wordlist data/subdomains.txt run
            python aiobrute.py --target example.com --recursive True --depth 2 --namelist data/next_subdomains.txt run
            python aiobrute.py --target www.{fuzz}.example.com --fuzz True --rule [a-z][0-9] run

        Note:
            参数segment的设置受CPU性能，网络带宽，运营商限制等问题影响，默认设置500个子域为一任务组，
            当你觉得你的环境不受以上因素影响，当前爆破速度较慢，那么强烈建议根据字典大小调整大小：
            十万字典建议设置为5000，百万字典设置为50000

    ARGUMENTS
        TARGET
            单个域名或者每行一个域名的文件路径

    FLAGS
        --processes=PROCESSES
            爆破的进程数(默认CPU核心数)
        --coroutine=COROUTINE
            每个爆破进程下的协程数(默认16)
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
            是否使用fuzz模式进行爆破(默认False，开启必须指定fuzz正则规则)
        --rule=RULE
            fuzz模式使用的正则规则(默认使用config.py配置)

   ```

3. dbexport.py使用帮助

   ```bash
   pipenv run python dbexport.py --help
   ```

   ```bash
   NAME
       dbexport.py - OneForAll数据库导出模块
   
   SYNOPSIS
       dbexport.py TABLE <flags>
   
   DESCRIPTION
       Example:
           python dbexport.py --db result.db --table name --format csv --output False
           python dbexport.py --db result.db --table name --format csv --path= ./result.csv
   
       Note:
           参数valid可选值1，0，None，分别表示导出有效，无效，全部子域
           参数format可选格式：'csv', 'tsv', 'json', 'yaml', 'html', 'xls', 'xlsx', 'dbf', 'latex', 'ods'
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
       --output=OUTPUT
           是否将导出数据输出到终端(默认False)
   
   NOTES
       You can also use flags syntax for POSITIONAL ARGUMENTS
   ```

## 👏主要框架

* [aiodns](https://github.com/saghul/aiodns) - 简单DNS异步解析库。
* [aiohttp](https://github.com/aio-libs/aiohttp) - 异步http客户端/服务器框架
* [aiomultiprocess](https://github.com/jreese/aiomultiprocess) - 将Python代码提升到更高的性能水平(multiprocessing和asyncio结合，实现异步多进程多协程)
* [beautifulsoup4](https://pypi.org/project/beautifulsoup4/) - 可以轻松从HTML或XML文件中提取数据的Python库
* [fire](https://github.com/google/python-fire) - Python Fire是一个纯粹根据任何Python对象自动生成命令行界面（CLI）的库
* [loguru](https://github.com/Delgan/loguru) - 旨在带来愉快的日志记录Python库
* [records](https://github.com/kennethreitz/records) - Records是一个非常简单但功能强大的库，用于对大多数关系数据库进行最原始SQL查询。
* [requests](https://github.com/psf/requests) - Requests 唯一的一个非转基因的 Python HTTP 库，人类可以安全享用。
* [tqdm](https://github.com/tqdm/tqdm) - 适用于Python和CLI的快速，可扩展的进度条库

感谢这些伟大优秀的Python库！

## 🌲目录结构

```bash
D:.
|
+---.github
+---docs
|       collection_modules.md 收集模块说明
+---images
\---oneforall
    |   aiobrute.py   异步多进程多协程子域爆破模块，可以单独运行
    |   collect.py    各个收集模块上层调用
    |   config.py     配置文件
    |   dbexport.py   数据库导出模块，可以单独运行
    |   domains.txt   要批量爆破的域名列表
    |   oneforall.py  OneForAll主入口，可以单独运行
    |   __init__.py
    |
    +---common 公共调用模块
    +---data   存放一些所需数据
    |       next_subdomains.txt     下一层子域字典
    |       public_suffix_list.dat  顶级域名后缀 
    |       srv_names.json          常见SRV记录前缀名
    |       subdomains.txt          子域爆破常见字典
    |
    \---modules 
        +---certificates     利用证书透明度收集子域模块
        +---check            常规检查收集子域模块
        +---crawl            利用网上爬虫档案收集子域模块
        +---datasets         利用DNS数据集收集子域模块
        +---dnsquery         利用DNS查询收集子域模块
        +---intelligence     利用威胁情报平台数据收集子域模块
        \---search           利用搜索引擎发现子域模块

```

## 🙏贡献

非常热烈欢迎各位大佬一起完善本项目！

## ⌛后续计划

- [ ] 子域收集模块优化
- [ ] 子域接管功能实现
- [ ] 子域收集爬虫实现
- [ ] 操作强大交互人性的前端界面实现

更多详细信息请阅读[TODO.md](./TODO.md)。

## 🔖版本控制

该项目使用[SemVer](https://semver.org/)语言化版本格式进行版本管理，你可以在[Releases](https://github.com/shmilylty/OneForAll/releases)查看可用版本。

## 👨‍💻作者

* **[Jing Ling](https://github.com/shmilylty)**
  * 核心开发

* **[Black Star](https://github.com/blackstar24)**
  * 模块贡献

* [**iceMatcha**](https://github.com/iceMatcha)
  * bug调试

*你也可以在[CONTRIBUTORS.md](./CONTRIBUTORS.md)中参看所有参与该项目的开发者。*

## 📄版权

该项目签署了GPL-3.0授权许可，详情请参阅[LICENSE.md](./LICENSE.md)。

## 😘鸣谢

感谢网上开源的各个子域收集项目！

感谢[A-Team](https://github.com/QAX-A-Team)大哥们热情无私的问题解答！

## 📜免责声明 ##

本工具仅限于安全研究与教学使用，用户使用本工具所造成的所有后果，由用户承担全部法律及连带责任，本项目所有作者和贡献者不承担任何法律及连带责任。
