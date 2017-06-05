#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
# Author: Hurray(hurray0@icloud.com)
# Date: 2017.06.02 17:25:05

import sys
import re
import time
import json
import threading
from threading import Thread, Lock
import cookielib
import urllib
import urllib2

reload(sys)
sys.setdefaultencoding('utf8')


class Spider():
    """爬虫通用类"""

    def __init__(self):
        self.cookie = cookielib.MozillaCookieJar("")
        self.header = [(
            'User-agent',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14'
        ), ('DNT', '1'), ('Accept', '*/*'), ('X-Requested-With',
                                             'XMLHttpRequest')]
        handler = urllib2.HTTPCookieProcessor(self.cookie)
        self.opener = urllib2.build_opener(handler)
        self.opener.addheaders = self.header

    def open(self, url, *postData):
        """获取网页并添加/修改新的cookie到self.opener"""
        if len(postData) == 0:
            response = self.opener.open(url)
        else:
            data = urllib.urlencode(postData[0])
            response = self.opener.open(url, data)
        self.doc = response.read()

    def get(self, url, data):
        """发送get消息"""
        textmod = urllib.urlencode(data)
        req = urllib2.Request(url='%s%s%s' % (url, '?', textmod))
        self.open(req)

    def post(self, url, data):
        """发送post消息"""
        self.open(url, data)


