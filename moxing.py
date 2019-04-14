# -*- coding: utf-8 -*-
# Time    : 2019/4/8 13:18
# Author  : Amd794
# Email   : 2952277346@qq.com
# Github  : https://github.com/Amd794


import requests
import re
import os
import time
import warnings  # 捕捉警告
import threading
from fake_useragent import UserAgent
import hashlib
from zipfile import ZipFile  # 压缩文件
from bypy import ByPy  # 上传百度云
from pyquery import PyQuery  # 使用css选择器

requests = requests.Session()  # 维持会话登录状态, 让Session函数自动管理cookies
glock = threading.Lock()
ua = UserAgent()
photos = list()


# TODO 统计时间, 日志记录
def time_logger(flag=False):
    def show_time(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            print('spend %s' % (end_time - start_time))
            if flag:  # 判断是否需要写入日志模块
                print('将这个操作的时间记录到日志中')
            return result
        return wrapper
    return show_time


# TODO 登录
def login():
    data = {
        'referer ': 'https: // www.moxing.fyi',
        'username': 'Amd794',
        'password': '6be15037369879e9cf4fa9c338e497e4',
        'questionid': '0',
        'answer': ''
    }
    response = requests.post(
        url='https://www.moxing.fyi/member.php?mod=logging&action=' +
            'login&loginsubmit=yes&handlekey=login&loginhash=LEBYu&inajax=1',
        data=data)
    if '欢迎' in response.text:
        print('登录成功'.center(76, '-'))
    else:
        print('登录失败')


# TODO url检查
def check_url(url):
    check_rule = re.compile('https?://www.*')
    if check_rule.search(url):
        print('开始运行'.center(76, '-'))
        return None
    else:
        print('内容不符合'.center(76, '-'))
        return True


# TODO 请求头
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


# TODO 获取图片链接
def get_photo(zp, folderName):
    global photos
    while photos:
        photourl = None
        glock.acquire()
        if photos:
            photourl = photos.pop()
            # print(threading.current_thread().name,
            #       photourl, sep='：', end='\n\n')  # 打印正在下载的图片
        glock.release()
        if photourl:
            down(photourl, zp, folderName)


# TODO 下载预览图片, 并同时压缩备份, 防止和谐
def down(photourl, zp, folderName):
    hs = hashlib.sha1()
    hs.update(photourl.encode())
    filename, extension = os.path.splitext(photourl)  # 分离文件名和后缀
    fileName = hs.hexdigest()+extension  # 重新构建文件
    r = requests.get(url=photourl).content
    with open('./'+folderName+os.sep+fileName, 'wb') as f:
        f.write(r)
    try:
        warnings.filterwarnings('error')  # 将警告转换为异常,ignore忽略警告
        zp.write('./'+folderName+os.sep+fileName)
    except UserWarning:
        print('文件{0}已经压缩过'.format(photourl).center(76, '-'))
    except ValueError:
        print('ValueError错误')
    except Exception as e:
        with open('异常记录.txt', 'a') as f:
            f.write(str(e))


# TODO 仿站
def downHtml(response, folderName):
    response.encoding = 'utf8'
    print('仿站完成'.center(74, '-'))
    with open('D:\\Downloads\\预览图\\{}.html'.format(folderName), 'wb') as f:
        f.write(response.content)


# TODO 上传资源
def upload_Bdyun(folderName):
    bp = ByPy()
    print('正在创建存储文件夹'.center(74, '-'))
    bp.mkdir(remotepath=folderName)  # 在网盘中新建目录

    print('开始上传图片'.center(76, '-'))
    bp.upload(localpath=folderName, remotepath=folderName,
              ondup='newcopy')  # 将本地文件上传到百度云盘中

    print('开始上传压缩包'.center(76, '-'))
    bp.upload(localpath=folderName + '.rar',
              remotepath=folderName, ondup='newcopy')  # 将本地文件上传到百度云盘中

    print('开始上传网页'.center(76, '-'))
    bp.upload(localpath='{}.html'.format(folderName), remotepath=folderName,
              ondup='newcopy')  # 将本地文件上传到百度云盘中

    print('上传完毕！'.center(76, '-'))


# TODO 解析网页, 提取数据
def analysisPage(response):
    if response.status_code:
        global photos
        photos = re.findall(' zoomfile="(.*?)" ', response.text)  # 图片url
        folderName = PyQuery(response.text)("span#thread_subject").text()  # 标题
        for ch in r'\/:|<>?*"':
            folderName = folderName.replace(ch, ' ⁂ ')  # 去除特殊字符
        downHtml(response, folderName)  # 下载单页, 以方便观看
        text = PyQuery(response.text)
        # print(text)
        formhash = text("input[name='formhash']").attr('value')
        # print(formhash)
        try:
            urlPay = text("td[class='t_f'] ignore_js_op span a").attr('href')
            # print(urlPay)
            aid, tid = re.findall(r'(\d+)', urlPay)
        except TypeError:
            urlPay = text("ignore_js_op .attnm a").attr('href')
            # print(urlPay)
            aid, tid = re.findall(r'(\d+)', urlPay)
        except ValueError:
            print('该资源已经解析过了'.center(72, '-'))
            aid, tid = None, None
        return {
            'folderName': folderName,
            'formhash': formhash,
            'aid': aid,
            'tid': tid
        }
    print('当前网络不可用')
    return None


# TODO 获取付费资源
def attachpay(formhash, aid, tid):
    data = {
        'formhash': formhash,  # 关键参数, 为了服务端的session能识别, 返回正确的下载路径
        'referer': 'https://www.moxing.fyi',  # 重定向, 写不写没影响
        'aid': aid,  # 附件对应的aid
        'buyall': 'yes'  # 获取所有附件
    }
    response = requests.post(
        url='https://www.moxing.fyi/forum.php?mod=misc&action=attachpay' +
            '&tid={tid}&paysubmit=yes&infloat=yes&inajax=1'.format(tid=tid),
        data=data)
    print('付费资源解析完成: https://www.moxing.fyi/'+
          re.search("succeedhandle_\('(.*?)'", response.text).group(1))
    return response.text


# TODO 下载分析付费资源 ,每个帖子规范不一,很难统一处理
def zippay(downurl, folderName):
    response = requtest_header(downurl)
    with open('[附件]' + folderName, 'wb') as f:
        f.write(response.content)
    with ZipFile('[附件]' + folderName, 'r') as zp:
        zp.extractall(pwd=b'moxing')
        print("%-46s %19s %12s" % ("File Name", "Modified    ", "Size"),
              file=None)
        for zinfo in zp.filelist:
            date = "%d-%02d-%02d %02d:%02d:%02d" % zinfo.date_time[:6]
            print("%-46s %s %12d" % (zinfo.filename, date, zinfo.file_size),
                  file=None)
            if '.txt' in zinfo.filename:
                filename = zinfo.filename
    try:
        with open(filename, encoding='utf-8') as fr:
            print(fr.read())
    except UnicodeDecodeError:
        with open(filename, encoding='gbk') as fr:
            print(fr.read())


# TODO 创建本地保存文件夹
def mkdir(content):
    # 改变当前工作目录
    os.chdir('D:\\Downloads\\预览图')
    # 创建保存文件夹
    if content['folderName'] not in os.listdir():
        os.mkdir(content['folderName'])


# TODO 程序入口
def main():
    login()
    if '预览图' not in os.listdir('D:\\Downloads'):
        os.mkdir('D:\\Downloads\\预览图')
    while True:
        url = input('>>>:').strip()
        if check_url(url):  # 检查url是否正确
            continue
        start = time.time()
        response = requtest_header(url)
##        print(response.text)
        content = analysisPage(response)
        if content:
            mkdir(content)  # 创建本地保存文件夹
            if content['aid']:
                jsonText = attachpay(content['formhash'],
                                     content['aid'],
                                     content['tid'])  # 付费
                downurl = 'https://www.moxing.fyi/' + \
                          re.search("succeedhandle_\('(.*?)'",
                                    jsonText).group(1)  # 提取付费下载链接
            zp = ZipFile(content['folderName']+'.rar', 'a')  # 创建压缩文件指针
            Threads = list()
            for i in range(8):
                t = threading.Thread(target=get_photo,
                                     args=(zp, content['folderName'], ))
                t.start()
                Threads.append(t)
            for t in Threads:
                t.join()
            # 释放压缩文件指针
            zp.close()
            # 读取资源文本
            # zippay(downurl, content['folderName']+'.rar')
            # 上传百度云
            upload_Bdyun(content['folderName'])
            end = time.time()
            print('操作完成,耗时:{t}S'.center(68, '-').format(t=end - start))
        else:
            print('找不到任何数据')


if __name__ == '__main__':
    main()
