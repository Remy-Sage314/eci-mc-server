# -*- coding: utf-8 -*-
import base64
import hashlib
import hmac
import json
import time
import urllib.parse
from logging import Handler

import requests


def get_dingtalk_sign(timestamp=None):
    if not timestamp:
        timestamp = str(round(time.time() * 1000))
    secret = DingtalkSecret
    secret_enc = secret.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    return base64.b64encode(hmac_code).decode('utf-8')


def send_dingtalk_message(message):
    if EnableDingtalk :
        timestamp = str(round(time.time() * 1000))
        sign = urllib.parse.quote_plus(get_dingtalk_sign())
        url = (RobotUrl +
               r"&timestamp=" + timestamp +
               r"&sign=" + sign)
        headers = {
            'Content-Type': 'application/json'
        }
        data = {
            'msgtype': 'text',
            'text': {
                'content': message
            }
        }
        return requests.post(url, headers=headers, data=json.dumps(data)).status_code
    return 200

EnableDingtalk, PushApiK, DingtalkSecret, RobotUrl = '', '', '', ''
class SendMessageHandler(Handler):
    def __init__(self, config, level=0):
        super().__init__(level)
        global EnableDingtalk, PushApiK, DingtalkSecret, RobotUrl
        EnableDingtalk, PushApiK, DingtalkSecret, RobotUrl = config.EnableDingtalk, config.PushApiK, config.DingtalkSecret, config.RobotUrl

    def emit(self, record):
        message = self.format(record)
        send_dingtalk_message(message)
        # just for Li
        requests.get('http://xdroid.net/api/message?c=mc&u=mc.lizihenmeng.cn',
                     params={'t':  message, 'k': PushApiK})
