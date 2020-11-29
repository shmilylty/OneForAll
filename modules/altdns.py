"""
Reference: https://github.com/ProjectAnte/dnsgen
"""
import re
import time
import itertools

from config import settings

from modules import wildcard
from common import utils
from common import resolve
from common import request
from common.domain import Domain
from common.module import Module
from config.log import logger


def split_domain(domain):
    """
    Split domain base on subdomain levels
    Root+TLD is taken as one part, regardless of its levels
    """

    # test.1.foo.example.com -> [test, 1, foo, example.com]
    # test.2.foo.example.com.cn -> [test, 2, foo, example.com.cn]
    # test.example.co.uk -> [test, example.co.uk]

    ext = Domain(domain).extract()
    subname = ext.subdomain
    parts = ext.subdomain.split('.') + [ext.registered_domain]
    return subname, parts


class Altdns(Module):
    def __init__(self, domain):
        Module.__init__(self)
        self.module = 'Altdns'
        self.source = 'Altdns'
        self.start = time.time()
        self.domain = domain
        self.words = set()
        self.now_subdomains = set()
        self.new_subdomains = set()
        self.wordlen = 6  # Min length of custom words extracted from domains
        self.num_count = 3

    def get_words(self):
        path = settings.data_storage_dir.joinpath('altdns_wordlist.txt')
        with open(path) as fd:
            for line in fd:
                word = line.lower().strip()
                if word:
                    self.words.add(word)

    def extract_words(self):
        """
        Extend the dictionary based on target's domain naming conventions
        """

        for subdomain in self.now_subdomains:
            _, parts = split_domain(subdomain)
            tokens = set(itertools.chain(*[word.lower().split('-') for word in parts]))
            tokens = tokens.union({word.lower() for word in parts})
            for token in tokens:
                if len(token) >= self.wordlen:
                    self.words.add(token)

    def increase_num(self, subname):
        """
        If number is found in existing subdomain,
        increase this number without any other alteration.
        """

        # test.1.foo.example.com -> test.2.foo.example.com, test.3.foo.example.com, ...
        # test1.example.com -> test2.example.com, test3.example.com, ...
        # test01.example.com -> test02.example.com, test03.example.com, ...

        count = 0
        digits = re.findall(r'\d{1,3}', subname)
        for d in digits:
            for m in range(self.num_count):
                replacement = str(int(d) + 1 + m).zfill(len(d))
                tmp_domain = subname.replace(d, replacement)
                new_domain = f'{tmp_domain}.{self.domain}'
                self.new_subdomains.add(new_domain)
                count += 1
        logger.log('DEBUG', f'The increase_num generated {count} subdomains')

    def decrease_num(self, subname):
        """
        If number is found in existing subdomain,
        decrease this number without any other alteration.
        """

        # test.4.foo.example.com -> test.3.foo.example.com, test.2.foo.example.com, ...
        # test4.example.com -> test3.example.com, test2.example.com, ...
        # test04.example.com -> test03.example.com, test02.example.com, ...

        count = 0
        digits = re.findall(r'\d{1,3}', subname)
        for d in digits:
            for m in range(self.num_count):
                new_digit = (int(d) - 1 - m)
                if new_digit < 0:
                    break

                replacement = str(new_digit).zfill(len(d))
                tmp_domain = subname.replace(d, replacement)
                new_domain = f'{tmp_domain}.{self.domain}'
                self.new_subdomains.add(new_domain)
                count += 1
        logger.log('DEBUG', f'The decrease_num generated {count} subdomains')

    def insert_word(self, parts):
        """
        Create new subdomain levels by inserting the words between existing levels
        """

        # test.1.foo.example.com -> WORD.test.1.foo.example.com,
        #                           test.WORD.1.foo.example.com,
        #                           test.1.WORD.foo.example.com,
        #                           test.1.foo.WORD.example.com,
        #                           ...

        count = 0
        for word in self.words:
            for index in range(len(parts)):
                tmp_parts = parts.copy()
                tmp_parts.insert(index, word)
                new_domain = '.'.join(tmp_parts)
                self.new_subdomains.add(new_domain)
                count += 1
        logger.log('DEBUG', f'The insert_word generated {count} subdomains')

    def add_word(self, subnames):
        """
        On every subdomain level, prepend existing content with WORD-`,
        append existing content with `-WORD`
        """

        count = 0
        for word in self.words:
            for index, name in enumerate(subnames):
                # Prepend with `-`
                # test.1.foo.example.com -> WORD-test.1.foo.example.com
                tmp_subnames = subnames.copy()
                tmp_subnames[index] = f'{word}-{name}'
                new_subname = '.'.join(tmp_subnames + [self.domain])
                self.new_subdomains.add(new_subname)

                # Prepend with `-`
                # test.1.foo.example.com -> test-WORD.1.foo.example.com
                tmp_subnames = subnames.copy()
                tmp_subnames[index] = f'{name}-{word}'
                new_subname = '.'.join(tmp_subnames + [self.domain])
                self.new_subdomains.add(new_subname)
                count += 1
        logger.log('DEBUG', f'The add_word generated {count} subdomains')

    def replace_word(self, subname):
        """
        If word longer than 3 is found in existing subdomain,
        replace it with other words from the dictionary
        """

        # WORD1.1.foo.example.com -> WORD2.1.foo.example.com,
        #                            WORD3.1.foo.example.com,
        #                            WORD4.1.foo.example.com,
        #                            ..

        count = 0
        for word in self.words:
            if word not in subname:
                continue
            for word_alt in self.words:
                if word == word_alt:
                    continue
                new_subname = subname.replace(word, word_alt)
                new_subdomain = f'{new_subname}.{self.domain}'
                self.new_subdomains.add(new_subdomain)
                count += 1
        logger.log('DEBUG', f'The replace_word generated {count} subdomains')

    def gen_new_subdomains(self):
        for subdomain in self.now_subdomains:
            subname, parts = split_domain(subdomain)
            subnames = subname.split('.')
            if settings.altdns_increase_num:
                self.increase_num(subname)
            if settings.altdns_decrease_num:
                self.decrease_num(subname)
            if settings.altdns_replace_word:
                self.replace_word(subname)
            if settings.altdns_insert_word:
                self.insert_word(parts)
            if settings.altdns_add_word:
                self.add_word(subnames)
        count = len(self.new_subdomains)
        logger.log('DEBUG', f'The altdns module generated {count} subdomains')

    def run(self, data, port):
        logger.log('INFOR', f'Start altdns module')
        self.now_subdomains = utils.get_subdomains(data)
        self.get_words()
        self.extract_words()
        self.gen_new_subdomains()
        self.subdomains = self.new_subdomains - self.now_subdomains
        count = len(self.subdomains)
        logger.log('INFOR', f'The altdns module generated {count} new subdomains')
        self.end = time.time()
        self.elapse = round(self.end - self.start, 1)
        self.gen_result()
        resolved_data = resolve.run_resolve(self.domain, self.results)
        valid_data = wildcard.deal_wildcard(resolved_data)  # 强制开启泛解析处理
        request.run_request(self.domain, valid_data, port)
