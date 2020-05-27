import time
import threading
import importlib

import dbexport
from config.log import logger
from config import setting


class Collect(object):
    """
    Collect subdomains
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
        Get modules
        """
        if setting.enable_all_module:
            # modules = ['brute', 'certificates', 'crawl',
            # 'datasets', 'intelligence', 'search']
            # The crawl module has some problems
            modules = ['certificates', 'check', 'datasets',
                       'dnsquery', 'intelligence', 'search']
            # modules = ['datasets']
            for module in modules:
                module_path = setting.module_dir.joinpath(module)
                for path in module_path.rglob('*.py'):
                    # Classes to be imported
                    import_module = ('modules.' + module, path.stem)
                    self.modules.append(import_module)
        else:
            self.modules = setting.enable_partial_module

    def import_func(self):
        """
        Import do function
        """
        for package, name in self.modules:
            import_object = importlib.import_module('.' + name, package)
            func = getattr(import_object, 'do')
            self.collect_funcs.append([func, name])

    def run(self):
        """
        Class entrance
        """
        start = time.time()
        logger.log('INFOR', f'Start collecting subdomains of {self.domain}')
        self.get_mod()
        self.import_func()

        threads = []
        # Create subdomain collection threads
        for collect_func in self.collect_funcs:
            func_obj, func_name = collect_func
            thread = threading.Thread(target=func_obj,
                                      name=func_name,
                                      args=(self.domain,),
                                      daemon=True)
            threads.append(thread)
        # Start all threads
        for thread in threads:
            thread.start()
        # Wait for all threads to finish
        for thread in threads:
            # 挨个线程判断超时 最坏情况主线程阻塞时间=线程数*module_thread_timeout
            # 超时线程将脱离主线程 由于创建线程时已添加守护属于 所有超时线程会随着主线程结束
            thread.join(setting.module_thread_timeout)

        for thread in threads:
            if thread.is_alive():
                logger.log('ALERT', f'{thread.name} module thread timed out')

        # Export
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
