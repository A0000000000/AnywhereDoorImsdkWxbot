import json
import os
import requests
from flask import Flask, send_from_directory
from flask import request
from threading import Thread

rpc_config = {
    'url': '',
    'token': '',
    'imsdk_name': '',
    'username': ''
}


def init_rpc_server(fn_send_msg_to_admin):
    host = os.getenv('HOST')
    port = os.getenv('PORT')
    prefix = os.getenv('PREFIX')
    username = os.getenv('USERNAME')
    if host is None:
        host = '192.168.25.7'
    if port is None:
        port = '8081'
    if prefix is None:
        prefix = ''
    if username is None:
        username = 'maoyanluo'
    url = 'http://' + host + ':' + port + prefix + '/imsdk'
    token = os.getenv('TOKEN')
    if token is None:
        token = '1998'
    imsdk_name = os.getenv('IMSDK_NAME')
    if imsdk_name is None:
        imsdk_name = 'wxbot'

    rpc_config['url'] = url
    rpc_config['token'] = token
    rpc_config['imsdk_name'] = imsdk_name
    rpc_config['username'] = username

    app = Flask('anywhere_door_imsdk_wxbot', static_folder='./')

    @app.post('/imsdk')
    def on_request():
        _token = request.headers.get('token')
        name = request.json.get('name')
        target = request.json.get('target')
        data = request.json.get('data')
        if _token != rpc_config['token']:
            resp = {'code': 500, 'message': 'token is invalid'}
            return json.dumps(resp)
        if target != rpc_config['imsdk_name']:
            resp = {'code': 500, 'message': 'target is not this'}
            return json.dumps(resp)
        fn_send_msg_to_admin(name + "\n" + data)
        resp = {'code': 200, 'message': 'success'}
        return json.dumps(resp)

    @app.get('/login')
    def login():
        return send_from_directory(app.static_folder, 'login.png')
    Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': 8080}, daemon=True).start()


def send_request(target, data):
    res = requests.post(rpc_config['url'], json={
        'target': target,
        'name': rpc_config['imsdk_name'],
        'data': data
    }, headers={
        'token': rpc_config['token'],
        'username': rpc_config['username']
    })
    print(res.text)


