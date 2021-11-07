import threading
import importlib

from config.log import logger
from config import settings


class Collect(object):
    def __init__(self, domain):
        self.domain = domain
        self.modules = []
        self.collect_funcs = []

    def get_mod(self):
        """
        Get modules
        """
        if settings.enable_all_module:
            # The crawl module has some problems
            modules = ['certificates', 'check', 'datasets',
                       'dnsquery', 'intelligence', 'search']
            for module in modules:
                module_path = settings.module_dir.joinpath(module)
                for path in module_path.rglob('*.py'):
                    import_module = f'modules.{module}.{path.stem}'
                    self.modules.append(import_module)
        else:
            self.modules = settings.enable_partial_module

    def import_func(self):
        """
        Import do function
        """
        for module in self.modules:
            name = module.split('.')[-1]
            import_object = importlib.import_module(module)
            func = getattr(import_object, 'run')
            self.collect_funcs.append([func, name])

    def run(self):
        """
        Class entrance
        """
        logger.log('INFOR', f'Start collecting subdomains of {self.domain}')
        self.get_mod()
        self.import_func()

        threads = []
        # Create subdomain collection threads
        for func_obj, func_name in self.collect_funcs:
            thread = threading.Thread(target=func_obj, name=func_name,
                                      args=(self.domain,), daemon=True)
            threads.append(thread)
        # Start all threads
        for thread in threads:
            thread.start()
        # Wait for all threads to finish
        for thread in threads:
            # 挨个线程判断超时 最坏情况主线程阻塞时间=线程数*module_thread_timeout
            # 超时线程将脱离主线程 由于创建线程时已添加守护属于 所有超时线程会随着主线程结束
            thread.join(settings.module_thread_timeout)

        for thread in threads:
            if thread.is_alive():
                logger.log('ALERT', f'{thread.name} module thread timed out')


if __name__ == '__main__':
    collect = Collect('example.com')
    collect.run()
