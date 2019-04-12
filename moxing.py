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


def check_url(url):
    check_rule = re.compile('https?://www.*')
    if check_rule.search(url):
        print('开始运行'.center(76, '-'))
        return None
    else:
        print('内容不符合'.center(76, '-'))
        return True


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


def get_photo(zp, folderName):
    global photos
    while photos:
        photourl = None
        glock.acquire()
        if photos:
            photourl = photos.pop()
            print(threading.current_thread().name,
                  photourl, sep='：', end='\n\n')
        glock.release()
        if photourl:
            down(photourl, zp, folderName)


# 下载图片
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


# 下载网页
def downHtml(response, folderName):
    response.encoding = 'utf8'
    print('仿站完成'.center(74, '-'))
    with open('D:\\Downloads\\预览图\\{}.html'.format(folderName), 'wb') as f:
        f.write(response.content)


def clock(func):
    def w(*args, **kwargs):
        start = time.time()
        func()
        end = time.time()
        print('下载完成,耗时:{t}S'.center(76, '-').format(t=end - start))
    return w


# 上传资源
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


# 解析网页, 提取数据
def analysisPage(response):
    if response.status_code:
        global photos
        photos = re.findall(' zoomfile="(.*?)" ', response.text)  # 图片url
        folderName = PyQuery(response.text)("span#thread_subject").text()  # 标题
        for ch in r'\/:|<>?*"':
            folderName = folderName.replace(ch, ' ⁂ ')  # 去除特殊字符
        formhash = PyQuery(response.text)("input[name='formhash']").attr('value')
        urlPay = PyQuery(response.text)("ignore_js_op .tattl dd .attnm a").attr('href')
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


# 获取付费资源
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
    print(response.text)


# 创建本地保存文件夹
def mkdir(content):
    if 'Downloads' not in os.listdir('D:\\'):
        os.mkdir('D:\\Downloads\\预览图')
    # 改变当前工作目录
    os.chdir('D:\\Downloads\\预览图')
    # 创建保存文件夹
    if content['folderName'] not in os.listdir():
        os.mkdir(content['folderName'])


def main():
    login()
    while True:
        url = input('>>>:').strip()
        if check_url(url):  # 检查url是否正确
            continue
        start = time.time()
        response = requtest_header(url)
        content = analysisPage(response)
        if content:
            mkdir(content)  # 创建本地保存文件夹
            attachpay(content['formhash'], content['aid'], content['tid'])
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
            # 上传百度云
            upload_Bdyun(content['folderName'])
            end = time.time()
            print('操作完成,耗时:{t}S'.center(68, '-').format(t=end - start))
        else:
            print('找不到任何数据')


if __name__ == '__main__':
    main()
