import os

import itchat
from itchat.content import *

wx_config = {
    'admin_nickname': ''
}


def init(fn_send_request):
    admin_nickname = os.getenv('ADMIN_NICKNAME')
    if admin_nickname is None:
        admin_nickname = '猫眼螺'
    wx_config['admin_nickname'] = admin_nickname
    itchat.auto_login(hotReload=True, enableCmdQR=True, picDir='login.png', statusStorageDir='itchat.pkl')
    itchat.fn_send_request = fn_send_request
    itchat.run()


@itchat.msg_register([TEXT])
def private_chat_text(msg):
    name = msg.user.nickName
    if name != wx_config['admin_nickname']:
        print('非管理员用户, 忽略信息...')
        return
    text = msg.text
    index = 0
    while index < len(text):
        if text[index] == ' ':
            break
        index = index + 1
    if index == 0 or index == len(text):
        print("wrong cmd: ", text)
        return
    itchat.fn_send_request(text[:index], text[index+1:])


def send_msg_to_admin(text):
    result = itchat.search_friends(nickName=wx_config['admin_nickname'])
    if result is not None and len(result) > 0:
        user = result[0]
        user.send(text)