# -*- coding: utf-8 -*-
# Time    : 2019/4/8 13:18
# Author  : Amd794
# Email   : 2952277346@qq.com
# Github  : https://github.com/Amd794

import requests
import re
from pyquery import PyQuery
from fake_useragent import UserAgent

ua = UserAgent()
requests = requests.Session()
from zipfile import ZipFile
import zipfile


# TODO 登录
def login():
    data = {
        'username': 'Amd794',
        'password': '6be15037369879e9cf4fa9c338e497e4'
    }
    response = requests.post(
        url='https://www.moxing.world/member.php?mod=logging&action=' +
            'login&loginsubmit=yes&handlekey=login&loginhash=LEBYu&inajax=1',
        data=data)
    if '欢迎' in response.text:
        print('登录成功'.center(76, '-'))
    else:
        print('登录失败')
        print(response.text)


def downHtml(response, folderName):
    response.encoding = 'utf8'
    print('仿站完成'.center(74, '-'))
    with open('D:\\Downloads\\预览图\\{}.html'.format(folderName), 'wb') as f:
        f.write(response.content)


def requtest_header(url):
    header = {
        'User-Agent': ua.random
    }
    count = 0
    while count < 3:
        try:
            return requests.get(url=url, headers=header, timeout=5)
        except requests.exceptions.RequestException:
            print('超时,正在重试......')
            count += 1
    else:
        print('这个链接已被抛弃.......')
        return None


# 获取付费资源
def attachpay(formhash, aid, tid):
    data = {
        'formhash': formhash,  # 关键参数, 为了服务端的session能识别, 返回正确的下载路径, 一般这个formhash 在页面hidden
        'referer': 'https://www.moxing.world',  # 重定向, 写不写没影响
        'aid': aid,  # 附件对应的aid
        'buyall': 'yes'  # 获取所有附件
    }
    response = requests.post(
        url='https://www.moxing.world/forum.php?mod=misc&action=attachpay' +
            '&tid={tid}&paysubmit=yes&infloat=yes&inajax=1'.format(tid=tid),
        data=data)
    print(response.text)


def analysisPage(response):
    if response.status_code:
        global photos
        photos = re.findall(' zoomfile="(.*?)" ', response.text)  # 图片url
        folderName = PyQuery(response.text)("span#thread_subject").text()  # 标题
        for ch in r'\/:|<>?*"':
            folderName = folderName.replace(ch, ' ⁂ ')  # 去除特殊字符
        formhash = PyQuery(response.text)("input[name='formhash']").attr('value')
        print(folderName)
        print(formhash)
        urlPay = PyQuery(response.text)("td[class='t_f'] ignore_js_op span a").attr('href')
        # print(urlPay,type(urlPay))
        aid, tid = re.findall(r'(\d+)', urlPay)
        downHtml(response, folderName)  # 下载单页, 以方便观看
        return {
            'folderName': folderName,
            'formhash': formhash,
            'aid': aid,
            'tid': tid
        }
    print('当前网络不可用')
    return None


if __name__ == '__main__':
    # with open('test.txt',encoding='utf8') as f:
    #     print('https://www.moxing.world/'+ re.search("succeedhandle_\('(.*?)'", f.read()).group(1))
    login()
    # url = input(">>>:").strip()
    # # url = 'https://www.moxing.world/forum.php?mod=attachment&aid=NjAwMDA0fDdkNmM4NTQ5fDE1NTUxMzA1NTB8OTY0MTl8OTA5MDc%3D'
    # response = requtest_header(url)
    # # print(analysisPage(response))
    # with open('test.zip', 'wb') as f:
    #     f.write(response.content)
    # with ZipFile('test.zip', 'r') as zp:
    #     zp.extractall(pwd=b'moxing')
    #     print("%-46s %19s %12s" % ("File Name", "Modified    ", "Size"),
    #           file=None)
    #     for zinfo in zp.filelist:
    #         date = "%d-%02d-%02d %02d:%02d:%02d" % zinfo.date_time[:6]
    #         print("%-46s %s %12d" % (zinfo.filename, date, zinfo.file_size),
    #               file=None)
    #         if '.txt' in zinfo.filename:
    #             filename = zinfo.filename
    # try:
    #     with open(filename,encoding='utf-8') as fr:
    #         print(fr.read())
    # except UnicodeDecodeError:
    #     with open(filename,encoding='gbk') as fr:
    #         print(fr.read())
