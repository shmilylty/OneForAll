注意：以下部分字段只存于结果数据库中

### id

标识作用无意义

### new

标记是否是新发现的子域名

### alive

是否存活，不存活的判定情况包含：无法解析IP、网络不可达、400、5XX等

### request

记录HTTP请求是否成功字段，为空是无法解析IP，为0是网络不可达，为1是成功请求

### resolve

记录DNS解析是否成功

### url

请求的url链接

### subdomain

子域名

### level

是几级子域名

### cname

cname记录

### ip

解析到的IP

### public

是否是公网IP

### cdn

解析的IP是否CDN

### port

请求的网络端口

### status

HTTP响应的状态码

### reason

网络连接情况及详情

###title

网站标题

### banner

网站指纹信息

### history
请求时URL跳转历史

### response
响应体文本内容

### times

在爆破中ip重复出现的次数

### ttl

DNS解析返回的TTL值

### cidr

ip2location库查询出的CIDR

### asn

ip2location库查询出的ASN

### addr

ip2region库查询出的物理地址

### isp

ip2region库查询出的网络服务提供商

### resolver

所使用的DNS解析服务器

### module

发现本子域名所使用的模块

### source

发现本子域名的具体来源

### elapse

当前模块发现用时

### find

当前模块发现的子域个数