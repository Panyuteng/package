import requests
from bs4 import BeautifulSoup
import pymysql
import hashlib
import redis
import time
import random

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
}


def get_mysql():
    # 定义获取nysql函数
    conn = pymysql.connect(host='127.0.0.1', user='root', passwd='123456', db='mysql', charset='utf8')
    cur = conn.cursor()  # 获取操作游标
    cur.execute('use flask_job')  # 使用kycmg这个数据库
    return (cur, conn)


def get_md5(st):
    """
    md5加密url，作为唯一hash
    :param st:
    :return:
    """
    hash_md5 = hashlib.md5()
    hash_md5.update(st.encode('utf-8'))
    hash = hash_md5.hexdigest()
    return hash




class QianchengJob:
    def __init__(self):
        self.cur, self.conn = get_mysql()   # 链接数据库
        self.id = 1
        self.r = redis.Redis(host='localhost', port=6379, decode_responses=True)    # 链接redis
        self.latetime = 3600 * 24 * 10

    def get_51job(self):
        """
        抓取51job 爬虫工作
        :return:
        """
        for i in range(1, 100):
            url = 'https://search.51job.com/list/030200%252C040000,000000,0000,00,9,99,%25E7%2588%25AC%25E8%2599%25AB,2,' \
                  + '{}'.format(
                i) + '.html?lang=c&stype=&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&com' \
                     'panysize=99&providesalary=99&lonlat=0%2C0&radius=-1&ord_field=0&confirmdate=9&fromType=&dibi' \
                     'aoid=0&address=&line=&specialarea=00&from=&welfare='
            print(url)
            session = requests.session()
            while True:
                try:
                    r = session.get(url, headers=headers, timeout=30)
                    break
                except:
                    time.sleep(random.randint(3,6))
                    continue
            r.encoding = r.apparent_encoding
            # print(r.text)
            soup = BeautifulSoup(r.text, 'html.parser')
            data_list = soup.find('div', {'class': 'dw_table'}).find_all('div', {'class': 'el'})[1:]
            print(len(data_list))
            job_list = []
            for data in data_list:
                all_data = []
                # print(data)
                lx = '爬虫'
                href = data.find('a')['href']
                job_name = data.find('a').text.replace(' ', '').replace('\r\n', '')
                company = data.find('span', {'class': 't2'}).text
                area = data.find('span', {'class': 't3'}).text
                sal = data.find('span', {'class': 't4'}).text
                pub_time = data.find('span', {'class': 't5'}).text
                hash_id = get_md5(href)
                if self.r.exists(hash_id):
                    continue
                all_data = [hash_id, href, job_name, company, area, sal, pub_time, lx]
                self.get_51job_detail(href, all_data)
                print(all_data)
                self.write_mysql(all_data)
            if len(data_list) < 45:
                break
        self.conn.commit()

    @staticmethod
    def get_51job_detail(href, all_data):
        """
        抓取详情页
        :return:
        """
        try:
            while True:
                try:
                    r = requests.get(href, headers=headers, timeout=30)
                    break
                except:
                    time.sleep(random.randint(3, 6))
                    continue
            soup = BeautifulSoup(r.text, 'html.parser')
            sm = soup.find('div', {'class': 'bmsg job_msg inbox'}).text.replace('\r\n', '').strip().replace('\n', '')
            msg = soup.find('p', {'class': 'msg ltype'}).text.replace('\r\n', '').strip()
            if '| ' in msg:
                try:
                    yaoqiu = ','.join(msg.split('| ')[1:-2])
                except:
                    yaoqiu = msg
            else:
                yaoqiu = msg
            fuli_list = soup.find('div', {'class': 't1'}).find_all('span')
            fuli = []
            for data in fuli_list:
                fuli.append(data.text.replace('\r\n', ''))
            fuli = ','.join(fuli)
            print(yaoqiu)
            print(fuli)
            print(sm)
            all_data.append(yaoqiu)
            all_data.append(fuli)
            all_data.append(sm)
        except:
            return 0

    def write_mysql(self, datalist):
        """
        存入mysql数据库
        :return:
        """
        try:
            sql = 'insert into job values("{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}")'\
                .format(self.id, datalist[0], datalist[1], datalist[2], datalist[3], datalist[4], datalist[5]
                        , datalist[6], datalist[7], datalist[8], datalist[9], datalist[10])
            print(sql)

            self.cur.execute(sql)
        except Exception as e:
            print(e)
            return 0
        self.r.set(datalist[0], datalist[1], ex=self.latetime)
        self.id += 1
        if self.id % 100 == 0:
            self.conn.commit()

    def get_max(self):
        # 获取数据库
        get_num_sql = 'select max(id) from job'
        self.cur.execute(get_num_sql)
        nums = self.cur.fetchall()
        if len(nums):
            for i in nums:
                self.id = i[0]
        else:
            self.id = 1


if __name__ == '__main__':
    qiancheng_job = QianchengJob()
    qiancheng_job.get_51job()
