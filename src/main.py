import json
import os
import time
import requests
import constant
import log
import server
import wxbot

from threading import Thread


def register():
    host = os.getenv(constant.ENV_HOST)
    port = os.getenv(constant.ENV_PORT)
    prefix = os.getenv(constant.ENV_PREFIX)
    if prefix is None:
        prefix = constant.EMPTY_STR
    token = os.getenv(constant.ENV_TOKEN)
    username = os.getenv(constant.ENV_USERNAME)
    imsdk_name = os.getenv(constant.ENV_IMSDK_NAME)
    self_host = os.getenv(constant.ENV_SELF_HOST)
    self_port = constant.FLASK_PORT
    self_port_env = os.getenv(constant.ENV_SELF_PORT)
    if self_port_env is not None:
        self_port = int(self_port_env)
    self_prefix = os.getenv(constant.ENV_SELF_PREFIX)
    if self_prefix is None:
        self_prefix = constant.EMPTY_STR
    register_url = constant.TEMPLATE_REGISTER_URL % (host, port, prefix)
    while True:
        try:
            res = requests.post(register_url, json={
                constant.PARAMS_NAME: imsdk_name,
                constant.PARAMS_HOST: self_host,
                constant.PARAMS_PORT: self_port,
                constant.PARAMS_PREFIX: self_prefix
            }, headers={
                constant.PARAMS_TOKEN: token,
                constant.PARAMS_USERNAME: username
            })
            resp = json.loads(res.text)
            if resp[constant.PARAMS_CODE] == -10:
                time.sleep(10)
            else:
                break
        except Exception as e:
            time.sleep(10)


def main():
    Thread(target=register, daemon=True).start()
    log_ctx = log.create_log_ctx()
    wxbot.init(log_ctx)
    server.init_http_server(log_ctx,
                            wxbot.send_msg_to_admin,
                            wxbot.gewe_config)


if __name__ == '__main__':
    main()
