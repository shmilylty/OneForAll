"""
通过枚举域名常见的SRV记录并做查询来发现子域
"""

import queue
import threading

from common import utils
from common.module import Module
from config.setting import data_storage_dir


class BruteSRV(Module):
    def __init__(self, domain):
        Module.__init__(self)
        self.domain = domain
        self.module = 'BruteSRV'
        self.source = "BruteSRV"
        self.qtype = 'SRV'
        self.thread_num = 20
        self.names_queue = queue.Queue()
        self.answers_queue = queue.Queue()

    def fill_queue(self):
        path = data_storage_dir.joinpath('srv_prefixes.json')
        prefixes = utils.load_json(path)
        for prefix in prefixes:
            self.names_queue.put(prefix + self.domain)

    def do_brute(self):
        for num in range(self.thread_num):
            thread = BruteThread(self.names_queue, self.answers_queue)
            thread.name = f'BruteThread-{num}'
            thread.daemon = True
            thread.start()
        self.names_queue.join()

    def deal_answers(self):
        while not self.answers_queue.empty():
            answer = self.answers_queue.get()
            if answer is None:
                continue
            for item in answer:
                record = str(item)
                subdomains = self.match_subdomains(record)
                self.subdomains.update(subdomains)

    def run(self):
        self.begin()
        self.fill_queue()
        self.do_brute()
        self.deal_answers()
        self.finish()
        self.save_json()
        self.gen_result()
        self.save_db()


class BruteThread(threading.Thread):
    def __init__(self, names_queue, answers_queue):
        threading.Thread.__init__(self)
        self.names_queue = names_queue
        self.answers_queue = answers_queue

    def run(self):
        while True:
            name = self.names_queue.get()
            answer = utils.dns_query(name, 'SRV')
            self.answers_queue.put(answer)
            self.names_queue.task_done()


if __name__ == '__main__':
    brute = BruteSRV('zonetransfer.me')
    brute.run()
