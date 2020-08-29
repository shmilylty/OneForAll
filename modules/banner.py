import re
import os
import time
import json
import string
import hashlib
import tqdm

from multiprocessing import Pool, Process, freeze_support
from multiprocessing import Manager

from bs4 import BeautifulSoup
from http.cookies import SimpleCookie

from common import utils
from common.module import Module
from config import settings
from config.log import logger


class MultiIdentify(Module):
    def __init__(self):
        Module.__init__(self)
        self.module = 'Identify'
        self.source = 'Identify'
        self.start = time.time()  # 模块开始执行时间
        self.rule_dir = settings.data_storage_dir.joinpath('rules')

    def run(self, data):
        logger.log('INFOR', f'Start Identify module')
        freeze_support()
        task_queue = Manager().Queue()
        done_queue = Manager().Queue()
        n = 0
        for d in data:
            if d.get('request'):
                n += 1
                task_queue.put(d)
        processes_num = min(settings.banner_process_number, os.cpu_count())
        logger.log('INFOR', f'Creating {processes_num} processes to identify')
        p = Process(target=self.listener, args=(n, done_queue,))
        p.start()
        pool = Pool(processes_num)
        rules = self.load_rules()
        _identify = Identify(rules)
        for i in range(processes_num):
            pool.apply_async(func=_identify.run, args=(task_queue, done_queue))
        pool.close()
        pool.join()
        p.join()
        result_data = done_queue.get()
        self.end = time.time()
        self.elapse = round(self.end - self.start, 1)
        logger.log('ALERT', f'The Identify module took {self.elapse} seconds')
        return result_data

    @staticmethod
    def listener(total, done_queue):
        par = tqdm.tqdm(total=total, desc='Identify Progress', ncols=80)
        result_data = []
        while len(result_data) < total:
            result_data.append(done_queue.get())
            par.update()
        done_queue.put(result_data)

    def load_rules(self):
        new_rules = {}
        new_rule_types = set()
        for rule_type in os.listdir(self.rule_dir):
            rule_type_dir = os.path.join(self.rule_dir, rule_type)
            if not os.path.isdir(rule_type_dir):
                continue
            new_rule_types.add(rule_type)
            for i in os.listdir(rule_type_dir):
                if not i.endswith('.json'):
                    continue

                with open(os.path.join(rule_type_dir, i), encoding='utf-8') as fd:
                    try:
                        data = json.load(fd)
                        for match in data['matches']:
                            if 'regexp' in match:  # 默认 大小写不敏感 可信度100%
                                match['regexp'] = re.compile(
                                    match['regexp'], re.I)
                            if 'certainty' not in match:
                                match['certainty'] = 100

                        data['origin'] = rule_type
                        key = '%s_%s' % (rule_type, data['name'])
                        new_rules[key] = data
                    except Exception as e:
                        logger.log('ERROR', f'Parse {i} failed, error: {e}')

        RULES = new_rules
        RULE_TYPES = new_rule_types
        return len(RULES), RULES, RULE_TYPES


