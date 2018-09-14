import itchat
import re
from itchat.content import *

chat_dict = {
    1: '在的',
    2: '这么有空啊？',
    3: '在干嘛？',
    4: '有什么开心的事情要分享吗？',
    5: '这么搞笑的吗？',
    6: '那就没有办法了',
    7: '有事情忙，等下聊',
    8: '拜'
}

name_dict = {}
@itchat.msg_register([TEXT])
def text_reply(msg):
    """
    发送的文字回复
    :param msg:
    :return:
    """
    if len(msg['Text']):
        if msg['FromUserName'] in name_dict:
            name_dict[msg['FromUserName']] += 1
        else:
            name_dict[msg['FromUserName']] = 1
        if name_dict[msg['FromUserName']] == 5 and re.search('没', msg['Text']):
            name_dict[msg['FromUserName']] += 1
        itchat.send((chat_dict[name_dict[msg['FromUserName']]]), msg['FromUserName'])
        if name_dict[msg['FromUserName']] == 5:
            name_dict[msg['FromUserName']] += 1
        if name_dict[msg['FromUserName']] == 8:
            name_dict[msg['FromUserName']] = 0



@itchat.msg_register([PICTURE, RECORDING, VIDEO])
def other_reply(msg):
    """
    发送的其它东西的回复， 如对方发送的是图片，音频，视频
    :param msg:
    :return:
    """
    itchat.send(('流量伤不起啊，大哥'), msg['FromUserName'])


@itchat.msg_register([SHARING])
def shart_reply(msg):
    """
    发送的分享的东西的回复
    :param msg:
    :return:
    """
    itchat.send(('谢谢,挺不错的'), msg['FromUserName'])


if __name__ == '__main__':
    itchat.auto_login(hotReload=True)
    itchat.run()