class UCAS():
    """UCAS教务处抢课实现类"""

    def __init__(self, course, username, password):
        self.course = course
        self.username = username
        self.password = password
        self.lock = Lock()
        self.threadNum = 0
        self.errInfo = ""

    def __getThreadNum(self):
        """原子变量threadNum读操作"""
        self.lock.acquire()
        result = self.threadNum
        self.lock.release()
        return result

    def __addThreadNum(self):
        """原子变量threadNum加操作"""
        self.lock.acquire()
        self.threadNum += 1
        self.lock.release()

    def __reduceThreadNum(self):
        """原子变量threadNum减操作"""
        self.lock.acquire()
        self.threadNum -= 1
        self.lock.release()

    def getReady(self):
        """一些准备工作，提取cookie等"""
        data = {
            'username': self.username,
            'password': self.password,
            'remember': 'checked'
        }
        data2 = "deptIds=910&deptIds=911&deptIds=957&deptIds=912&deptIds=928&deptIds=913&deptIds=914&deptIds=921&deptIds=951&deptIds=952&deptIds=958&deptIds=917&deptIds=945&deptIds=927&deptIds=964&deptIds=915&deptIds=954&deptIds=955&deptIds=959&deptIds=946&deptIds=961&deptIds=962&deptIds=963&sb=0"
        data3 = "deptIds=910&deptIds=911&deptIds=957&deptIds=912&deptIds=928&deptIds=913&deptIds=914&deptIds=921&deptIds=951&deptIds=952&deptIds=958&deptIds=917&deptIds=945&deptIds=927&deptIds=964&deptIds=915&deptIds=954&deptIds=955&deptIds=959&deptIds=946&deptIds=961&deptIds=962&deptIds=963"
        url1 = "http://onestop.ucas.ac.cn/"
        url2 = "http://onestop.ucas.ac.cn/Ajax/Login/0"

        # 一系列登录cookie操作 学校的教务真麻烦。。
        spider = Spider()
        spider.open(url1)
        spider.post(url2, data)
        try:
            url3 = json.loads(spider.doc)['msg']
        except Exception as e:
            sys.stderr.write("【ERROR】账号登录出错\n")
            raise e
        spider.open(url3)
        print '【INFO】登录成功'

        url4 = "http://sep.ucas.ac.cn/portal/site/226/821"
        spider.open(url4)
        tmp = re.findall('Identity=(.*)\"\>', spider.doc)[0]

        url5 = "http://jwxk.ucas.ac.cn/login?Identity=" + tmp
        spider.open(url5)  # set new cookie

        url6 = "http://jwxk.ucas.ac.cn/courseManage/main"
        spider.open(url6)
        tmp = re.findall('\/selectCourse\?s\=(.*)\"\ class', spider.doc)[0]

        # 获取课程列表
        url7 = "http://jwxk.ucas.ac.cn/courseManage/selectCourse?s=" + tmp
        try:
            response = spider.opener.open(url7, data2)
            spider.doc = response.read()
        except:
            wait = raw_input("【ERROR】课程信息刷新失败，是否循环等待并继续抢课Y/n?")
            if not wait == 'n' and not wait == 'N':
                while True:
                    try:
                        response = spider.opener.open(url7, data2)
                        spider.doc = response.read()
                        break
                    except:
                        time.sleep(0.1)  # 100毫秒等待
                        print '【INFO】课程列表刷新中'
            else:
                raise Exception('【WARNING】暂停程序')

        print '【INFO】开始查询课程ID'
        # 根据课程号查询课程ID
        ids = []
        for item in self.course:
            try:
                s_re = "id=\"courseCode_([0-9]*)\"\>" + item[0]
                id = re.findall(s_re, spider.doc)[0]
                ids += [id]
            except IndexError as e:
                sys.stderr.write('【ERROR】课程号设置有误，其余课程继续抢课\n')
                ids += [None]

        print '【INFO】课程信息查询成功'
        # 抢课POST data生成
        for j,i in enumerate(ids):
            if not i == None:
                data3 += "&sids=" + i
                data3 += ("&did_" + i + "=" + i) if self.course[j][1] else ""

        self.url8 = "http://jwxk.ucas.ac.cn/courseManage/saveCourse?s=" + tmp
        self.spider = spider
        self.data3 = data3
        print '【INFO】获取课程信息成功'

    def getCourse(self):
        """抢课单任务"""
        self.__addThreadNum()
        spider = self.spider
        url8 = self.url8
        data3 = self.data3

        # 发送抢课消息
        try:
            response = spider.opener.open(url8, data3)
            spider.doc = response.read()
        except:
            sys.stderr.write('【WARNING】某线程超时\n')
            self.over = False if not self.over else True

        # 读取抢课结果
        info_success = re.findall("class\=\"success\"\>(.*)\<", spider.doc)[0]
        info_error = re.findall("class\=\"error\"\>(.*)\<", spider.doc)[0]
        if info_success and not self.over:
            print '【教务】【SUCCESS】' + info_success
            self.success = True
            self.over = True
        if info_error and not self.over:
            if not self.errInfo == info_error:
                self.errInfo = info_error
                print '【教务】【ERROR】' + info_error
            self.over = True

        self.__reduceThreadNum()

    def __main__(self):
        # 准备工作，如果在这里报错则说明无法登录教务。网络问题或者账号问题。
        self.success = False
        try:
            self.getReady()
        except Exception as e:
            print e.message
        else:
            self.over = False
            try:
                urllib2.socket.setdefaulttimeout(TIME_OUT)  # 连接超时时间(s)
                print '【INFO】多线程启动中'
                while not self.over:
                    if (self.__getThreadNum() >= MAX_THREAD):
                        # print '线程超数等待'
                        time.sleep(0.1)
                        pass
                    new_thread = threading.Thread(
                        target=self.getCourse, args=())
                    new_thread.start()
            except KeyboardInterrupt:
                sys.stderr.write('【WARNING】手动结束中\n')
                time.sleep(1)
                sys.stderr.write('【WARNING】手动结束\n')
                return

        print '【结果】抢课成功，请登录教务网站查看' if self.success else '【结果】抢课失败'


if __name__ == '__main__':
    # ==============================
    # 请按照需求修改下方变量
    # ==============================
    username = ''  # 教务登录email
    password = ''  # 教务登录password
    course = [
        ('091M7021H', 0),
        #('091M7010H', 1),
    ]  # 需要抢课的课程号，格式('课程号', 学位课？)，1是学位课，0是非学位课

    # 以下内容请不要轻易改动
    global MAX_THREAD  # 最大线程数
    global TIME_OUT  # 网络延时，网络不好的同学可以适当调高
    MAX_THREAD = 10
    TIME_OUT = 5

    # 程序执行
    ucas = UCAS(course, username, password)
    ucas.__main__()