class Identify(object):
    def __init__(self, rules):
        self.start = time.time()  # 模块开始执行时间
        self._targets = {}
        self._cond_parser = Condition()
        self.url = ''
        self.rules_num, self.RULES, self.RULE_TYPES = rules

    def run(self, task_queue, done_queue):
        while not task_queue.empty():
            item = task_queue.get()
            if not item.get('request'):
                done_queue.put(item)
                continue
            self.url = item.get('url')
            implies = set()
            excludes = set()
            self.parse(item)
            banners = []
            for name, rule in self.RULES.items():
                # print(name)
                r = self._check_rule(rule)
                if r:
                    if 'implies' in rule:
                        if isinstance(rule['implies'], str):
                            implies.add(rule['implies'])
                        else:
                            implies.update(rule['implies'])

                    if 'excludes' in rule:
                        if isinstance(rule['excludes'], str):
                            excludes.add(rule['excludes'])
                        else:
                            excludes.update(rule['excludes'])

                    if r['name'] in excludes:
                        continue
                    banners.append(r)

            for imply in implies:
                _result = {
                    'name': imply,
                    "origin": 'implies'
                }
                for rule_type in self.RULE_TYPES:
                    rule_name = '%s_%s' % (rule_type, imply)
                    rule = self.RULES.get(rule_name)
                    if not rule:
                        continue
                    if 'excludes' in rule:
                        if isinstance(rule['excludes'], str):
                            excludes.add(rule['excludes'])
                        else:
                            excludes.update(rule['excludes'])
                if _result['name'] in excludes:
                    continue
                banners.append(_result)
            item['banner'] = self.deal_output(banners)
            # print(item['banner'])
            done_queue.put(item)
        return

    @staticmethod
    def deal_output(banners):
        result = []
        for banner in banners:
            if 'version' in banner:
                version = 'v' + banner['version']
                result.append(banner['name'] + ' ' + version)
            else:
                result.append(banner['name'])
        result = ','.join(result)
        return result

    def parse(self, item):
        script = []
        meta = {}
        if item.get('response'):
            p = BeautifulSoup(item.get('response'), "html.parser")
            for i in p.find_all("script"):
                script_src = i.get("src")
                if script_src:
                    script.append(script_src)

            for i in p.find_all("meta"):
                meta_name = i.get("name")
                meta_content = i.get("content", "")
                if meta_name:
                    meta[meta_name] = meta_content

        title = item.get("title")
        if 'Set-Cookie' in json.loads(item.get('header')):
            cookies = json.loads(item.get('header'))['Set-Cookie'].lower()
        else:
            cookies = None
        self._targets[self.url] = {
            "url": self.url,
            "body": item.get('response'),
            "headers": json.loads(item.get('header')),
            "status": item.get('status_code'),
            "script": script,
            "meta": meta,
            "title": title,
            "cookies": SimpleCookie(cookies),
            "raw_cookies": cookies,
            "raw_response": item.get('header') + item.get('response'),
            "raw_headers": item.get('header'),
            "md5": hashlib.md5(item.get('response').encode('utf-8')),
        }

    def _check_match(self, match: hash) -> (bool, str):
        s = {
            'regexp',
            'text',
            # 'md5',  # 因为删除了主动式识别 所以md5 status方式失效
            # 'status'
        }  # 如果增加新的检测方式，需要修改这里
        if not s.intersection(list(match.keys())):  # 判断 传进的规则类型 和s里规定的类型是否符合
            return False, None

        target = self._targets[self.url]

        # parse search
        search_context = target['body']
        if 'search' in match:
            if match['search'] == 'all':
                search_context = target['raw_response']
            elif match['search'] == 'headers':
                search_context = target['raw_headers']
            elif match['search'] == 'script':
                search_context = target['script']
            elif match['search'] == 'title':
                search_context = target['title']
            elif match['search'] == 'cookies':
                search_context = target['raw_cookies']
            elif match['search'].endswith(']'):
                for i in ('headers', 'meta', 'cookies'):
                    if not match['search'].startswith('%s[' % i):
                        continue
                    key = match['search'][len('%s[' % i):-1]
                    if i == 'headers':  # header首字母大写
                        key = key.title()
                    if key not in target[i]:
                        return False, None
                    search_context = target[i][key]
            match.pop('search')
        version = match.get('version', None)
        for key in list(match.keys()):
            if key == 'text':
                search_contexts = search_context
                if isinstance(search_context, str):
                    search_contexts = [search_context]

                for search_context in search_contexts:
                    if match[key] not in search_context:
                        continue
                    break
                else:
                    return False, None

            if key == 'regexp':
                search_contexts = search_context
                if isinstance(search_context, str):
                    search_contexts = [search_context]

                for search_context in search_contexts:
                    result = match[key].findall(search_context)
                    if not result:
                        continue

                    if 'offset' in match:
                        if isinstance(result[0], str):
                            version = result[0]
                        elif isinstance(result[0], tuple):
                            if len(result[0]) > match['offset']:
                                version = result[0][match['offset']]
                            else:
                                version = ''.join(result[0])
                    break
                else:
                    return False, None

        return True, version

    def _check_rule(self, rule):
        matches = rule['matches']

        cond_map = {}
        result = {
            'name': rule['name'],
            'origin': rule['origin']
        }

        for index, match in enumerate(matches):
            is_match, version = self._check_match(match)
            if is_match:
                cond_map[str(index)] = True
                if version:
                    result['version'] = version
            else:
                cond_map[str(index)] = False

        # default or
        if 'condition' not in rule:
            if any(cond_map.values()):
                return result
            return

        if self._cond_parser.parse(rule['condition'], cond_map):
            return result


def save_db(domain, data):
    logger.log('INFOR', f'Saving Identify results')
    utils.save_db(domain, data, 'Identify')


__all__ = ["Condition", "ParseException"]

EOF = -1

TOKEN_TYPE = {
    'not': 'NOT',
    'and': 'AND',
    'or': 'OR',
    '(': 'LP',
    ')': 'RP',
    'variable': 'VARIABLE',
    'eof': 'EOF'
}


class ParseException(Exception):
    pass


class Token(object):
    def __init__(self, type: TOKEN_TYPE, name: str = '', value: bool = False):
        self.type = type
        self.name = name
        self.value = value

    def __str__(self):
        return '<Token {} {}>'.format(self.type, self.name)

    __repr__ = __str__


class Result(object):
    def __init__(self, name: str, value: bool):
        self.name = name
        self.value = value

    def __str__(self):
        return '<result {} = {}>'.format(self.name, self.value)

    __repr__ = __str__


