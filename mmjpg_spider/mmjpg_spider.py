# coding:utf8
# python环境2.7
# 爬取网站：www.mmjpg.com

import os
import threading
import urllib2

import time
from bs4 import BeautifulSoup
from pip._vendor import requests

PATH_CONFIG = 'config.txt'
PATH_URL_DOWNLOADED = 'downloaded_url.txt'
BASE_PATH = 'mm'
HOST_MM = 'http://www.mmjpg.com/mm/'
HOST_BASE = 'http://www.mmjpg.com/'
ONE_TIME_NUM = 40
MAX_NUM = 1041

class threadDownload(threading.Thread):
    def __init__(self,path,url):
        threading.Thread.__init__(self)
        self.path = path
        self.url = url
    def run(self):
        i=0
        while downloadOnePic(self.path, self.url) == False:
            print 'redownload'
            i = i + 1
            if i > 5:
                print "timeout's time too much"
                break

def downloadUrl(url, time):
    try:
        # response = requests.get(url)
        response = urllib2.urlopen(url, timeout=5)
        response.encoding = 'utf-8'
        if response.getcode() == 200:
            return response.read()
        else:
            print "error:url visit failed"
            return ''
    except Exception, e:
        print "exception:"+e.message
        print "reopen"
        return downloadUrl(url, time+1)

def checkDocuments(path):
    if os.path.exists(path) == False:
        os.mkdir(path)
# 获取相册名称
def getPicName(picUrl) :
    picName = os.path.basename(picUrl)
    if '.jpg' in picName:
        return picName
    return 'error.jpg'
# 下载单张照片
def downloadOnePic(path,url):
    soup = BeautifulSoup(downloadUrl(url, 1),
                         'html.parser',
                         from_encoding='utf-8')
    img_node = soup.find('div', class_='content').find('img')
    pic_url = img_node.get('src')
    pic_name = getPicName(pic_url).encode('utf-8')
    try:
        content = urllib2.urlopen(pic_url, timeout=5).read()
        with open(path + '/' + pic_name, 'wb') as code:
            code.write(content)
        print '  -> ' + pic_name + " download success"
    except Exception, e:
        print "exception:"+e.message
        return False
    return True

def downloadPicAblum(url,order):
    print url
    content = downloadUrl(url, 1)
    soup = BeautifulSoup(content,
                         'html.parser',
                         from_encoding='utf-8')
    title = soup.find('div', class_='article')
    title = title.find('h2')
    pages = soup.find('div', class_='page').findAll('a')
    max_page = pages[len(pages)-2].get_text()
    path = BASE_PATH+"/"+str(order)+"-"+title.get_text().encode('utf-8')+"["+str(max_page)+"p]"
    checkDocuments(path)
    print path

    with open(PATH_URL_DOWNLOADED, 'a') as fadd:
        fadd.write(str(order)+"-"+title.get_text().encode('utf-8')+"-["+str(max_page)+"p]    "+url.encode('utf-8')+"\n")

    with open(path+'/source.html','w') as fout:
        fout.write("<html>")
        fout.write("<body>")
        fout.write("<p>"+str(order)+"-"+title.get_text().encode('utf-8')+"-["+str(max_page)+"p]"+"</p>")
        fout.write("<a href=\""+url.encode('utf-8')+"\">来源网址:"+url.encode('utf-8')+"</a>")
        fout.write("</body>")
        fout.write("</html>")
    for num in range(1, int(max_page)+1):
        pic_url = url+"/"+str(num)
        threadD = threadDownload(path,pic_url)
        threadD.start()
    while threading.active_count() != 0:
        if threading.active_count() == 1:
            print '  all pic has downloaded of this page:' + url
            return True

def getUrlByOrder(order):
    return HOST_MM+str(order)
def getCurMaxId():
    soup = BeautifulSoup(downloadUrl(HOST_BASE,1),
                         'html.parser',
                         from_encoding='utf-8')
    img_node = soup.find('a', target='_blank')
    return int(os.path.basename(img_node.get('href')))

if __name__ == "__main__":
    checkDocuments(BASE_PATH)
    checkDocuments(PATH_CONFIG)
    checkDocuments(PATH_URL_DOWNLOADED)
    order = 0

    max_id = getCurMaxId()
    with open(PATH_CONFIG, 'r') as fread:
        config = fread.read().encode('utf-8')
        if len(config) != 0:
            print config
            order = int(config)

    for i in range(order+1, max_id+1):
        downloadPicAblum(getUrlByOrder(i), i)
        with open(PATH_CONFIG, 'w') as file:
            file.write(str(i).encode('utf-8'))
        time.sleep(3)
        # 若运行中想终止爬虫程序，可在同目录下新建stop.txt文件
        if os.path.exists('stop.txt'):
            exit(0)