import pytesseract
from PIL import Image
import requests
import smtplib

import requests
from bs4 import BeautifulSoup
import time
import http.cookiejar as cookielib
import pymysql
import pytesseract
import re
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
from email.header import Header
from email import encoders

# 设置headers
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36(KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
    }
# 打开session
session = requests.Session()
# 保存cookies
session.cookies = cookielib.LWPCookieJar(filename='cookies')


# get_chaptcha()主要使用tesseract来通过subprocess来将验证码识别
def get_captcha():
    captcha_url ="http://210.38.102.131:86/reader/captcha.php"
    bin = session.get(captcha_url, headers=headers).content
    print(bin)
    with open("d:/LP/crawler/0.jpg", "wb")as file:
        file.write(bin)
    code = pytesseract.image_to_string(Image.open("d:/LP/crawler/0.jpg"))
    return code

#连接数据库
def get_mysql():
    conn = pymysql.connect(host = 'localhost', user = 'root', passwd = '123456', db = 'mysql', charset = 'utf8')
    cur = conn.cursor()    # 获取操作游标
    cur.execute('use book_list')   # 使用book这个数据库
    return (cur, conn)

def login():
    form_data = {
        'number': '',  #登陆学号
        'passwd': '',  #登陆密码
        'captcha': get_captcha(),
        'select': 'cert_no',
        'returnUrl': '',
        }
    session.post("http://210.38.102.131:86/reader/redr_verify.php",
                 data=form_data, headers=headers)
    info = session.get("http://210.38.102.131:86/reader/book_lst.php",
                       headers=headers).content.decode("UTF-8")
    # print(info)
    soup = BeautifulSoup(info, "html.parser")


    cur, conn = get_mysql()
    # sql = 'truncate table book_list'
    sql = 'select * from book_list;'
    cur.execute(sql)
    all_data = cur.fetchall()
    all_book = []
    for i in all_data:
        all_book.append(i[1])


    book_list = []  # 书本列表
    book_detail = []


    for book in soup.select('.whitetext'):
        pattern = re.compile(r'\s')
        content = re.sub(pattern, r'', book.get_text())  # 去除空白符
        # print(content)

        if content != '':
            book_detail.append(content)
            if len(book_detail) == 7:
                book_list.append(book_detail)
                if book_detail[0] not in all_book:
                    sql = 'insert into book_list(条形码, 书名和作者, 借阅日期, 应还日期, 续借量, 馆藏地) value(' + "\'" \
                          + book_detail[0] + "\'," + "\'" + book_detail[1] + "\'," + "\'" + book_detail[2] + "\'," + "\'" \
                          + book_detail[3] + "\'," + "\'" + book_detail[4] + "\'," + "\'" + book_detail[5] + "\'" + ');'

                try:
                    print(sql)
                    cur.execute(sql)

                except:
                    conn.rollback()
                print(book_detail)
                book_detail = []
        conn.commit()
    print(book_list)
    session.cookies.save()

def format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))

def send_message():
    from_addr = ''  # input('From: ')
    password = ''  # input('Password: ')
    to_addr = '815490913@qq.com'
    smtp_server = 'smtp.163.com'  # input('SMTP server: ')

    book_list = []
    day_list = []
    book = ' '
    day = ' '
    sql = 'select * from book_list;'
    cur, conn = get_mysql()
    cur.execute(sql)
    rows = cur.fetchall()
    # local_time = time.strftime('%Y-%m-%d', time.localtime())
    local_time = time.time()
    print(local_time)
    print(rows)
    for i in rows:
        a2time = time.mktime(time.strptime(i[4], '%Y-%m-%d'))
        print(a2time)
        day = (a2time - local_time) / 3600 / 24
        print(day)
        if day < 10 and day > -1:
            day_list.append(int(day))
            book_list.append(i[2])
    if len(book_list) > 0:
        text =''
        for i in range(len(book_list)):
            if day_list[i] < 0:
                text = '你的 %s 超期了，超了%s天，请尽快归还！' % (book_list[i], abs(day_list[i])) + '\n' + text

            text = '你的 %s 快超期了，距离到期时间为%s天，请尽快归还或者续借！' % (book_list[i], day_list[i]) + '\n' + text


        msg = MIMEText(text, 'plain', 'utf-8')
        msg['From'] = format_addr('腾 <%s>' % from_addr)
        msg['To'] = format_addr('管理员 <%s>' % to_addr)
        msg['Subject'] = Header('腾哥的问候', 'utf-8').encode()
        server = smtplib.SMTP(smtp_server, 25)
        server.set_debuglevel(1)
        server.login(from_addr, password)
        server.sendmail(from_addr, [to_addr], msg.as_string())
        server.quit()


if __name__ == '__main__':
        login()
        send_message()
