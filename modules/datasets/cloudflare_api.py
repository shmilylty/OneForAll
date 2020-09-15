from config import settings
from common.query import Query
from config.log import logger
from time import sleep


class CloudFlareAPI(Query):

    def __init__(self, domain):
        Query.__init__(self)
        self.domain = domain
        self.module = 'Dataset'
        self.source = 'CloudFlareAPIQuery'
        self.token = settings.cloudflare_api_token
        self.addr = 'https://api.cloudflare.com/client/v4/'
        self.header = self.get_header()
        self.header.update({'Authorization': 'Bearer ' + self.token})
        self.header.update({'Content-Type': 'application/json'})
        self.proxy = self.get_proxy(self.source)

    def query(self):
        """
        query from source
        """
        account_id_resp = self.get(self.addr + 'accounts')
        if account_id_resp:
            if account_id_resp.status_code != 200:
                return
        else:
            return
        result = account_id_resp.json()['result']
        if not result:
            return
        account_id = result[0]['id']
        # query domain zone, if it not exist, create
        zones_resp = self.get(self.addr + 'zones',
                              params={'name': self.domain}, check=False)
        if zones_resp:
            if zones_resp.status_code == 200:
                if zones_resp.json()['success'] and not zones_resp.json()['result']:
                    zone_id = self.create_zone(account_id)
                    if zone_id:
                        self.list_dns(zone_id)
                        return
                    return
                elif zones_resp.json()['success']:
                    zone_id = self.create_zone(account_id)
                    if zone_id:
                        self.list_dns(zone_id)
                    return
            elif zones_resp.status_code == 403:
                logger.log('DEBUG',
                           f'{self.domain} is banned or not a registered domain, '
                           f'so cannot be added to Cloudflare.')
                return
            else:
                logger.log('DEBUG',
                           f'{zones_resp.status_code} {zones_resp.text}')
        return

    def create_zone(self, account_id):
        data = {"name": self.domain, "account": {"id": account_id},
                "jump_start": True, "type": "full"}
        create_zone_resp = self.post(self.addr + 'zones', json=data, check=False)
        if not create_zone_resp:
            logger.log('DEBUG', f'{create_zone_resp.status_code} {create_zone_resp.text}')
            return False
        if create_zone_resp.json()['success']:
            return create_zone_resp.json()['result']['id']
        else:
            logger.log('DEBUG', f'{self.domain} is temporarily banned '
                                f'and cannot be added to Cloudflare')
            return False

    def list_dns(self, zone_id):
        page = 1
        list_dns_resp = self.get(self.addr + f'zones/{zone_id}/dns_records',
                                 params={'page': page, 'per_page': 10})
        if not list_dns_resp:
            logger.log('DEBUG',
                       f'{list_dns_resp.status_code} {list_dns_resp.text}')
            return
        subdomains = self.match_subdomains(list_dns_resp.text)
        self.subdomains.update(subdomains)
        if not self.subdomains:
            # waiting for cloudflare enumerate subdomains
            sleep(5)
            self.list_dns(zone_id)
        else:
            while True:
                list_dns_resp = self.get(self.addr + f'zones/{zone_id}/dns_records',
                                         params={'page': page, 'per_page': 10})
                if not list_dns_resp:
                    logger.log('DEBUG',
                               f'{list_dns_resp.status_code} {list_dns_resp.text}')
                    return
                total_pages = list_dns_resp.json()['result_info']['total_pages']
                subdomains = (self.match_subdomains(list_dns_resp.text))
                self.subdomains.update(subdomains)
                page += 1
                if page > total_pages:
                    break
            return

    def run(self):
        """
        class entrance
        """
        if not self.have_api(self.token):
            return
        self.begin()
        self.query()
        self.finish()
        self.save_json()
        self.gen_result()
        self.save_db()


def run(domain):
    """
    class call entrance

    :param str domain: 域名
    """
    query = CloudFlareAPI(domain)
    query.run()


if __name__ == '__main__':
    run('example.com')
