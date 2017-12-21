# -*-coding:utf8-*-

import requests
import json
import random
import pymysql
import sys
import datetime
import time
from imp import reload
from multiprocessing.dummy import Pool as ThreadPool
import threading
from queue import Queue




def datetime_to_timestamp_in_milliseconds(d):
    def current_milli_time(): return int(round(time.time() * 1000))

    return current_milli_time()


reload(sys)
head = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'http://space.bilibili.com/45388',
    'Origin': 'http://space.bilibili.com',
    'Host': 'space.bilibili.com',
    'AlexaToolbar-ALX_NS_PH': 'AlexaToolbar/alx-4.0',
    'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,ja;q=0.4',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
}



def get_ip(file):
    with open(file, 'r') as f:
        ips = f.readlines()
    proxys = []
    for p in ips:
        # print(ip)
        proxy = 'http://' + p.strip('\n')
        proxies = {'http': proxy}
        proxys.append(proxies)
    return proxys


def get_UserAgents(uafile):
    """
    uafile : string
        path to text file of user agents, one per line
    """
    uas = []
    with open(uafile, 'rb') as uaf:
        for ua in uaf.readlines():
            if ua:
                uas.append(ua.strip()[1:-1 - 1])
    random.shuffle(uas)
    return uas
uas = get_UserAgents("user_agents.txt")
proxys = get_ip('ip2.txt')
time1 = time.time()

def get_data(url):
    data = {
        '_': datetime_to_timestamp_in_milliseconds(datetime.datetime.now()),
        'mid': url.replace('https://space.bilibili.com/', '')
    }
    ua = random.choice(uas)
    proxy = random.choice(proxys)
    headers = {
        'User-Agent': ua,
        'Referer': url + '?from=search&seid=' + str(random.randint(10000, 50000))
    }
    jscontent = '{"name":"test", "type":{"name":"seq", "parameter":["1", "2"]}}'
    try:
        jscontent = requests \
            .session() \
            .post('http://space.bilibili.com/ajax/member/GetInfo',
                  headers=headers,
                  data=data,
                  proxies=proxy, timeout=10) \
            .text
    except:
        pass
    time2 = time.time()
    # print(jscontent)
    try:
        jsDict = json.loads(jscontent)
        statusJson = jsDict['status'] if 'status' in jsDict.keys() else False
        if statusJson == True:
            if 'data' in jsDict.keys():
                jsData = jsDict['data']
                mid = jsData['mid']
                name = jsData['name']
                sex = jsData['sex']
                face = jsData['face']
                spacesta = jsData['spacesta']
                birthday = jsData['birthday'] if 'birthday' in jsData.keys() else 'nobirthday'
                place = jsData['place'] if 'place' in jsData.keys() else 'noplace'
                playnum = jsData['playNum']
                sign = jsData['sign']
                level = jsData['level_info']['current_level']
                exp = jsData['level_info']['current_exp']
                print("Succeed: " + mid + "\t" + str(time2 - time1))
                try:
                    res = requests.get('http://api.bilibili.com/x/relation/stat?vmid=' + mid + '&jsonp=jsonp').text
                    js_fans_data = json.loads(res)
                    following = js_fans_data['data']['following']
                    fans = js_fans_data['data']['follower']
                except:
                    following = 0
                    fans = 0
            else:
                print('no data now')
            try:
                print(1)
                conn = pymysql.connect(
                    host='localhost', user='root', passwd='123456', db='bilibili', charset='utf8')
                cur = conn.cursor()
                print(2)
                sql = 'INSERT INTO data(mid, name, sex, face, spacesta, \
                    birthday, place, following, fans, playnum, sign, level, exp) \
                    VALUES ("%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s");' \
                      % (
                          mid, name, sex, face, spacesta,
                          birthday, place,following, fans, playnum, sign, level, exp
                      )
                print(sql)
                cur.execute(sql)
                conn.commit()
            except Exception:
                print("MySQL Error")
        else:
            print("Error: " + url)
    except ValueError:
        pass


class MyThread(threading.Thread) :

    def __init__(self, func) :
        super(MyThread, self).__init__()  #调用父类的构造函数
        self.func = func  #传入线程函数逻辑

    def run(self) :
        self.func()

def worker() :
    # global q
    while not q.empty():
        url = q.get() #获得任务
        # print(q.get())
        get_data(url)
        time.sleep(1)
        q.task_done()




if __name__ == '__main__':
    # global q
    q = Queue()
    urls = []
    threads = []
    for i in range(1,500000):
        url = 'https://space.bilibili.com/' + str(i)
        q.put(url)
    # print(q.get())
    #用200个线程处理
    for i in range(1, 200):
        thread = MyThread(worker)
        thread.start()  # 线程开始处理任务
        threads.append(thread)
    for thread in threads:
        thread.join()








