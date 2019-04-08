# -*- coding: utf-8 -*-
# Time    : 2019/4/8 13:18
# Author  : Amd794
# Email   : 2952277346@qq.com
# Github  : https://github.com/Amd794

import requests
from fake_useragent import UserAgent
ua = UserAgent()


def downHtml(response):
    response.encoding = 'utf8'
    with open('index.html', 'wb') as f:
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
    response = requtest_header(input('>>>:'))
    downHtml(response)