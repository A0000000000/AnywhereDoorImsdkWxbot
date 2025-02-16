import json
import os
import base64
import time
import requests
import constant
from threading import Thread

GEWE_CONFIG = {
    constant.CONFIG_APP_ID: constant.EMPTY_STR,
    constant.CONFIG_GEWE_TOKEN: constant.EMPTY_STR,
    constant.CONFIG_GEWE_API: constant.EMPTY_STR,
    constant.CONFIG_TARGET_WECHAT_ID: constant.EMPTY_STR,
    constant.PARAMS_LOG_CONTEXT: None
}


def init(log_ctx):
    GEWE_CONFIG[constant.PARAMS_LOG_CONTEXT] = log_ctx
    Thread(target=init_inner,
           kwargs={},
           daemon=True).start()


def init_inner():
    collect = os.getenv(constant.ENV_COLLECT)
    gewe_api = os.getenv(constant.ENV_API_GEWE)
    admin_wxid = os.getenv(constant.ENV_ADMIN_WXID)
    app_id = constant.EMPTY_STR
    if os.path.exists(constant.SESSION_CONFIG_FILE):
        with open(constant.SESSION_CONFIG_FILE, 'r') as f:
            config = json.load(f)
            if constant.CONFIG_APP_ID in config:
                app_id = config[constant.CONFIG_APP_ID]
    res = requests.post(gewe_api + '/v2/api/tools/getTokenId', headers={
        constant.HEADER_CONTENT_TYPE: constant.APPLICATION_JSON
    }, timeout=60).json()
    if res[constant.RET] != 200:
        return
    gewe_token = res[constant.PARAMS_DATA]
    if not check_online_status(app_id, gewe_api, gewe_token):
        while True:
            app_id, result = request_login(app_id, gewe_api, gewe_token)
            if result:
                break
    resp = requests.post(gewe_api + '/v2/api/tools/setCallback', json={
        constant.PARAMS_TOKEN: gewe_token,
        constant.GEWE_CALLBACK_URL: collect + constant.FLASK_URL_COLLECT
    }, headers={
        constant.HEADER_CONTENT_TYPE: constant.APPLICATION_JSON,
        constant.HEADER_TOKEN: gewe_token
    }, timeout=60).json()
    if resp[constant.RET] != 200:
        return
    GEWE_CONFIG[constant.CONFIG_APP_ID] = app_id
    GEWE_CONFIG[constant.CONFIG_GEWE_TOKEN] = gewe_token
    GEWE_CONFIG[constant.CONFIG_GEWE_API] = gewe_api
    resp = requests.post(gewe_api + '/v2/api/contacts/search', json={
        constant.GEWE_PARAMS_APP_ID: app_id,
        constant.GEWE_CONTACTS_INFO: admin_wxid
    }, headers={
        constant.HEADER_CONTENT_TYPE: constant.APPLICATION_JSON,
        constant.HEADER_TOKEN: gewe_token
    }, timeout=60).json()
    if resp[constant.RET] != 200 or 'v3' not in resp[constant.PARAMS_DATA]:
        return
    GEWE_CONFIG[constant.CONFIG_TARGET_WECHAT_ID] = resp[constant.PARAMS_DATA]['v3']


def check_online_status(app_id, gewe_api, gewe_token):
    if app_id != constant.EMPTY_STR:
        resp = requests.post(gewe_api + '/v2/api/login/checkOnline', json={
            constant.GEWE_PARAMS_APP_ID: app_id,
        }, headers={
            constant.HEADER_CONTENT_TYPE: constant.APPLICATION_JSON,
            constant.HEADER_TOKEN: gewe_token
        }, timeout=60).json()
        if resp[constant.RET] != 200:
            return False
        if resp[constant.PARAMS_DATA]:
            return True
    return False


def request_login(app_id, gewe_api, gewe_token):
    resp = requests.post(gewe_api + '/v2/api/login/getLoginQrCode', json={
        constant.GEWE_PARAMS_APP_ID: app_id,
    }, headers={
        constant.HEADER_CONTENT_TYPE: constant.APPLICATION_JSON,
        constant.HEADER_TOKEN: gewe_token
    }, timeout=60).json()
    if resp[constant.RET] == 500 and resp[constant.PARAMS_DATA][constant.PARAMS_CODE] == '-1':
        resp = requests.post(gewe_api + '/v2/api/login/getLoginQrCode', json={
            constant.GEWE_PARAMS_APP_ID: constant.EMPTY_STR,
        }, headers={
            constant.HEADER_CONTENT_TYPE: constant.APPLICATION_JSON,
            constant.HEADER_TOKEN: gewe_token
        }, timeout=60).json()
    if resp[constant.RET] != 200:
        return app_id, False
    app_id_new = resp[constant.PARAMS_DATA][constant.GEWE_PARAMS_APP_ID]
    uuid = resp[constant.PARAMS_DATA][constant.GEWE_UUID]
    qr_code_base64 = resp[constant.PARAMS_DATA][constant.GEWE_QR_IMAGE_BASE64]
    qr_image = base64.b64decode(qr_code_base64.split(',')[1])
    with open(constant.SESSION_LOGIN_FILE, 'wb') as f:
        f.write(qr_image)
    if app_id != app_id_new:
        app_id = app_id_new
        with open(constant.SESSION_CONFIG_FILE, 'w') as f:
            f.write(json.dumps({
                constant.CONFIG_APP_ID: app_id,
            }))
    while True:
        resp = requests.post(gewe_api + '/v2/api/login/checkLogin', json={
            constant.GEWE_PARAMS_APP_ID: app_id,
            constant.GEWE_UUID: uuid
        }, headers={
            constant.HEADER_CONTENT_TYPE: constant.APPLICATION_JSON,
            constant.HEADER_TOKEN: gewe_token
        }, timeout=60).json()
        if resp[constant.RET] != 200:
            return app_id, False
        if resp[constant.PARAMS_DATA][constant.GEWE_EXPIRED_TIME] is None:
            return app_id, False
        if resp[constant.PARAMS_DATA][constant.GEWE_STATUS] == 2:
            os.remove(constant.SESSION_LOGIN_FILE)
            break
        time.sleep(5)
    return app_id, True


def send_msg_to_admin(text):
    if (GEWE_CONFIG[constant.CONFIG_APP_ID] != constant.EMPTY_STR
            and GEWE_CONFIG[constant.CONFIG_GEWE_TOKEN] != constant.EMPTY_STR
            and GEWE_CONFIG[constant.CONFIG_GEWE_API] != constant.EMPTY_STR
            and GEWE_CONFIG[constant.CONFIG_TARGET_WECHAT_ID] != constant.EMPTY_STR):
        requests.post(GEWE_CONFIG[constant.CONFIG_GEWE_API] + '/v2/api/message/postText', json={
            constant.GEWE_PARAMS_APP_ID: GEWE_CONFIG[constant.CONFIG_APP_ID],
            constant.GEWE_TO_WXID: GEWE_CONFIG[constant.CONFIG_TARGET_WECHAT_ID],
            constant.GEWE_CONTENT: text
        }, headers={
            constant.HEADER_CONTENT_TYPE: constant.APPLICATION_JSON,
            constant.HEADER_TOKEN: GEWE_CONFIG[constant.CONFIG_GEWE_TOKEN]
        }, timeout=60).json()
