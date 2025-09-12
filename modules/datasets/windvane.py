from config import settings
from common.query import Query


class Windvane(Query):
    def __init__(self, domain):
        Query.__init__(self)
        self.domain = domain
        self.module = 'Dataset'
        self.source = "WindvaneQuery"
        self.addr = 'https://windvane.lichoin.com/trpc.backendhub.public.WindvaneService/ListSubDomain'
        self.api_key = settings.windvane_api_token
        self.page_size = 1000
        
    def query(self):
        """
        向接口查询子域并做子域匹配
        """
        self.header = self.get_header()
        self.header.update({
            'Content-Type': 'application/json',
            'Referer': 'https://windvane.lichoin.com'
        })
        
        if self.api_key:
            self.header.update({'X-Api-Key': self.api_key})
            
        self.proxy = self.get_proxy(self.source)
        
        page = 1
        total_pages = 1
        all_subdomains = []
        
        while page <= total_pages:
            data = {
                "domain": self.domain,
                "page_request": {
                    "page": page,
                    "count": self.page_size
                }
            }
            
            resp = self.post(self.addr, json=data)
            if not resp:
                break
                
            try:
                result = resp.json()
                
                if result.get('code') != 0:
                    break
                
                data_section = result.get('data', {})

                subdomains = self.match_subdomains(resp)
                if not subdomains:
                    break
                self.subdomains.update(subdomains)
                
                page_info = data_section.get('page_response', {})
                total_pages = int(page_info.get('total_page', 1))
                
                page += 1
                
            except:
                break
        

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
    query = Windvane(domain)
    query.run()


if __name__ == '__main__':
    run('baidu.com')
