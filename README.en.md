# OneForAll

[![Build Status](https://travis-ci.org/shmilylty/OneForAll.svg?branch=master)](https://travis-ci.org/shmilylty/OneForAll)
[![codecov](https://codecov.io/gh/shmilylty/OneForAll/branch/master/graph/badge.svg)](https://codecov.io/gh/shmilylty/OneForAll)
[![Maintainability](https://api.codeclimate.com/v1/badges/1287668a6b4c72af683e/maintainability)](https://codeclimate.com/github/shmilylty/OneForAll/maintainability)
[![License](https://img.shields.io/github/license/shmilylty/OneForAll)](https://github.com/shmilylty/OneForAll/tree/master/LICENSE)
[![python](https://img.shields.io/badge/python-3.8-blue)](https://github.com/shmilylty/OneForAll/tree/master/)
[![python](https://img.shields.io/badge/release-v0.0.8-brightgreen)](https://github.com/shmilylty/OneForAll/releases)

👊**OneForAll is a powerful subdomain collection tool**  📝[中文文档](https://github.com/shmilylty/OneForAll/tree/master/README.md)

![](https://raw.githubusercontent.com/shmilylty/OneForAll/master/images/All_Might.jpg)

## 🎉Project profile

Project home：[https://shmilylty.github.io/OneForAll/](https://shmilylty.github.io/OneForAll/)

Project address ：[https://github.com/shmilylty/OneForAll](https://github.com/shmilylty/OneForAll)

The importance of information collection in penetration testing is self-evident. Subdomain collection is an essential and very important part of information collection. At present, there are many open source tools for subdomain collection on the Internet, but there are always some of the following problems:

* **Not powerful enough**，there are not enough interfaces to collect subdomains automatically, and there are no functions such as automatic subdomain resolve, verification, FUZZ and information expansion.
* **Not friendly enough**，although the command line module is more convenient, but when there are a lot of optional parameters and the operation to be implemented is complex, using command line mode is a bit unfriendly. If there is a good interaction, With a highly operable front end, the experience will be much better.

* **Lack of maintenance**，Many tools have not been updated once in years, what issues and PR are, do not exist.

* **Efficiency issues**，do not take advantage of multi-process, multi-threading and asynchronous cooperation technology, the speed is slow.

In order to solve the above pain points, the term OneForAll comes from one of my favorite Japanese cartoons,《[My Hero Academia](https://manhua.fzdm.com/131/)》.It's a top personality that has grown from generation to generation, and now [TV series](https://www.bilibili.com/bangumi/media/md7452/)has been updated to season 4. As its name suggests, I want OneForAll to be a collection of 100 strong, powerful and fast subdomains that collect the ultimate artifact 🔨.

At present, OneForAll is still under development, there must be a lot of problems and areas for improvement. Welcome to submit [Issues](https://github.com/shmilylty/OneForAll/issues) or [PR](https://github.com/shmilylty/OneForAll/pulls)，If you like, give it to a little star ✨，At present, there is a special QQ group for OneForAll communication and feedback: 👨‍👨‍👦‍👦：:[**824414244**](//shang.qq.com/wpa/qunwpa?idkey=125d3689b60445cdbb11e4ddff38036b7f6f2abbf4f7957df5dddba81aa90771)，You can also 📧[email](mailto://admin@hackfun.org) or [tweet](https://twitter.com/jinglingbiaodi) to me .

## 👍Features

* **Powerful collection capability**，For more information, please see [collection module description](https://github.com/shmilylty/OneForAll/tree/master/docs/collection_modules.md).
  1. Collect subdomains using certificate transparency (there are currently 6 modules: `censys_api`，`spyse_api`，`certspotter`，`crtsh`，`entrust`，`google`）

  2. General check collection subdomains (there are currently 4 modules: domain transfer vulnerability exploitation`cdx`, cross-domain policy file `cdx`, HTTPS certificate `cert`, content security policy `csp`, robots file `robots`, and sitemap file `sitemap`. Check NSEC record, NSEC3 record and other modules will be added later).

  3.  Collect subdomains using web crawler files (there are currently two modules: `archirawl`, `commoncrawl`, which is still being debugged and needs to be added and improved). 

  4.  Collect subdomains using DNS datasets (there are currently 22 modules: `ip138`, `ximcx`, `CeBaidu`, `binaryedge_api`, `circl_api`, `hackertarget`, `riddler`, `bufferover`, `dnsdb`, `ipv4info`, `robtex`, `chinaz`, `dnsdb_api`, `netcraft`, `securitytrails_api`, `chinaz_api`, `dnsdumpster`, `passivedns_api`,  `ptrarchive`, `sitedossier`,`threatcrowd`）

  5.  Collect subdomains using DNS queries (there is currently a module to collect subdomains `srv` by enumerating common SRV records and making queries, which needs to be added and improved). 

  6.  Collect subdomains using threat intelligence platform data (there are currently 6 modules: `alienvault`, `riskiq_ api`, `threatbook_ api`, `threatkeeper `, `virustotal`, `virustotal_ api`, which need to be added and improved).

  7.  Use search engines to discover subdomains (there are currently 16 modules: `ask`, `bing_ api`, `fofa_ api`, `shodan_ api`, `yahoo`, `baidu`, `duckduckgo`, `github`, `google`, `so`, `yandex`, `bing`, `exalead`, `google_ api`, `sogou`, `zoomeye_ api`), except for special search engines in the search module. General search engines support automatic exclusion of search, full search, recursive search. 
* **Support subdomain blasting**，This module has both conventional dictionary blasting and custom fuzz mode. It supports batch blasting and recursive blasting, and automatically judges pan-parsing and processing.
* **Support subdmain verification**，default to enable subdomain verification, automatically resolve subdomain DNS, automatically request subdomain to obtain title and banner, and comprehensively determine subdomain survival.
* **Support subdomain takeover**，By default, subdomain takeover risk checking is enabled. Automatic subdomain takeover is supported (only Github, remains to be improved at present), and batch inspection is supported.
* **Powerful processing feature**，The found subdomain results support automatic removal, automatic DNS parsing, HTTP request detection, automatic filtering of valid subdomains, and expansion of Banner information for subdomains. The final supported export formats are `txt`, `rst`, `csv`, `tsv`, `json`, `yaml`, `html`, `xls`, `xlsx`, `dbf`, `latex`, `ods`.
* **Very fast**，[collection module](https://github.com/shmilylty/OneForAll/tree/master/oneforall//collect.py) uses multithreaded calls, [blasting module](https://github.com/shmilylty/OneForAll/tree/master/oneforall/aiobrute.py) uses asynchronous multiprocess and multiprogramming, and DNS parsing and HTTP requests use asynchronous multiprogramming in subdomain verification. Multithreaded check [subdomain takeover](https://github.com/shmilylty/OneForAll/tree/master/oneforall/takeover.py) risk.
* **Good experience**，Each module has a progress bar, and the results of each module are saved asynchronously.

## 🚀Start Guide

📢Currently, the project is **under development**, so it will continue to update iterations. It is best to **clone** the project when downloading and using OneForAll. Please take a moment to read this document to help you quickly get familiar with OneForAll!

**🐍Installation requirements**

OneForAll is developed and tested based on [Python 3.8.0](https://www.python.org/downloads/release/python-380/). For more information on installing the Python environment, please see [Python 3 installation Guide](https://pythonguidecn.readthedocs.io/zh/latest/starting/installation.html#python-3) . Run the following command to check the Python and pip3 versions:
```bash
python -V
pip3 -V
```
If you see the following output, there is no problem with the Python environment:
```bash
Python 3.8.0
pip 19.2.2 from C:\Users\shmilylty\AppData\Roaming\Python\Python37\site-packages\pip (python 3.8)
```

**✔Installation steps (Git version)**

1. **Download**
   
   This project has been mirrored in [Gitee](https://gitee.com/shmilylty/OneForAll.git). If you are in China, it is recommended that you use Gitee for cloning, which is faster:

   ```bash
   git clone https://gitee.com/shmilylty/OneForAll.git
   ```
   or：
   ```bash
   git clone https://github.com/shmilylty/OneForAll.git
   ```

2. **Installation**
   
   You can install OneForAll dependencies via pip3 (if you are familiar with [pipenv](https://docs.pipenv.org/en/latest/), then it is recommended that you use [pipenv install dependencies](https://github.com/shmilylty/OneForAll/tree/master/docs/Installation_dependency.md), the following is an example of using **pip3** to install dependencies under **Windows system**: (Note: If your Python3 is installed in the system Program Files In the directory, such as: `C:\Program Files\Python38`, then run the command prompt cmd as an administrator to execute the following command!)
```bash
   cd OneForAll/
   python -m pip install -U pip setuptools wheel
   pip3 install -r requirements.txt
   cd oneforall/
   python oneforall.py --help
```
​      For other system platforms, please refer to [dependency installation](https://github.com/shmilylty/OneForAll/tree/master/docs/installation_dependency.md). If you find that compiling a dependent library fails during the installation dependencies, Refer to the solution in the [Q&A](https://github.com/shmilylty/OneForAll/tree/master/docs/Q&A.md) documentation, if not resolved, welcome feedback.

3. **Update**

   ❗Note: If you have cloned the project before, please **back** up your own modified files (such as **config.py**) to the location outside the project before updating, then execute the following command **update** project:

   ```bash
   git fetch --all
   git reset --hard origin/master
   git pull
   ```

**✔Installation steps (Docker version)**

Method 1: directly pull the deployed image (not updated in time)

```shell
docker pull tardis07/oneforall
docker run -it oneforall
```

Method 2: build from `Dockerfile` (same as git version)

```shell
docker build -t oneforall .
docker run -it oneforall
```

**✨Demonstration**

1. If you are installing dependencies through pip3, run the example using the following command: 
    ```bash
    cd oneforall/
    python3 oneforall.py --target example.com run
    ```

    ![Example](./docs/usage_example.svg)

2. If you install dependencies through pipenv, run the example using the following command: 
   ```bash
   cd oneforall/
   pipenv run python oneforall.py --target example.com run
   ```

**🤔Help**

The command line parameters only provide some common parameters. For more detailed parameter configuration, please see [config.py](https://github.com/shmilylty/OneForAll/tree/master/oneforall/config.py) if you think Some parameters are frequently used in the command interface or missing parameters. Feedback is welcome. For well-known reasons, if you want to use some of the wall's collection interface, please go to [config.py](https://github.com/shmilylty/OneForAll/tree/master/oneforall/config.py) to configure the proxy, some collection Modules need to provide APIs (most of which are freely available for registered accounts). If you need to use them, please go to [config.py](https://github.com/shmilylty/OneForAll/tree/master/oneforall/config.py) to configure the API. Information, if not used, please ignore the error message. (For detailed modules, please read [collection module description](https://github.com/shmilylty/OneForAll/tree/master/docs/collection_modules.md))

The OneForAll command line interface is based on [Fire](https://github.com/google/python-fire/). For more advanced usage of Fire, please refer to [using the Fire CLI](https://github.com/google/Python-fire/blob/master/docs/using-cli.md), if you have any doubts during the use, please feel free to give me feedback.

[oneforall.py](https://github.com/shmilylty/OneForAll/tree/master/oneforall/oneforall.py) is the main program entry, and oneforall.py can call [aiobrute.py](https://github.com/shmilylty/OneForAll/tree/master/oneforall/aiobrute.py), [takerover.py](https://github.com/shmilylty/OneForAll/tree/master/oneforall/takerover.py) and [dbexport.py ](https://github.com/shmilylty/OneForAll/tree/master/oneforall/dbexport.py) and other modules, in order to facilitate the sub-field blasting, aiobrute.py is isolated independently, in order to facilitate the subdomain takeover risk check independently takeover.py, in order to facilitate the database export independently dbexport.py, these modules can be run separately, and the parameters accepted are more abundant.

❗ Note: When you encounter some problems or doubts during use, please use [Issues](https://github.com/shmilylty/OneForAll/issues) to search for answers. Also see [Q&A](https://github.com/shmilylty/OneForAll/tree/master/docs/Q&A.md).

1. **oneforall.py help**

   ```bash
   python oneforall.py --help
   ```
   ```bash
   NAME
       oneforall.py - OneForAll is a powerful subdomain collection tool
   
   SYNOPSIS
       oneforall.py --target=TARGET <flags>
   
   DESCRIPTION
       Version: 0.0.6
       Project: https://git.io/fjHT1
   
       Example:
           python3 oneforall.py --target example.com run
           python3 oneforall.py --target ./domains.txt run
           python3 oneforall.py --target example.com --brute True run
           python3 oneforall.py --target example.com --dns False run
           python3 oneforall.py --target example.com --req False run
           python3 oneforall.py --target example.com --valid None run
           python3 oneforall.py --target example.com --port medium run
           python3 oneforall.py --target example.com --format csv run
           python3 oneforall.py --target example.com --show True run
   
       Note:
           Parameter valid optional value 1, 0, none indicates that the export is 
           valid, invalid, and all subdomains, respectively.
           Parameter port have optional values 'default' 'small', 'medium', 'large',
           See config.py configuration for details.
           Parameter format have optional values 'txt', 'rst', 'csv', 'tsv', 'json', 
           'yaml', 'html', 'jira', 'xls', 'xlsx', 'dbf', 'latex', 'ods'.
           If the parameter path is None, the appropriate file is generated in the 
           project result directory based on the format parameter and the domain 
           name.
   
   ARGUMENTS
       TARGET
           Single domain name or file path for one domain name per line (required)
   
   FLAGS
       --brute=BRUTE
           Use blasting module (default False)
       --dns=DNS
           DNS resolve subdomain (default True)
       --req=REQ
           HTTP request subdomain (default True)
       --port=PORT
           Port range for request authentication (default 80 port)
       --valid=VALID
           Export validity of subdomains (default 1)
       --path=PATH
           Export path (default None)
       --format=FORMAT
           Export format (default xls)
       --takeover=TAKEOVER
           Check subdomain takeover (default False)
       --show=SHOW
           Terminal display exported data (default False)
   ```
   
2. **aiobrute.py help**

   With regard to the handling of the universal parsing problem, first of all, OneForAll accesses a random subdomain to determine whether universal parsing is used, and if universal parsing is used, it is handled by the following judgment: 
   - First, it is mainly compared with the pan-parsed IP set and TTL values, see [this article](http://sh3ll.me/archives/201704041222.txt).

   - Second, the number of times to resolve to the same IP collection multiple times (the default is 10, which can be set to size in config.py).

   - Third, considering the blasting efficiency, there is no HTTP response volume similarity comparison and response volume content judgment,  this function has not been implemented yet, and will be implemented if necessary.

   After not rigorous testing, in the 16-core CPU, using 16 processes 64 coroutines, 100M network bandwidth environment, set the task to be divided into 50000, run two million dictionaries about 10 minutes to run, about 3333 subdomains per second.

   ```bash
   python aiobrute.py --help
   ```

   ```bash
   NAME
       aiobrute.py - OneForAll multi-process multi-correlation asynchronous subdomain blasting module
   
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
           The setting of the parameter segment is affected by CPU performance, 
           network bandwidth, and operator restrictions. By default, 500 subdomains 
           are set as task groups. When you feel that your environment is not 
           affected by the above factors, the current blasting speed is slow, so it 
           is strongly recommended to use the dictionary. Size resizing: 100,000 
           dictionary suggestions set to 5000, million dictionary set to 50000.
           
           Parameter valid optional value 1, 0, none indicates that the export is 
           valid, invalid, and all subdomains, respectively.
           
           Parameter format have optional values 'txt', 'rst', 'csv', 'tsv', 'json', 
           'yaml', 'html', 'jira', 'xls', 'xlsx', 'dbf', 'latex', 'ods'.
           If the parameter path is None, the appropriate file is generated in the 
           project result directory based on the format parameter and the domain 
           name.
   
   ARGUMENTS
       TARGET
           Single domain name or file path for one domain name per line (required)
   
   FLAGS
       --process=PROCESS
           Number of processes blasted (default CPU core count)
       --coroutine=COROUTINE
           Number of coroutines per blasting process (default 64)
       --wordlist=WORDLIST
           Specify the dictionary path used for blasting (config.py is used by default)
       --segment=SEGMENT
           Blasting task segmentation (default 500)
       --recursive=RECURSIVE
           Whether to use recursive blasting (default False)
       --depth=DEPTH
           Depth of recursive blasting (default 2)
       --namelist=NAMELIST
           Specifies the dictionary path used by recursive blasting (configured by default using config.py)
       --fuzz=FUZZ
           Whether to use the fuzz mode for blasting (default False, you must specify the fuzz regular rule)
       --rule=RULE
           Regular rules used by fuzz mode (configured by default using config.py)
       --export=EXPORT
           Whether to export the blast result (default True)
       --valid=VALID
           Export validity of subdomains (default None)
       --format=FORMAT
           Export format (default xls)
       --path=PATH
           Export path (default None)
       --show=SHOW
           Terminal display exported data (default False)
   ```

3. For other module usage, please refer to [usage help](https://github.com/shmilylty/OneForAll/tree/master/docs/using_help.md).

## 👏Framework used

* [aiodns](https://github.com/saghul/aiodns) - aiodns provides a simple way for doing asynchronous DNS resolutions using [pycares](https://github.com/saghul/pycares). 
* [aiohttp](https://github.com/aio-libs/aiohttp) -  Asynchronous HTTP client/server framework for asyncio and Python 
* [aiomultiprocess](https://github.com/jreese/aiomultiprocess) -  Take a modern Python codebase to the next level of performance. (Multiprocessing and asyncio combine to implement asynchronous multi-process multi-coroutine)
* [beautifulsoup4](https://pypi.org/project/beautifulsoup4/) -  Beautiful Soup is a library that makes it easy to scrape information from web pages. 
* [fire](https://github.com/google/python-fire) -  Python Fire is a library for automatically generating command line interfaces (CLIs) from absolutely any Python object. 
* [loguru](https://github.com/Delgan/loguru) -  Loguru is a library which aims to bring enjoyable logging in Python. 
* [records](https://github.com/kennethreitz/records) -  Records is a very simple, but powerful, library for making raw SQL queries to most relational databases.
* [requests](https://github.com/psf/requests) -  A simple, yet elegant HTTP library. 
* [tqdm](https://github.com/tqdm/tqdm) -  A Fast, Extensible Progress Bar for Python and CLI 

Thanks to these great excellent Python libraries!

## 🌲Directory structure

```bash
D:.
|
+---.github
+---docs
|       collection_modules.md collection module description
+---images
\---oneforall
    |   aiobrute.py   Asynchronous multi-process multi-correlation subdomain blasting module, can be run separately
    |   collect.py    Upper layer call of each collection module
    |   config.py     Configuration file
    |   dbexport.py   Database export module, can be run separately
    |   domains.txt   List of domain names to be blasted
    |   oneforall.py  OneForAll main entrance, can be run separately
    |   __init__.py
    |
    +---common Common call module
    +---data   Store some of the required data
    |       next_subdomains.txt     Next level subdomain dictionary
    |       public_suffix_list.dat  Top-level domain name suffix
    |       srv_names.json          Common SRV record prefix name
    |       subdomains.txt          Common Dictionary of subdomain blasting
    |
    \---modules 
        +---certificates     Using certificate transparency to collect subdomain
        +---check            Using conventional methods to collect subdomain
        +---crawl            Using web crawler files to collect subdomain
        +---datasets         Using DNS datasets to collect subdomain
        +---dnsquery         Using DNS query to collect subdomain
        +---intelligence     Using threat intelligence platform to collect subdomain
        \---search           Using search engine to collect subdomain

```

## 🙏Contribution

Very warmly welcome all ace to improve the project together!

## ⌛Follow-up plan

- [ ] Continuous optimization and improvement of each module
- [x] Subdomain monitoring (marking each newly discovered subdomain)
- [ ] Subdomain collection crawler implementation (including collection of subdomains from static resource files such as JS)
- [ ] Implementation of front-end interface for powerful interaction (tentative: front-end: Element + back-end: Flask)

For more details, see [TODO.md](https://github.com/shmilylty/OneForAll/tree/master/TODO.md).

## 🔖Version control

The project uses [SemVer](https://semver.org/) language version format for version management), and you can view the available version in [Releases](https://github.com/shmilylty/OneForAll/releases).

## 👨‍💻Contributors

* **[Jing Ling](https://github.com/shmilylty)**
  * Core development

* **[Black Star](https://github.com/blackstar24)**，**[Echocipher](https://github.com/Echocipher)**
  * Module contribution

* **[iceMatcha](https://github.com/iceMatcha)**，**[mikuKeeper](https://github.com/mikuKeeper)**
  * Tool test

* **Anyone**
  * Tool feedback

You can see all the developers involved in the project in [CONTRIBUTORS.md](https://github.com/shmilylty/OneForAll/tree/master/CONTRIBUTORS.md).

## 📄License

The project has signed a GPL-3.0 license, for more information, please see [LICENSE](https://github.com/shmilylty/OneForAll/LICENSE).

## 😘Acknowledgement

Thanks to the various subdomain collection projects of online open source!

Thanks ace of [A-Team](https://github.com/QAX-A-Team) for their enthusiastic and unselfish answers!

## 📜Disclaimer ##

This tool is limited to legally authorized enterprise security construction. In the process of using this tool, you should ensure that all your actions comply with local laws and regulations and have obtained sufficient authorization.
If you have any illegal behavior in the process of using this tool, you are responsible for all consequences, and all authors and all contributors of this tool do not assume any legal and joint responsibility.
Unless you have fully read, fully understood and accepted all the terms of this Agreement, please do not install and use this tool.
Your use or any other express or implied representation of you to this Agreement is deemed to have been read and agreed to be bound by this Agreement.
