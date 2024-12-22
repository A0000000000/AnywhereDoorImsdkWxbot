import os

import itchat
from itchat.content import *

import constant


def empty_send_method(target, data):
    send_msg_to_admin(constant.ERROR_INIT)


wx_config = {
    constant.CONFIG_ADMIN_NICKNAME: '',
    constant.CONFIG_SEND_METHOD: empty_send_method
}


def init(fn_send_request):
    admin_nickname = os.getenv(constant.ENV_ADMIN_NICKNAME)
    if admin_nickname is None:
        admin_nickname = constant.DEFAULT_ADMIN_NICKNAME
    wx_config[constant.CONFIG_ADMIN_NICKNAME] = admin_nickname
    itchat.auto_login(hotReload=True,
                      enableCmdQR=True,
                      picDir=constant.LOGIN_PIC_DIR,
                      statusStorageDir=constant.LOGIN_STATUS_STORAGE_DIR)
    wx_config[constant.CONFIG_SEND_METHOD] = fn_send_request
    itchat.run()


@itchat.msg_register([TEXT])
def private_chat_text(msg):
    name = msg.user.nickName
    if name != wx_config[constant.CONFIG_ADMIN_NICKNAME]:
        # 非管理员用户, 忽略信息
        return
    text = msg.text
    index = 0
    while index < len(text):
        if text[index] == ' ':
            break
        index = index + 1
    if index == 0 or index == len(text):
        send_msg_to_admin(constant.ERROR_CMD_FORMAT)
        return
    wx_config[constant.CONFIG_SEND_METHOD](text[:index], text[index + 1:])


def send_msg_to_admin(text):
    result = itchat.search_friends(nickName=wx_config[constant.CONFIG_ADMIN_NICKNAME])
    if result is not None and len(result) > 0:
        user = result[0]
        user.send(text)
