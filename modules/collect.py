import threading
import importlib
import queue

from config.log import logger
from config import settings
from common.module_status import get_module_run_records, reset_module_run_records


class Collect(object):
    def __init__(self, domain):
        self.domain = domain
        self.modules = []
        self.collect_funcs = []
        self.module_results = []
        self._result_queue = queue.Queue()

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
                    
                    # Filter deprecated and unstable if loaded automatically
                    if hasattr(settings, 'deprecated_modules') and import_module in settings.deprecated_modules:
                        continue
                    if hasattr(settings, 'unstable_modules') and import_module in settings.unstable_modules:
                        continue
                    status_mapping = getattr(settings, 'module_status', None)
                    if status_mapping is None:
                        status_mapping = getattr(settings, 'module_status_mapping', {})
                    if status_mapping.get(import_module) in {'deprecated', 'unstable', 'needs_migration', 'disabled'}:
                        continue
                        
                    self.modules.append(import_module)
        else:
            if getattr(settings, 'enable_partial_module', []):
                self.modules = settings.enable_partial_module
            elif hasattr(settings, 'recommended_modules'):
                status_mapping = getattr(settings, 'module_status', None)
                if status_mapping is None:
                    status_mapping = getattr(settings, 'module_status_mapping', {})
                self.modules = [
                    module for module in settings.recommended_modules
                    if status_mapping.get(module, 'stable') not in {'deprecated', 'unstable', 'needs_migration', 'disabled'}
                ]
            else:
                self.modules = []

    def import_func(self):
        """
        Import do function
        """
        for module in self.modules:
            name = module.split('.')[-1]
            import_object = importlib.import_module(module)
            func = getattr(import_object, 'run')
            self.collect_funcs.append([func, name])

    def execute_module(self, module_path, func):
        try:
            func(self.domain)
            self._result_queue.put({
                'module_name': module_path,
                'status': 'completed',
                'count': None,
                'error_message': '',
                'elapsed_ms': None
            })
        except Exception as exc:
            self._result_queue.put({
                'module_name': module_path,
                'status': 'failed',
                'count': None,
                'error_message': str(exc),
                'elapsed_ms': None
            })
            logger.log('ERROR', f'{module_path} execution failed: {exc}')

    def run(self):
        """
        Class entrance
        """
        logger.log('INFOR', f'Start collecting subdomains of {self.domain}')
        reset_module_run_records()
        self.get_mod()
        self.import_func()

        threads = []
        # Create subdomain collection threads
        for module_path, (func_obj, func_name) in zip(self.modules, self.collect_funcs):
            thread = threading.Thread(target=self.execute_module, name=func_name,
                                      args=(module_path, func_obj), daemon=True)
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
                self.module_results.append({
                    'module_name': thread.name,
                    'status': 'timeout',
                    'count': None,
                    'error_message': 'module thread timed out',
                    'elapsed_ms': None
                })

        while not self._result_queue.empty():
            self.module_results.append(self._result_queue.get())

        status_records = get_module_run_records()
        for result in self.module_results:
            module_name = result['module_name']
            if module_name in status_records:
                result.update(status_records[module_name])

        if self.module_results:
            for result in self.module_results:
                logger.log('DEBUG', f'Module result {result}')


if __name__ == '__main__':
    collect = Collect('example.com')
    collect.run()
