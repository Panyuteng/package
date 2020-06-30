import requests
from bs4 import BeautifulSoup


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'
}


def get_detail_data(soup):
    """
    获取详细数据
    :param soup:
    :return:
    """
    tr_lists = soup.find_all('tr', {'class': 'nslist'})
    xy_main_url = 'http://www.xyjsgc.com/website/main/'
    for tr in tr_lists:
        title = tr.find('a')['title']
        detail_url = '{}{}'.format(xy_main_url, tr.find('a')['href'])
        print(title)


def xy_business_circles(datas={}):
    """
    抓取咸阳的招标信息
    :param datas:请求的参数
    :return:
    """
    url = 'http://www.xyjsgc.com/website/main/Channel.aspx?fcol=122002'
    # r = requests.get(url, headers=headers) if datas else requests.post(url, datas=datas, headers=headers)
    r = requests.post(url, data=datas, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    get_detail_data(soup)
    if '下一页' in r.text:
        datas ={
            '__EVENTTARGET': 'Pager1$lb_Next',
            '__EVENTARGUMENT': '',
            '__LASTFOCUS': '',
            '__VIEWSTATEGENERATOR': '1B79AC81',
            'cl1$KeyWord1': '',
            'Pager1$NavPage': ''
        }
        datas['__EVENTVALIDATION'] = soup.find('input', {'name': '__EVENTVALIDATION'})['value']
        datas['__VIEWSTATE'] = soup.find('input', {'name': '__VIEWSTATE'})['value']
        print(datas)
        xy_business_circles(datas)


if __name__ == '__main__':
    data_list = []
    xy_business_circles()