class Condition(object):
    def __init__(self):
        self.condstr = ''
        self.index = 0
        self.back_tokens = []
        self.symbol_table = {}

        self.allow_character = string.ascii_lowercase + string.digits + '_'
        self.ignore_character = ' \t'

    def _get_token(self):
        while self.index < len(self.condstr):
            if self.condstr[self.index] in self.ignore_character:
                self.index += 1
                continue

            if self.condstr[self.index: self.index + 2] == 'or' and \
                    self.condstr[self.index + 2] not in self.allow_character:
                name = self.condstr[self.index: self.index + 2]
                self.index += 2
                return Token(TOKEN_TYPE[name])

            elif self.condstr[self.index: self.index + 3] in ('not', 'and') and \
                    self.condstr[self.index + 3] not in self.allow_character:
                name = self.condstr[self.index: self.index + 3]
                self.index += 3
                return Token(TOKEN_TYPE[name])

            elif self.condstr[self.index] in ('(', ')'):
                name = self.condstr[self.index]
                self.index += 1
                return Token(TOKEN_TYPE[name])

            else:
                name = []
                while self.index < len(self.condstr) and self.condstr[self.index] \
                        in self.allow_character:
                    name.append(self.condstr[self.index])
                    self.index += 1

                name = ''.join(name)
                if name not in self.symbol_table:
                    raise ParseException('{} does not exists'.format(name))

                return Token(
                    TOKEN_TYPE['variable'],
                    name,
                    self.symbol_table[name])

        return Token(TOKEN_TYPE['eof'])

    def pop_token(self):
        if self.back_tokens:
            return self.back_tokens.pop(0)
        try:
            return self._get_token()
        except IndexError:
            raise ParseException('invalid condition "%s"', self.condstr)

    def push_token(self, token):
        self.back_tokens.append(token)

    def parse_var_expression(self):
        """
        v_exp := VARIABLE
        """
        token = self.pop_token()
        if token.type == TOKEN_TYPE['eof']:
            return Result(name='', value=False)

        if token.type != TOKEN_TYPE['variable']:
            raise ParseException('invalid condition "%s"' % self.condstr)

        return Result(name=token.name, value=token.value)

    def parse_primary_expression(self):
        """
        p_exp := (exp)
        """
        token = self.pop_token()
        if token.type == TOKEN_TYPE['eof']:
            return Result(name='', value=False)
        elif token.type != TOKEN_TYPE['(']:
            self.push_token(token)
            return self.parse_var_expression()

        r = self.parse_expression()

        token = self.pop_token()
        if token.type != TOKEN_TYPE[')']:
            raise ParseException('invalid condition "%s"' % self.condstr)

        return r

    def parse_not_expression(self):
        """
        n_exp := NOT n_exp | NOT p_exp
        """
        token = self.pop_token()
        if token.type == TOKEN_TYPE['eof']:
            return Result(name='', value=False)
        elif token.type != TOKEN_TYPE['not']:
            self.push_token(token)
            return self.parse_primary_expression()

        r1 = self.parse_not_expression()

        r = Result('(not {})'.format(r1.name), not r1.value)
        logger.debug('[*] {}'.format(r))
        return r

    def parse_and_expression(self):
        """
        and_exp := and_exp AND n_exp
        """
        r1 = self.parse_not_expression()
        if not r1.name and not r1.value:
            return r1

        while True:
            token = self.pop_token()
            if token.type == TOKEN_TYPE['eof']:
                break

            if token.type != TOKEN_TYPE['and']:
                self.push_token(token)
                return r1

            r2 = self.parse_not_expression()
            if not r2.name and not r2.value:
                raise ParseException('invalid condition "%s"', self.condstr)

            r1 = Result(
                '({} and {})'.format(
                    r1.name,
                    r2.name),
                r1.value and r2.value)
            logger.debug('[*] {}'.format(r1))

        return r1

    def parse_or_expression(self):
        """
        or_exp := or_exp OR and_exp
        """
        r1 = self.parse_and_expression()
        if not r1.name and not r1.value:
            return r1

        while True:
            token = self.pop_token()
            if token.type == TOKEN_TYPE['eof']:
                break

            elif token.type != TOKEN_TYPE['or']:
                self.push_token(token)
                return r1

            r2 = self.parse_and_expression()
            if not r2.name and not r2.value:
                raise ParseException('invalid condition "%s"', self.condstr)

            r1 = Result(
                '({} or {})'.format(
                    r1.name,
                    r2.name),
                r1.value or r2.value)
            logger.debug('[*] {}'.format(r1))

        return r1

    def parse_expression(self):
        """
        exp := or_exp
        """
        return self.parse_or_expression()

    def parse(self, condstr, symbol_table):
        self.condstr = condstr.lower()
        self.symbol_table = symbol_table
        self.index = 0
        self.back_tokens = []

        result = self.parse_expression()

        if self.back_tokens:
            raise ParseException('invalid condition "%s"', self.condstr)

        return result.value
