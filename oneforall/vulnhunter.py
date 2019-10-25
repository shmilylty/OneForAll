#!/usr/bin/python3
# coding=utf-8

"""
OneForAll写入WEB平台模块

:copyright: Copyright (c) 2019, JrD. All rights reserved.
:license: GNU General Public License v3.0, see LICENSE for more details.
"""

import os
import pathlib
import sys
import django
import time
from config import logger


def save_subdomain(datas, vulnhunter, domain):
    dir = pathlib.Path.cwd()
    sys.path.append(dir.as_posix())
    os.environ['DJANGO_SETTINGS_MODULE'] = 'VulnHunterPlatform.settings'  # 装载vulnhunter项目的settings
    django.setup()
    from AssetManage.models import SubDomain
    start = time.time()
    num = 0
    for i in datas:
        if i['valid'] == 1:
            num += 1
            try:
                subdomain_create = SubDomain.objects.update_or_create(
                    project=vulnhunter,
                    url=i['url'],
                    subdomain=i['subdomain'],
                    port=i['port'],
                    ips=i['ips'][1:-1],
                    status=i['status'],
                    title=i['title'],
                    banner=i['banner'][1:-1],
                    domain=domain
                )
            except django.db.utils.IntegrityError:
                pass
    end = time.time()
    elapsed = round(end - start, 1)
    logger.log('INFOR', f'VulnHunter模块耗时{elapsed}秒'
    f'写入了{num}个子域')
