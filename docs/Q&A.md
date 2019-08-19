# 常见问题与回答

## 使用问题

1. 为什么运行OneForAll之后最终结果为空？

   有几种可能性：第一可能目标域名没有子域。第二由于OneForAll默认会自动验证子域，在导出是只会有效子域，所以存在导出时没有有效子域的情况，你可以在运行OneForAll使用--valid=None指定导出所有发现的子域，你也可以使用--verify=False指定不验证子域的有效性。

2. 安装依赖时出现以下类似报错
   Cannot uninstall 'PyYAML'. It is a distutils installed project and thus we cannot accurately determine which files belong to it which would lead to only a partial uninstall.
   
   安装依赖时尝试加上--ignore-installed参数