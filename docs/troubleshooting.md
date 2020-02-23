# 常见问题与回答

## 依赖问题

**Q: 在安装依赖过程遇到编译某个依赖库失败，怎么解决？**

A: 可以尝试以下方法:

1. 到提供编译好的whl文件的第三方平台，找到对应库手动下载安装。第三方平台平台有： 
 * [https://www.lfd.uci.edu/~gohlke/pythonlibs](https://www.lfd.uci.edu/~gohlke/pythonlibs)
 * [https://pythonwheels.com/](https://pythonwheels.com/)

选择好对应版本执行以下命令手动安装。举个例子，当编译 brotlipy 时失败时，找到[https://www.lfd.uci.edu/~gohlke/pythonlibs/#brotlipy](https://www.lfd.uci.edu/~gohlke/pythonlibs/#brotlipy)，由于我的系统是Windows 10 64位，使用的Python 3.8便下载`brotlipy‑0.7.0‑cp38‑cp38‑win_amd64.whl`（一般来说下载最新版本的），然后手动安装：

```bash
pip3 install brotlipy‑0.7.0‑cp38‑cp38‑win_amd64.whl
```

2. 到库的项目地址issues和wiki等找找有没有解决方法，如果没有就给他们提issues发邮件😜。

## 使用问题

**Q: 为什么运行OneForAll之后最终结果为空？**

*A: 有几种可能性：第一可能目标域名没有子域。第二由于OneForAll默认会自动验证子域，在导出是只会有效子域，所以存在导出时没有有效子域的情况，你可以在运行OneForAll使用--valid=None指定导出所有发现的子域，你也可以使用--verify=False指定不验证子域的有效性。*

**Q: 安装依赖时出现以下类似报错，怎么解决？**
   Cannot uninstall 'PyYAML'. It is a distutils installed project and thus we cannot accurately determine which files belong to it which would lead to only a partial uninstall.

*A: 安装依赖时尝试加上--ignore-installed参数*

**Q:使用Excel打开结果的csv中有中文乱码，怎么解决？**

*A:由于Excel打开文件需要带BOM头识别编码，而默认生成的结果csv文件是UTF-8编码不是UTF-8-BOM，所以会使用Excel打开会出现中文乱码*，有以下解决办法：

1.在一开始运行OneForAll，设置format参数为xls或者xlsx格式。

2.使用NotePad++类似工具转化编码格式为UTF-8-BOM。

3.使用Excel软件导入结果csv文件中的数据。