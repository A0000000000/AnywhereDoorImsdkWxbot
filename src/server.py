import json
import os
import requests
import constant

from flask import Flask
from flask import request


server_config = {
    constant.CONFIG_URL: constant.EMPTY_STR,
    constant.CONFIG_TOKEN: constant.EMPTY_STR,
    constant.CONFIG_IMSDK_NAME: constant.EMPTY_STR,
    constant.CONFIG_USERNAME: constant.EMPTY_STR,
    constant.CONFIG_SEND_METHOD: None
}


def init_http_server(log_ctx, fn_send_msg_to_admin, gewe_config):
    host = os.getenv(constant.ENV_HOST)
    port = os.getenv(constant.ENV_PORT)
    prefix = os.getenv(constant.ENV_PREFIX)
    if prefix is None:
        prefix = constant.EMPTY_STR
    username = os.getenv(constant.ENV_USERNAME)
    url = constant.TEMPLATE_URL % (host, port, prefix)
    token = os.getenv(constant.ENV_TOKEN)
    imsdk_name = os.getenv(constant.ENV_IMSDK_NAME)

    server_config[constant.CONFIG_URL] = url
    server_config[constant.CONFIG_TOKEN] = token
    server_config[constant.CONFIG_IMSDK_NAME] = imsdk_name
    server_config[constant.CONFIG_USERNAME] = username
    server_config[constant.CONFIG_SEND_METHOD] = fn_send_msg_to_admin

    app = Flask(constant.FLASK_APP_NAME)

    @app.post(constant.FLASK_URL_IMSDK)
    def on_request():
        _token = request.headers.get(constant.PARAMS_TOKEN)
        name = request.json.get(constant.PARAMS_NAME)
        target = request.json.get(constant.PARAMS_TARGET)
        data = request.json.get(constant.PARAMS_DATA)
        if _token != server_config[constant.CONFIG_TOKEN]:
            resp = {
                constant.PARAMS_CODE: constant.ERROR_CODE_INVALID_TOKEN,
                constant.PARAMS_MESSAGE: constant.ERROR_MESSAGE_INVALID_TOKEN
            }
            return json.dumps(resp)
        if target != server_config[constant.CONFIG_IMSDK_NAME]:
            resp = {
                constant.PARAMS_CODE: constant.ERROR_CODE_INVALID_TARGET,
                constant.PARAMS_MESSAGE: constant.ERROR_MESSAGE_INVALID_TARGET
            }
            return json.dumps(resp)
        fn_send_msg_to_admin(constant.FROM
                             + constant.WHITE_SPACE
                             + name
                             + constant.COLON
                             + constant.NEWLINE
                             + data)
        resp = {
            constant.PARAMS_CODE: constant.ERROR_CODE_SUCCESS,
            constant.PARAMS_MESSAGE: constant.ERROR_MESSAGE_SUCCESS
        }
        return json.dumps(resp)

    @app.post(constant.FLASK_URL_COLLECT)
    def on_rev_message():
        data = request.json
        if 'TypeName' in data and data['TypeName'] == 'AddMsg' and data['Data']['MsgType'] == 1:
            text = data['Data']['Content']['string']
            from_user = data['Data']['FromUserName']['string']
            if from_user == gewe_config[constant.CONFIG_TARGET_WECHAT_ID]:
                index = 0
                while index < len(text):
                    if text[index] == constant.WHITE_SPACE:
                        break
                    index = index + 1
                if index == 0 or index == len(text):
                    fn_send_msg_to_admin(constant.ERROR_CMD_FORMAT + constant.WHITE_SPACE + text)
                else:
                    send_request(text[:index], text[index + 1:])
        return constant.EMPTY_STR

    app.run(constant.FLASK_HOST, constant.FLASK_PORT)


def send_request(target, data):
    res = requests.post(server_config[constant.CONFIG_URL], json={
        constant.PARAMS_TARGET: target,
        constant.PARAMS_NAME: server_config[constant.CONFIG_IMSDK_NAME],
        constant.PARAMS_DATA: data
    }, headers={
        constant.PARAMS_TOKEN: server_config[constant.CONFIG_TOKEN],
        constant.PARAMS_USERNAME: server_config[constant.CONFIG_USERNAME]
    })
    resp = json.loads(res.text)
    if resp[constant.PARAMS_CODE] != constant.ERROR_CODE_SUCCESS \
            and server_config[constant.CONFIG_SEND_METHOD] is not None:
        server_config[constant.CONFIG_SEND_METHOD](resp[constant.PARAMS_MESSAGE])
