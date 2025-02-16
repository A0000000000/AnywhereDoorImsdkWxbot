import os
import time
import requests
import constant


class LogContext:
    def __init__(self, log_url, username, token, imsdk_name):
        self.log_url = log_url
        self.username = username
        self.token = token
        self.imsdk_name = imsdk_name

    def d(self, tag, msg):
        self.__save_log(tag, msg, constant.LOG_LEVEL_DEBUG)

    def i(self, tag, msg):
        self.__save_log(tag, msg, constant.LOG_LEVEL_INFO)

    def w(self, tag, msg):
        self.__save_log(tag, msg, constant.LOG_LEVEL_WARN)

    def e(self, tag, msg):
        self.__save_log(tag, msg, constant.LOG_LEVEL_ERROR)

    def __save_log(self, tag, msg, level):
        requests.post(self.log_url, json={
            constant.PARAMS_NAME: self.imsdk_name,
            constant.PARAMS_TIMESTAMP: int(round(time.time() * 1000)),
            constant.PARAMS_LEVEL: level,
            constant.PARAMS_TAG: tag,
            constant.PARAMS_LOG: msg
        }, headers={
            constant.PARAMS_TOKEN: self.token,
            constant.PARAMS_USERNAME: self.username,
        })


def create_log_ctx() -> LogContext:
    host = os.getenv(constant.ENV_HOST)
    port = os.getenv(constant.ENV_PORT)
    prefix = os.getenv(constant.ENV_PREFIX)
    username = os.getenv(constant.ENV_USERNAME)
    if prefix is None:
        prefix = constant.EMPTY_STR
    token = os.getenv(constant.ENV_TOKEN)
    imsdk_name = os.getenv(constant.ENV_IMSDK_NAME)
    return LogContext(constant.TEMPLATE_LOG_URL % (host, port, prefix), username, token, imsdk_name)

