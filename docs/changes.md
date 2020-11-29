# 更新日志
OneForAll的所有值得注意的更改都将记录在此文件中。

OneForAll的更新日志格式基于[Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)。

OneForAll遵守[语义化版本格式](https://semver.org/)。

# Unreleased

# Released
## [0.4.3](https://github.com/shmilylty/oneforall/releases/tag/v0.4.3) - 2020-11-29
- 修复了已知问题
- 更新了文档

## [0.4.2](https://github.com/shmilylty/oneforall/releases/tag/v0.4.2) - 2020-11-23
- 添加了数据表初始化处理流程，修复了#163中出现的问题。

## [0.4.1](https://github.com/shmilylty/oneforall/releases/tag/v0.4.1) - 2020-11-18
- 修复了数字开头主域（如58.com）出现数据库报错的问题

## [0.4.0](https://github.com/shmilylty/oneforall/releases/tag/v0.4.0) - 2020-11-18
- 重构了子域请求模块，解决了内存占用过大问题
- 新增了子域置换模块，能从现有的子域发现更多新子域
- 新增了数据富化模块，富化出更多有用的信息
- 新增了finder模块，能从响应体和JS及跳转历史收集子域
- 重构了泛解析探测，泛解析探测更加准确
- 实现了配置插拔式设计
- 实现了版本更新检查、运行环境检查、网络环境检查
- 优化了子域爆破模块
- 优化了泛解析处理
- 优化了子域字典
- 删除和优化了部分收集模块
- 修复了一些反馈的bug
- 更新了文档

## [0.3.0](https://github.com/shmilylty/oneforall/releases/tag/v0.3.0) - 2020-05-13
- 重构了项目目录结构
- 修改了输出显示为英文
- 优化了泛解析处理
- 优化了部分收集模块
- 新增了静默级别的日志输出
- 新增了超大爆破压缩包字典
- 新增了利用NSEC记录遍历DNS域模块
- 新增了sublist3r接口查询模块
- 现在`docker pull shmilylty/oneforall`是自动构建的
- 修复了一些反馈的bug
- 更新了文档

## [0.2.0](https://github.com/shmilylty/oneforall/releases/tag/v0.2.0) - 2020-04-27
- 重构子域爆破和解析模块 改用massdns 一般情况下可以达到10000pps 速度非常快
- 优化泛解析处理
- 优化部分子域收集模块
- 新增了爆破字典
- 新增了github_api和rapiddns收集模块
- 修复了一些bug
- 更新了文档

## [0.1.0](https://github.com/shmilylty/oneforall/releases/tag/v0.1.0) - 2020-03-02
- 重构OneForAll入口
- 添加1个新的子域收集模块
- 添加了查询类型type和子域层数level两个结果字段
- 调整项目结构
- 优化个别收集模块
- 优化子域爆破字典
- 优化响应体解码处理
- 更新说明文档
- 修复已知bug

## [0.0.9](https://github.com/shmilylty/oneforall/releases/tag/v0.0.9) - 2020-02-20
- 重构子域解析模块
- 添加4个新的子域收集模块
- 添加了Docker部署
- 优化配置参数和收集模块
- 优化子域爆破字典和默认参数
- 优化响应体解码处理
- 更新说明文档
- 修复已知bug

## [0.0.8](https://github.com/shmilylty/oneforall/releases/tag/v0.0.8) - 2019-10-30
- 添加新子域监控功能
- 优化子域爆破字典和默认参数
- 修复端口重复问题
- 移除aiodns依赖

## [0.0.7](https://github.com/shmilylty/oneforall/releases/tag/v0.0.7) - 2019-10-18
- 修复一些已知问题
- 添加百度云观测接口
- 添加添加英文Readme文档
- 更新有关文档
- 优化标题获取
- 更新依赖

## [0.0.6](https://github.com/shmilylty/oneforall/releases/tag/v0.0.6) - 2019-08-27
- 修复一些已知问题
- 添加PassiveDNS查询和Github子域搜索模块
- 优化FoFa和BufferOver收集模块
- 更新有关文档
- 更新依赖

## [0.0.5](https://github.com/shmilylty/oneforall/releases/tag/v0.0.5) - 2019-08-19
- 修复一些已知Bugs
- 优化各子域收集接口并添加新的子域收集接口
- 添加子域DNS解析和子域HTTP探测进度条
- 添加子域接管风险检查模块及其使用说明
- 更新OneForAll依赖

## [0.0.4](https://github.com/shmilylty/oneforall/releases/tag/v0.0.4) - 2019-08-11
### 修复
- 修复一些已知Bugs

## [0.0.3](https://github.com/shmilylty/oneforall/releases/tag/v0.0.3) - 2019-08-08
### 修改
- 代码PEP8格式化
### 修改
- 修改一些已知Bugs

## [0.0.2](https://github.com/shmilylty/oneforall/releases/tag/v0.0.2) - 2019-08-04
### 新增
- 新增有关文档
### 修改
- 修改有关日志输出格式和信息
### 修复
- 升级fire库版本解决运行报错问题
### 移除
- 移除brotlipy依赖


## [0.0.1](https://github.com/shmilylty/oneforall/releases/tag/v0.0.1) - 2019-08-02
### 新增
- 新增检查crossdomain.xml收集子域功能
- 新增检查域名证书收集子域功能
- 新增检查内容安全策略头收集子域功能
- 新增域传送利用功能
- 新增子域收集功能（搜索引擎，DNS数据集，证书透明度，网上爬虫档案）
- 新增子域爆破功能
- 新增数据库导出功能
