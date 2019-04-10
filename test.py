# -*- coding: utf-8 -*-
# Time    : 2019/4/8 13:18
# Author  : Amd794
# Email   : 2952277346@qq.com
# Github  : https://github.com/Amd794

import requests
from fake_useragent import UserAgent
ua = UserAgent()
requests = requests.Session()


def login():
    data = {
        'referer ': 'https: // www.moxing.fyi',
        'username': 'Amd794',
        'password': '6be15037369879e9cf4fa9c338e497e4',
        'questionid': '0',
        'answer': ''
    }
    response = requests.post(
        url='https://www.moxing.fyi/member.php?mod=logging&action=login&loginsubmit=yes&handlekey=login&loginhash=LEBYu&inajax=1',
        data=data)
    print(response.text)

def downHtml(response):
    response.encoding = 'utf8'
    with open('test.html', 'wb') as f:
        f.write(response.content)


def requtest_header(url):
    header = {
        'User-Agent': ua.random
    }
    count = 0
    while count < 3:
        try:
            return requests.get(url=url, headers=header, timeout=5)
        except requests.exceptions.RequestException as e:
            print('超时,正在重试......')
            count += 1
    else:
        print('这个链接已被抛弃.......')
        return None


if __name__ == '__main__':
    login()
    response = requtest_header(input('>>>:'))
    downHtml(response)