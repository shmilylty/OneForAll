from common.query import Query
import json
import os


class Crtsh(Query):
    def __init__(self, domain):
        Query.__init__(self)
        self.domain = domain
        self.module = 'Certificate'
        self.source = 'CrtshQuery'
        self.addr = 'https://crt.sh/'

    def query(self):
        """
        向接口查询子域并做子域匹配
        """
        self.header = self.get_header()
        self.proxy = self.get_proxy(self.source)
        self.timeout = 120
        params = {'q': f'%.{self.domain}', 'output': 'json'}
        resp = self.get(self.addr, params)
        if not resp:
            return
        text = resp.text.replace(r'\n', ' ')
        """
        * > altdns
        """
        subDomains = set()
        try:
            jsonData = json.loads(text)
        except Exception as e:
            pass
        for i in range(len(jsonData)):
            try:
                name_value = str(jsonData[i]['name_value'])
            except Exception as e:
                pass
            if '*' in name_value:
                try:
                    if 'certificates' in os.path.dirname(os.path.abspath(__file__)):
                        dictFile = open("../../data/altdns_wordlist.txt", "r", encoding='utf8')
                    else:
                        dictFile = open("./data/altdns_wordlist.txt", "r", encoding='utf8')
                    for line in dictFile.readlines():
                        altdns = line.strip()
                        result = name_value.replace('*', altdns)
                        if self.domain in result:
                            subDomains.add(result)
                except Exception as e:
                    pass
        if len(subDomains) > 0:
            for x in subDomains:
                text = text + ',' + x + ','
        """
        * > altdns end
        """
        subdomains = self.match_subdomains(text)
        self.subdomains.update(subdomains)

    def run(self):
        """
        类执行入口
        """
        self.begin()
        self.query()
        self.finish()
        self.save_json()
        self.gen_result()
        self.save_db()


def run(domain):
    """
    类统一调用入口

    :param str domain: 域名
    """
    query = Crtsh(domain)
    query.run()


if __name__ == '__main__':
    run('163.com')
