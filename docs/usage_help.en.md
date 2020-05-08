**🤔Help**

The command line parameters only provide some common parameters. For more detailed parameter configuration, please see [config.py](https://github.com/shmilylty/OneForAll/tree/master/oneforall/config.py) if you think Some parameters are frequently used in the command interface or missing parameters. Feedback is welcome. For well-known reasons, if you want to use some of the wall's collection interface, please go to [config.py](https://github.com/shmilylty/OneForAll/tree/master/oneforall/config.py) to configure the proxy, some collection Modules need to provide APIs (most of which are freely available for registered accounts). If you need to use them, please go to [api.py](https://github.com/shmilylty/OneForAll/tree/master/oneforall/api.py) to configure the API. Information, if not used, please ignore the error message. (For detailed modules, please read [collection module description](https://github.com/shmilylty/OneForAll/tree/master/docs/collection_modules.md))

The OneForAll command line interface is based on [Fire](https://github.com/google/python-fire/). For more advanced usage of Fire, please refer to [using the Fire CLI](https://github.com/google/Python-fire/blob/master/docs/using-cli.md), if you have any doubts during the use, please feel free to give me feedback.

[oneforall.py](https://github.com/shmilylty/OneForAll/tree/master/oneforall/oneforall.py) is the main program entry, and oneforall.py can call [aiobrute.py](https://github.com/shmilylty/OneForAll/tree/master/oneforall/aiobrute.py), [takerover.py](https://github.com/shmilylty/OneForAll/tree/master/oneforall/takerover.py) and [dbexport.py ](https://github.com/shmilylty/OneForAll/tree/master/oneforall/dbexport.py) and other modules, in order to facilitate the sub-field blasting, aiobrute.py is isolated independently, in order to facilitate the subdomain takeover risk check independently takeover.py, in order to facilitate the database export independently dbexport.py, these modules can be run separately, and the parameters accepted are more abundant.

❗ Note: When you encounter some problems or doubts during use, please use [Issues](https://github.com/shmilylty/OneForAll/issues) to search for answers. Also see [Q&A](https://github.com/shmilylty/OneForAll/tree/master/docs/Q&A.md).

1. **oneforall.py help**

   ```bash
   python oneforall.py --help
   ```
   ```bash
   NAME
       oneforall.py - OneForAll help Information
   
   SYNOPSIS
       oneforall.py --target=TARGET <flags>
   
   DESCRIPTION
       OneForAll is a powerful subdomain collection tool
   
       Example:
           python3 oneforall.py version
           python3 oneforall.py --target example.com run
           python3 oneforall.py --target ./domains.txt run
           python3 oneforall.py --target example.com --valid None run
           python3 oneforall.py --target example.com --brute True run
           python3 oneforall.py --target example.com --port small run
           python3 oneforall.py --target example.com --format csv run
           python3 oneforall.py --target example.com --dns False run
           python3 oneforall.py --target example.com --req False run
           python3 oneforall.py --target example.com --takeover False run
           python3 oneforall.py --target example.com --show True run
   
       Note:
           Parameter valid optional value 1, 0, none indicates that the export is 
           valid, invalid, and all subdomains, respectively.
           Parameter port have optional values 'default' 'small', 'large',
           See config.py configuration for details.
           Parameter format have optional values 'txt', 'rst', 'csv', 'tsv', 'json', 
           'yaml', 'html', 'jira', 'xls', 'xlsx', 'dbf', 'latex', 'ods'.
           If the parameter path is None, the appropriate file is generated in the 
           project result directory based on the format parameter and the domain 
           name.
           Parameter path default None uses the OneForAll result directory generation path
   
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
           Export validity of subdomains (default None)
       --format=FORMAT
           Export format (default xls)
       --path=PATH
           Export path (default None)
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
           Number of coroutines per blasting process (default 1024)
       --wordlist=WORDLIST
           Specify the dictionary path used for blasting (config.py is used by default)
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