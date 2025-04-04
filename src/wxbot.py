import os
import requests
import constant

from threading import Thread


gewe_env = {
    constant.ENV_COLLECT: constant.EMPTY_STR,
    constant.ENV_API_GEWE: constant.EMPTY_STR,
    constant.ENV_ADMIN_WXID: constant.EMPTY_STR,
    constant.ENV_APP_ID: constant.EMPTY_STR
}


gewe_config = {
    constant.CONFIG_GEWE_TOKEN: constant.EMPTY_STR,
    constant.CONFIG_TARGET_WECHAT_ID: constant.EMPTY_STR,
    constant.PARAMS_LOG_CONTEXT: None
}


def init(log_ctx):
    gewe_config[constant.PARAMS_LOG_CONTEXT] = log_ctx
    Thread(target=init_inner,
           kwargs={},
           daemon=True).start()


def init_inner():
    gewe_env[constant.ENV_COLLECT] = os.getenv(constant.ENV_COLLECT)
    gewe_env[constant.ENV_API_GEWE] = os.getenv(constant.ENV_API_GEWE)
    gewe_env[constant.ENV_ADMIN_WXID] = os.getenv(constant.ENV_ADMIN_WXID)
    gewe_env[constant.ENV_APP_ID] = os.getenv(constant.ENV_APP_ID)
    get_basic_params()


def check_online_status():
    if gewe_env[constant.ENV_APP_ID] != constant.EMPTY_STR:
        resp = requests.post(gewe_env[constant.ENV_API_GEWE] + '/v2/api/login/checkOnline', json={
            constant.GEWE_PARAMS_APP_ID: gewe_env[constant.ENV_APP_ID],
        }, headers={
            constant.HEADER_CONTENT_TYPE: constant.APPLICATION_JSON,
            constant.HEADER_TOKEN: gewe_config[constant.CONFIG_GEWE_TOKEN]
        }, timeout=60).json()
        if resp[constant.RET] != 200:
            return False
        if resp[constant.PARAMS_DATA]:
            return True
    return False


def get_basic_params():
    res = requests.post(gewe_env[constant.ENV_API_GEWE] + '/v2/api/tools/getTokenId', headers={
        constant.HEADER_CONTENT_TYPE: constant.APPLICATION_JSON
    }, timeout=60).json()
    if res[constant.RET] != 200:
        return
    gewe_config[constant.CONFIG_GEWE_TOKEN] = res[constant.PARAMS_DATA]
    resp = requests.post(gewe_env[constant.ENV_API_GEWE] + '/v2/api/tools/setCallback', json={
        constant.PARAMS_TOKEN: gewe_config[constant.CONFIG_GEWE_TOKEN],
        constant.GEWE_CALLBACK_URL: gewe_env[constant.ENV_COLLECT] + constant.FLASK_URL_COLLECT
    }, headers={
        constant.HEADER_CONTENT_TYPE: constant.APPLICATION_JSON,
        constant.HEADER_TOKEN: gewe_config[constant.CONFIG_GEWE_TOKEN]
    }, timeout=60).json()
    if resp[constant.RET] != 200:
        return
    if check_online_status():
        resp = requests.post(gewe_env[constant.ENV_API_GEWE] + '/v2/api/contacts/search', json={
            constant.GEWE_PARAMS_APP_ID: gewe_env[constant.ENV_APP_ID],
            constant.GEWE_CONTACTS_INFO: gewe_env[constant.ENV_ADMIN_WXID]
        }, headers={
            constant.HEADER_CONTENT_TYPE: constant.APPLICATION_JSON,
            constant.HEADER_TOKEN: gewe_config[constant.CONFIG_GEWE_TOKEN]
        }, timeout=60).json()
        if resp[constant.RET] != 200 or 'v3' not in resp[constant.PARAMS_DATA]:
            return
        gewe_config[constant.CONFIG_TARGET_WECHAT_ID] = resp[constant.PARAMS_DATA]['v3']


def send_msg_to_admin(text):
    if (gewe_config[constant.CONFIG_TARGET_WECHAT_ID] == constant.EMPTY_STR
            or gewe_config[constant.CONFIG_GEWE_TOKEN] == constant.EMPTY_STR
            or not check_online_status()):
        get_basic_params()
    if (gewe_config[constant.CONFIG_TARGET_WECHAT_ID] == constant.EMPTY_STR
            or gewe_config[constant.CONFIG_GEWE_TOKEN] == constant.EMPTY_STR
            or not check_online_status()):
        return
    if (gewe_env[constant.ENV_APP_ID] != constant.EMPTY_STR
            and gewe_config[constant.CONFIG_GEWE_TOKEN] != constant.EMPTY_STR
            and gewe_env[constant.ENV_API_GEWE] != constant.EMPTY_STR
            and gewe_config[constant.CONFIG_TARGET_WECHAT_ID] != constant.EMPTY_STR):
        requests.post(gewe_env[constant.ENV_API_GEWE] + '/v2/api/message/postText', json={
            constant.GEWE_PARAMS_APP_ID: gewe_env[constant.ENV_APP_ID],
            constant.GEWE_TO_WXID: gewe_config[constant.CONFIG_TARGET_WECHAT_ID],
            constant.GEWE_CONTENT: text
        }, headers={
            constant.HEADER_CONTENT_TYPE: constant.APPLICATION_JSON,
            constant.HEADER_TOKEN: gewe_config[constant.CONFIG_GEWE_TOKEN]
        }, timeout=60).json()
