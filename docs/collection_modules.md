#  收集模块说明 #

 1. 利用证书透明度收集子域（目前有6个模块：`censys_api`，`certdb_api`，`certspotter`，`crtsh`，`entrust`，`google`）
    
      | 模块        | 是否需要代理 | 是否需要API | 其他说明 |
      | ----------- | ------------ | ----------- | -------- |
      | censys_api  | 否           | 是          |          |
      | certdb_api  | 否           | 是          |          |
      | certspotter | 否           | 否          |          |
      | crtsh       | 否           | 否          |          |
      | entrust     | 否           | 否          |          |
      | google      | 是           | 否          |          |


  2. 常规检查收集子域（目前有4个模块：域传送漏洞利用`axfr`，检查跨域策略文件`cdx`，检查HTTPS证书`cert`，检查内容安全策略`csp`，后续会添加检查NSEC记录，NSEC记录等模块）
  
      |      |      |      |      |
      | ---- | ---- | ---- | ---- |
      |      |      |      |      |
      |      |      |      |      |
      |      |      |      |      |
      |      |      |      |      |
      |      |      |      |      |
      |      |      |      |      |
  3. 利用网上爬虫档案收集子域（目前有2个模块：`archivecrawl`，`commoncrawl`，此模块还在调试，该模块还有待添加和完善）
  
      |      |      |      |      |
      | ---- | ---- | ---- | ---- |
      |      |      |      |      |
      |      |      |      |      |
      |      |      |      |      |
      |      |      |      |      |
      |      |      |      |      |
      |      |      |      |      |
  4. 利用DNS数据集收集子域（目前有16个模块：`binaryedge_api`, `circl_api`, `hackertarget`, `riddler`, `bufferover`, `dnsdb`, `ipv4info`, `robtex`, `chinaz`, `dnsdb_api`, `netcraft`, `securitytrails_api`, `chinaz_api`, `dnsdumpster`, `ptrarchive`, `sitedossier`）
  
      |      |      |      |      |
      | ---- | ---- | ---- | ---- |
      |      |      |      |      |
      |      |      |      |      |
      |      |      |      |      |
      |      |      |      |      |
      |      |      |      |      |
      |      |      |      |      |
  5. 利用DNS查询收集子域（目前有1个模块：通过枚举常见的SRV记录并做查询来收集子域`srv`，该模块还有待添加和完善）
  
      |      |      |      |      |
      | ---- | ---- | ---- | ---- |
      |      |      |      |      |
      |      |      |      |      |
      |      |      |      |      |
      |      |      |      |      |
      |      |      |      |      |
      |      |      |      |      |
  6. 利用威胁平台数据收集子域（目前有5个模块：`riskiq`，`threatbook`，`threatminer`，`virustotal`，`virustotal_api`该模块还有待添加和完善）
  
      |      |      |      |      |
      | ---- | ---- | ---- | ---- |
      |      |      |      |      |
      |      |      |      |      |
      |      |      |      |      |
      |      |      |      |      |
      |      |      |      |      |
      |      |      |      |      |
  8. [搜索引擎](./oneforall/modules/search)发现子域（目前有15个模块：`ask`, `bing_api`, `fofa`, `shodan_api`, `yahoo`, `baidu`, `duckduckgo`, `google`, `so`, `yandex`, `bing`, `exalead`, `google_api`, `sogou`, `zoomeye_api`）
  
     除特殊搜索引擎，通用的搜索引擎都支持自动排除搜索，全量搜索，递归搜索。
  
     | 模块        | 是否需要代理           | 是否需要API | 其他说明                                            |
     | ----------- | ---------------------- | ----------- | --------------------------------------------------- |
     | ask         | 是                     | 否          |                                                     |
     | baidu       | 否                     | 否          |                                                     |
     | bing        | 否                     | 否          |                                                     |
     | bing_api    | 否                     | 是          | API使用和申请见[config.py](./oneforall/config.py)。 |
     | duckduckgo  | 是                     | 否          |                                                     |
     | exalead     | 否，最好使用国外代理。 | 否          |                                                     |
     | fofa        | 否                     | 否          |                                                     |
     | google      | 是                     | 否          |                                                     |
     | google_api  | 是                     | 是          | API使用和申请见[config.py](./oneforall/config.py)。 |
     | shodan_api  | 否，最好使用国外代理。 | 是          | API使用和申请见[config.py](./oneforall/config.py)。 |
     | so          | 否                     | 否          |                                                     |
     | sogou       | 否                     | 否          |                                                     |
     | yahoo       | 是                     | 否          |                                                     |
     | yandex      | 是                     | 否          |                                                     |
     | zoomeye_api | 否                     | 是          | API使用和申请见[config.py](./oneforall/config.py)。 |