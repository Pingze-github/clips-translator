# coding=u8

from threading import Thread
from threading import Lock
import requests
import time

murl = 'http://www.iciba.com/%E6%96%B0%E9%97%BB%EF%BC%8C%E4%B9%9F%E5%8F%AB%E6%B6%88%E6%81%AF%EF%BC%8C%E6%98%AF%E6%8C%87%E9%80%9A%E8%BF%87%E6%8A%A5%E7%BA%B8%E3%80%81%E7%94%B5%E5%8F%B0%E3%80%81%E5%B9%BF%E6%92%AD%E3%80%81%E7%94%B5%E8%A7%86%E5%8F%B0%E7%AD%89%E5%AA%92%E4%BD%93%E9%80%94%E5%BE%84%E6%89%80%E4%BC%A0%E6%92%AD%E4%BF%A1%E6%81%AF%E7%9A%84%E4%B8%80%E7%A7%8D%E7%A7%B0%E8%B0%93%E3%80%82%E6%98%AF%E8%AE%B0%E5%BD%95%E7%A4%BE%E4%BC%9A%E3%80%81%E4%BC%A0%E6%92%AD%E4%BF%A1%E6%81%AF%E3%80%81%E5%8F%8D%E6%98%A0%E6%97%B6%E4%BB%A3%E7%9A%84%E4%B8%80%E7%A7%8D%E6%96%87%E4%BD%93%E3%80%82%E6%96%B0%E9%97%BB%E6%A6%82%E5%BF%B5%E6%9C%89%E5%B9%BF%E4%B9%89%E4%B8%8E%E7%8B%AD%E4%B9%89%E4%B9%8B%E5%88%86%EF%BC%8C%E5%B0%B1%E5%85%B6%E5%B9%BF%E4%B9%89%E8%80%8C%E8%A8%80%EF%BC%8C%E9%99%A4%E4%BA%86%E5%8F%91%E8%A1%A8%E4%BA%8E%E6%8A%A5%E5%88%8A%E3%80%81%E5%B9%BF%E6%92%AD%E3%80%81%E4%BA%92%E8%81%94%E7%BD%91%E3%80%81%E7%94%B5%E8%A7%86%E4%B8%8A%E7%9A%84%E8%AF%84%E8%AE%BA%E4%B8%8E%E4%B8%93%E6%96%87%E5%A4%96%E7%9A%84%E5%B8%B8%E7%94%A8%E6%96%87%E6%9C%AC%E9%83%BD%E5%B1%9E%E4%BA%8E%E6%96%B0%E9%97%BB%E4%B9%8B%E5%88%97%EF%BC%8C%E5%8C%85%E6%8B%AC%E6%B6%88%E6%81%AF%E3%80%81%E9%80%9A%E8%AE%AF%E3%80%81%E7%89%B9%E5%86%99%E3%80%81%E9%80%9F%E5%86%99%EF%BC%88%E6%9C%89%E7%9A%84%E5%B0%86%E9%80%9F%E5%86%99%E7%BA%B3%E5%85%A5%E7%89%B9%E5%86%99%E4%B9%8B%E5%88%97%EF%BC%89%E7%AD%89%E7%AD%89%EF%BC%8C%E7%8B%AD%E4%B9%89%E7%9A%84%E6%96%B0%E9%97%BB%E5%88%99%E4%B8%93%E6%8C%87%E6%B6%88%E6%81%AF%EF%BC%8C%E6%B6%88%E6%81%AF%E6%98%AF%E7%94%A8%E6%A6%82%E6%8B%AC%E7%9A%84%E5%8F%99%E8%BF%B0%E6%96%B9%E5%BC%8F%EF%BC%8C%E4%BB%A5%E8%BE%83%E7%AE%80%E6%98%8E%E6%89%BC%E8%A6%81%E7%9A%84%E6%96%87%E5%AD%97%EF%BC%8C%E8%BF%85%E9%80%9F%E5%8F%8A%E6%97%B6%E5%9C%B0%E6%8A%A5%E9%81%93%E5%9B%BD%E5%86%85%E5%A4%96%E6%96%B0%E8%BF%91%E5%8F%91%E7%94%9F%E7%9A%84%E3%80%81%E6%9C%89%E4%BB%B7%E5%80%BC%E7%9A%84%E4%BA%8B%E5%AE%9E%EF%BC%8C%E8%AE%A9%E5%88%AB%E4%BA%BA%E4%BA%86%E8%A7%A3%E3%80%82%E6%AF%8F%E5%88%99%E6%96%B0%E9%97%BB%E4%B8%80%E8%88%AC%E5%8C%85%E6%8B%AC%E6%A0%87%E9%A2%98%E3%80%81%E5%AF%BC%E8%AF%AD%E3%80%81%E4%B8%BB%E4%BD%93%E3%80%81%E8%83%8C%E6%99%AF%E5%92%8C%E7%BB%93%E8%AF%AD%E4%BA%94%E9%83%A8%E5%88%86%E3%80%82%E5%89%8D%E4%B8%89%E8%80%85%E6%98%AF%E4%B8%BB%E8%A6%81%E9%83%A8%E5%88%86%EF%BC%8C%E5%90%8E%E4%BA%8C%E8%80%85%E6%98%AF%E8%BE%85%E5%8A%A9%E9%83%A8%E5%88%86%E3%80%82%E5%86%99%E6%B3%95%E4%B8%8A%E4%B8%BB%E8%A6%81%E6%98%AF%E5%8F%99%E8%BF%B0%EF%BC%8C%E6%9C%89%E6%97%B6%E5%85%BC%E6%9C%89%E8%AE%AE%E8%AE%BA%E3%80%81%E6%8F%8F%E5%86%99%E3%80%81%E8%AF%84%E8%AE%BA%E7%AD%89%E3%80%82'

timeout = 10
thread_num = 10

def get(tid,lock,url):
    time_start = time.time()
    try:
        response = requests.get(url,timeout=timeout)
        # time_done = time.time()
        # time_use = time_done-time_start
        # lock.acquire()
        # print('[{}]{}'.format(tid,time_use))
        # lock.release()
        return response
    except:
        return None

    


def mtget(url):
    global got_tid
    got_tid = -1
    thread_list = []
    lock = Lock()
    for i in range(thread_num):
        tid = i
        thread = MyThread(get,tid,lock,url)
        thread.setDaemon(True)
        thread_list.append(thread)
    for thread in thread_list:
        thread.start()
    while(1):
        time.sleep(0.01)
        if got_tid > 0:
            return thread_list[got_tid].result


class MyThread(Thread):
    '可传递参数、指定运行函数的线程类'
    def __init__(self,target,tid,lock,url):
        super(MyThread,self).__init__()
        self.setDaemon(True)
        self.target = target
        self.tid = tid
        self.lock = lock
        self.url = url
        self.result = None
    def run(self):
        self.result = self.target(self.tid,self.lock,self.url)
        global got_tid
        got_tid = self.tid


class MtgetThread(Thread):
    '可传递参数、指定运行函数的线程类'
    def __init__(self,url):
        super(MtgetThread,self).__init__()
        self.setDaemon(True)
        self.url = url
        self.result = None
    def run(self):
        self.result = mtget(self.url)


    # for thread in thread_list:
    #     thread.join()

def main():
    r = mtget(murl)
    print(r)
    time.sleep(10) # 模拟之后程序继续运行


if __name__ == '__main__':
    main()
