import time
import threading
import importlib
import config
import dbexport
from config import logger


class Collect(object):
    """
    收集子域名类
    """
    def __init__(self, domain, export=True):
        self.domain = domain
        self.elapsed = 0.0
        self.modules = []
        self.collect_func = []
        self.path = None
        self.export = export
        self.format = 'csv'

    def get_mod(self):
        """
        获取要运行的模块
        """
        if config.enable_all_module:
            # modules = ['brute', 'certificates', 'crawl',
            # 'datasets', 'intelligence', 'search']
            # crawl模块还有点问题
            modules = ['certificates', 'check', 'datasets',
                       'dnsquery', 'intelligence', 'search']
            # modules = ['intelligence']  # crawl模块还有点问题
            for module in modules:
                module_path = config.oneforall_module_path.joinpath(module)
                for path in module_path.rglob('*.py'):
                    # 需要导入的类
                    import_module = ('modules.' + module, path.stem)
                    self.modules.append(import_module)
        else:
            self.modules = config.enable_partial_module

    def import_func(self):
        """
        导入脚本的do函数
        """
        for package, name in self.modules:
            import_object = importlib.import_module('.'+name, package)
            self.collect_func.append(getattr(import_object, 'do'))

    def run(self):
        """
        类运行入口
        """
        start = time.time()
        logger.log('INFOR', f'开始收集{self.domain}的子域')
        self.get_mod()
        self.import_func()

        threads = []
        # 创建多个子域收集线程
        for collect_func in self.collect_func:
            thread = threading.Thread(target=collect_func,
                                      args=(self.domain,),
                                      daemon=True)
            threads.append(thread)
        # 启动所有线程
        for thread in threads:
            thread.start()
        # 等待所有线程完成
        for thread in threads:
            thread.join()

        # 数据库导出
        if self.export:
            if not self.path:
                name = f'{self.domain}.{self.format}'
                self.path = config.result_save_path.joinpath(name)
            dbexport.export(self.domain, dpath=self.path, format=self.format)
        end = time.time()
        self.elapsed = round(end - start, 1)


if __name__ == '__main__':
    a = Collect('example.com')
    a.run()
