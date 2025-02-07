import json
import os
import signal
import base64
import time
import requests
import constant
from threading import Thread


GEWE_CONFIG = {
    constant.CONFIG_APP_ID: '',
    constant.CONFIG_GEWE_TOKEN: '',
    constant.CONFIG_GEWE_API: '',
    constant.CONFIG_TARGET_WECHAT_ID: ''
}


def init():
    Thread(target=init_inner,
           kwargs={},
           daemon=True).start()


def init_inner():
    collect = os.getenv(constant.ENV_COLLECT)
    gewe_api = os.getenv(constant.ENV_API_GEWE)
    admin_wxid = os.getenv(constant.ENV_ADMIN_WXID)
    app_id = ''
    if os.path.exists(constant.SESSION_CONFIG_FILE):
        with open(constant.SESSION_CONFIG_FILE, 'r') as f:
            config = json.load(f)
            if 'app_id' in config:
                app_id = config['app_id']
    print('app_id = %s' % app_id)
    res = requests.post(gewe_api + '/v2/api/tools/getTokenId', headers={
        'Content-Type': 'application/json'
    }, timeout=60).json()

    if res['ret'] != 200:
        print('gewe token获取失败, 程序退出')
        os.kill(os.getpid(), signal.SIGTERM)
    gewe_token = res['data']
    need_login = True
    if app_id != '':
        resp = requests.post(gewe_api + '/v2/api/login/checkOnline', json={
            'appId': app_id,
        }, headers={
            'Content-Type': 'application/json',
            'X-GEWE-TOKEN': gewe_token
        }, timeout=60).json()
        if resp['ret'] != 200:
            print('gewe 检查登录状态失败, 程序退出')
            os.kill(os.getpid(), signal.SIGTERM)
        if resp['data']:
            need_login = False
    if need_login:
        resp = requests.post(gewe_api + '/v2/api/login/getLoginQrCode', json={
            'appId': app_id,
        }, headers={
            'Content-Type': 'application/json',
            'X-GEWE-TOKEN': gewe_token
        }, timeout=60).json()
        if resp['ret'] != 200:
            print('gewe 获取登录信息失败, 程序退出')
            os.kill(os.getpid(), signal.SIGTERM)
        app_id_new = resp['data']['appId']
        uuid = resp['data']['uuid']
        qr_code_base64 = resp['data']['qrImgBase64']
        qr_image = base64.b64decode(qr_code_base64.split(',')[1])
        with open(constant.SESSION_LOGIN_FILE, 'wb') as f:
            f.write(qr_image)
            print('app_id = %s, app_id_new = %s' % (app_id, app_id_new))
        if app_id != app_id_new:
            app_id = app_id_new
            with open(constant.SESSION_CONFIG_FILE, 'w') as f:
                f.write(json.dumps({
                    'appId': app_id,
                }))
        while True:
            resp = requests.post(gewe_api + '/v2/api/login/checkLogin', json={
                'appId': app_id,
                'uuid': uuid
            }, headers={
                'Content-Type': 'application/json',
                'X-GEWE-TOKEN': gewe_token
            }, timeout=60).json()
            if resp['ret'] != 200:
                print('gewe 检出登录状态失败, 程序退出')
                os.kill(os.getpid(), signal.SIGTERM)
            if resp['data']['status'] == 2:
                os.remove(constant.SESSION_LOGIN_FILE)
                break
            print('当前状态: %d' % (resp['data']['status']))
            time.sleep(5)
    # 到此为止, 登录成功，可以设置参数及回调消息了
    resp = requests.post(gewe_api + '/v2/api/tools/setCallback', json={
        'token': gewe_token,
        'callbackUrl': collect + constant.FLASK_URL_COLLECT
    }, headers={
        'Content-Type': 'application/json',
        'X-GEWE-TOKEN': gewe_token
    }, timeout=60).json()

    if resp['ret'] != 200:
        print('回调消息地址设置失败.')
        os.kill(os.getpid(), signal.SIGTERM)
    # 保存上下文(gewe_token、app_id)
    GEWE_CONFIG[constant.CONFIG_APP_ID] = app_id
    GEWE_CONFIG[constant.CONFIG_GEWE_TOKEN] = gewe_token
    GEWE_CONFIG[constant.CONFIG_GEWE_API] = gewe_api
    resp = requests.post(gewe_api + '/v2/api/contacts/search', json={
        'appId': app_id,
        'contactsInfo': admin_wxid
    }, headers={
        'Content-Type': 'application/json',
        'X-GEWE-TOKEN': gewe_token
    }, timeout=60).json()
    if resp['ret'] != 200 or 'v3' not in resp['data']:
        print('管理员账号不存在.')
        os.kill(os.getpid(), signal.SIGTERM)
    GEWE_CONFIG[constant.CONFIG_TARGET_WECHAT_ID] = resp['data']['v3']


def send_msg_to_admin(text):
    if (GEWE_CONFIG[constant.CONFIG_APP_ID] != ''
            and GEWE_CONFIG[constant.CONFIG_GEWE_TOKEN] != ''
            and GEWE_CONFIG[constant.CONFIG_GEWE_API] != ''
            and GEWE_CONFIG[constant.CONFIG_TARGET_WECHAT_ID] != ''):
        resp = requests.post(GEWE_CONFIG['gewe_api'] + '/v2/api/message/postText', json={
            'appId': GEWE_CONFIG[constant.CONFIG_APP_ID],
            'toWxid': GEWE_CONFIG[constant.CONFIG_TARGET_WECHAT_ID],
            'content': text
        }, headers={
            'Content-Type': 'application/json',
            'X-GEWE-TOKEN': GEWE_CONFIG[constant.CONFIG_GEWE_TOKEN]
        }, timeout=60).json()
        print(resp)
    else:
        print('微信未登录.')

