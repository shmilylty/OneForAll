**🤔Help**

The command line parameters only provide some common parameters. For more detailed parameter configuration, please see [config.py](https://github.com/shmilylty/OneForAll/tree/master/oneforall/config/setting.py) if you think Some parameters are frequently used in the command interface or missing parameters. Feedback is welcome. For well-known reasons, if you want to use some of the wall's collection interface, please go to [config.py](https://github.com/shmilylty/OneForAll/tree/master/oneforall/config/setting.py) to configure the proxy, some collection Modules need to provide APIs (most of which are freely available for registered accounts). If you need to use them, please go to [api.py](https://github.com/shmilylty/OneForAll/tree/master/oneforall/config/api.py) to configure the API. Information, if not used, please ignore the error message. (For detailed modules, please read [collection module description](https://github.com/shmilylty/OneForAll/tree/master/docs/collection_modules.md))

The OneForAll command line interface is based on [Fire](https://github.com/google/python-fire/). For more advanced usage of Fire, please refer to [using the Fire CLI](https://github.com/google/Python-fire/blob/master/docs/using-cli.md), if you have any doubts during the use, please feel free to give me feedback.

[oneforall.py](https://github.com/shmilylty/OneForAll/tree/master/oneforall/oneforall.py) is the main program entry, and oneforall.py can call [aiobrute.py](https://github.com/shmilylty/OneForAll/tree/master/oneforall/aiobrute.py), [takerover.py](https://github.com/shmilylty/OneForAll/tree/master/oneforall/takerover.py) and [dbexport.py ](https://github.com/shmilylty/OneForAll/tree/master/oneforall/dbexport.py) and other modules, in order to facilitate the sub-field blasting, aiobrute.py is isolated independently, in order to facilitate the subdomain takeover risk check independently takeover.py, in order to facilitate the database export independently dbexport.py, these modules can be run separately, and the parameters accepted are more abundant.

❗ Note: When you encounter some problems or doubts during use, please use [Issues](https://github.com/shmilylty/OneForAll/issues) to search for answers. Also see [Q&A](https://github.com/shmilylty/OneForAll/tree/master/docs/Q&A.md).

1. **oneforall.py help**

```bash
python oneforall.py --help
```
```bash
NAME
   oneforall.py - OneForAll help summary page

SYNOPSIS
   oneforall.py COMMAND | <flags>

DESCRIPTION
   OneForAll is a powerful subdomain integration tool

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
       --port   small/medium/large  See details in ./config/setting.py(default small)
       --format csv/json (result format)
       --path   Result path (default None, automatically generated)

FLAGS
   --target=TARGET
    One domain (target or targets parameters must be provided)
   --targets=TARGETS
       File path of one domain per line
   --brute=BRUTE
       Use brute module (default False)
   --dns=DNS
       Use DNS resolution (default True)
   --req=REQ
       HTTP request subdomains (default True)
   --port=PORT
       The port range to request (default small port is 80,443)
   --alive=ALIVE
       Only export alive subdomains (default False)
   --format=FORMAT
       Result format (default csv)
   --path=PATH
       Result path (default None, automatically generated)
   --takeover=TAKEOVER
       Scan subdomain takeover (default False)

COMMANDS
   COMMAND is one of the following:

   check
     Check if there is a new version and exit

   version
     Print version information and exit
```
   
2. **aiobrute.py help**

With regard to the handling of the universal parsing problem, first of all, OneForAll accesses a random subdomain to determine whether universal parsing is used, and if universal parsing is used, it is handled by the following judgment: 
- First, it is mainly compared with the pan-parsed IP set and TTL values, see [this article](http://sh3ll.me/archives/201704041222.txt).

- Second, the number of times to resolve to the same IP collection multiple times (the default is 10, which can be set to size in config.py).

- Third, considering the blasting efficiency, there is no HTTP response volume similarity comparison and response volume content judgment,  this function has not been implemented yet, and will be implemented if necessary.


```bash
python brute.py --help
```

```bash
NAME
brute.py - OneForAll subdomain brute module

SYNOPSIS
    brute.py <flags>

DESCRIPTION
    Example：
        brute.py --target domain.com --word True run
        brute.py --targets ./domains.txt --word True run
        brute.py --target domain.com --word True --concurrent 2000 run
        brute.py --target domain.com --word True --wordlist subnames.txt run
        brute.py --target domain.com --word True --recursive True --depth 2 run
        brute.py --target d.com --fuzz True --place m.*.d.com --rule '[a-z]' run
        brute.py --target d.com --fuzz True --place m.*.d.com --fuzzlist subnames.txt run

    Note:
        --format rst/csv/tsv/json/yaml/html/jira/xls/xlsx/dbf/latex/ods (result format)
        --path   Result path (default None, automatically generated)

    FLAGS
        --target=TARGET
            One domain (target or targets must be provided)
        --targets=TARGETS
            File path of one domain per line
        --process=PROCESS
            Number of processes (default 1)
        --concurrent=CONCURRENT
            Number of concurrent (default 2000)
        --word=WORD
            Use word mode generate dictionary (default False)
        --wordlist=WORDLIST
            Dictionary path used in word mode (default use ./config/default.py)
        --recursive=RECURSIVE
            Use recursion (default False)
        --depth=DEPTH
            Recursive depth (default 2)
        --nextlist=NEXTLIST
            Dictionary file path used by recursive (default use ./config/default.py)
        --fuzz=FUZZ
            Use fuzz mode generate dictionary (default False)
        --place=PLACE
            Designated fuzz position (required if use fuzz mode)
        --rule=RULE
            Specify the regexp rules used in fuzz mode (required if use fuzz mode)
        --fuzzlist=FUZZLIST
            Dictionary path used in fuzz mode (default use ./config/default.py)
        --export=EXPORT
            Export the results (default True)
        --alive=ALIVE
            Only export alive subdomains (default False)
        --format=FORMAT
            Result format (default csv)
        --path=PATH
            Result directory (default None)
```

3. **takeover.py help**

```bash
python takeover.py --help
```

```bash
NAME
takeover.py - OneForAll subdomain takeover module                                                                                                                                 SYNOPSIS                                                                                       takeover.py <flags>                                                                                                                                                               DESCRIPTION

Example:
    python3 takeover.py --target www.example.com  --format csv run
    python3 takeover.py --targets ./subdomains.txt --thread 10 run

Note:
    --format rst/csv/tsv/json/yaml/html/jira/xls/xlsx/dbf/latex/ods (result format)
    --path   Result directory (default directory is ./results)

FLAGS
    --target=TARGET
        One domain (target or targets must be provided)
    --targets=TARGETS
        File path of one domain per line
    --thread=THREAD
        threads number (default 20)
    --path=PATH
        Result directory (default None)
    --format=FORMAT
        Result format (default csv)
```

4. **dbexport.py help**

```bash
python dbexport.py --help
```

```bash
NAME
    dbexport.py - OneForAll export from database module

SYNOPSIS
    dbexport.py TARGET <flags>

DESCRIPTION
    Example:
        python3 dbexport.py --target name --format csv --dir= ./result.csv
        python3 dbexport.py --db result.db --target name --show False
        python3 dbexport.py --target table_name --tb True --show False

    Note:
        --format rst/csv/tsv/json/yaml/html/jira/xls/xlsx/dbf/latex/ods (result format)
        --path   Result directory (default directory is ./results)

POSITIONAL ARGUMENTS
    TARGET
        Table to be exported

FLAGS
    --type=TYPE
        Type of target
    --db=DB
        Database path to be exported (default ./results/result.sqlite3)
    --alive=ALIVE
        Only export the results of alive subdomains (default False)
    --limit=LIMIT
        Export limit (default None)
    --path=PATH
        Result directory (default None)
    --format=FORMAT
        Result format (default csv)
    --show=SHOW
        Displays the exported data in terminal (default False)
```
