import time
import threading
import importlib

import dbexport
from config.log import logger
from config import setting


class Collect(object):
    """
    收集子域名类
    """
    def __init__(self, domain, export=True):
        self.domain = domain
        self.elapse = 0.0
        self.modules = []
        self.collect_funcs = []
        self.path = None
        self.export = export
        self.format = 'csv'

    def get_mod(self):
        """
        获取要运行的模块
        """
        if setting.enable_all_module:
            # modules = ['brute', 'certificates', 'crawl',
            # 'datasets', 'intelligence', 'search']
            # crawl模块还有点问题
            modules = ['certificates', 'check', 'datasets',
                       'dnsquery', 'intelligence', 'search']
            # modules = ['intelligence']  # crawl模块还有点问题
            for module in modules:
                module_path = setting.module_dir.joinpath(module)
                for path in module_path.rglob('*.py'):
                    # 需要导入的类
                    import_module = ('modules.' + module, path.stem)
                    self.modules.append(import_module)
        else:
            self.modules = setting.enable_partial_module

    def import_func(self):
        """
        导入脚本的do函数
        """
        for package, name in self.modules:
            import_object = importlib.import_module('.' + name, package)
            func = getattr(import_object, 'do')
            self.collect_funcs.append([func, name])

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
        for collect_func in self.collect_funcs:
            func_obj, func_name = collect_func
            thread = threading.Thread(target=func_obj,
                                      name=func_name,
                                      args=(self.domain,),
                                      daemon=True)
            threads.append(thread)
        # 启动所有线程
        for thread in threads:
            thread.start()
        # 等待所有线程完成
        for thread in threads:
            # 挨个线程判断超时 最坏情况主线程阻塞时间=线程数*module_thread_timeout
            # 超时线程将脱离主线程 由于创建线程时已添加守护属于 所有超时线程会随着主线程结束
            thread.join(setting.module_thread_timeout)

        for thread in threads:
            if thread.is_alive():
                logger.log('ALERT', f'{thread.name}模块线程发生超时')

        # 数据库导出
        if self.export:
            if not self.path:
                name = f'{self.domain}.{self.format}'
                self.path = setting.result_save_dir.joinpath(name)
            dbexport.export(self.domain, path=self.path, format=self.format)
        end = time.time()
        self.elapse = round(end - start, 1)


if __name__ == '__main__':
    collect = Collect('example.com')
    collect.run()
