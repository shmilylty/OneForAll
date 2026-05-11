from common.query import Query
import json
import os
from common.module_status import ModuleRunStatus

class Crtsh(Query):
    def __init__(self, domain):
        Query.__init__(self)
        self.domain = domain
        self.module = 'Certificate'
        self.source = 'CrtshQuery'
        self.addr = 'https://crt.sh/'
        self.status = ModuleRunStatus.SKIPPED

    def query(self):
        """
        向接口查询子域并做子域匹配
        """
        self.header = self.get_header()
        self.proxy = self.get_proxy(self.source)
        self.timeout = 120
        params = {'q': f'%.{self.domain}', 'output': 'json'}
        resp = self.get(self.addr, params, check=False, ignore=True)
        if not resp:
            self.status = ModuleRunStatus.NETWORK_ERROR
            return
            
        if resp.status_code == 429:
            self.status = ModuleRunStatus.RATE_LIMITED
            return
        elif resp.status_code != 200:
            self.status = ModuleRunStatus.FAILED
            return
            
        text = resp.text.replace(r'\n', ' ')
        """
        * > altdns
        """
        subDomains = set()
        try:
            jsonData = json.loads(text)
        except Exception as e:
            self.status = ModuleRunStatus.PARSE_ERROR
            return
            
        if not jsonData:
            self.status = ModuleRunStatus.EMPTY
            return
            
        for item in jsonData:
            try:
                name_value = str(item.get('name_value', ''))
            except Exception:
                continue
                
            if name_value:
                # Handle comma separated multiple domains
                names = [n.strip() for n in name_value.split(',')]
                for result in names:
                    result = result.lstrip('*.')
                    if result and result.endswith(self.domain):
                        self.subdomains.add(result)
                        
        if self.subdomains:
            self.status = ModuleRunStatus.SUCCESS
        else:
            self.status = ModuleRunStatus.EMPTY

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
