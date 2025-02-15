# -*- coding: utf-8 -*-
import base64
import hashlib
import hmac
import json
import time
import subprocess
import os
import urllib
import threading
import shlex

import requests
from flask import Flask
from alibabacloud_eci20180808.models import DeleteContainerGroupRequest

from utils import *

app = Flask(__name__)


@app.route("/send/<string:message>")
def send_dingtalk_message(message):
    timestamp = str(round(time.time() * 1000))
    secret = DingtalkSecret
    secret_enc = secret.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
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
    return str(requests.post(url, headers=headers, data=json.dumps(data)).status_code)


def wait():
    n = 0
    while True:
        if p.poll() is None:
            time.sleep(5)
            n += 1
        else:
            send_dingtalk_message("MC服务器进程已退出")
            delete_container_group()
            return
        if n % 8 == 0 and n <= 16:
            send_dingtalk_message(f"MC服务器进程在{5 * n}秒内仍未退出")


@app.route('/stop_mc')
def stop():
    """关闭MC服务器并删除容器组"""
    global t
    if not t.is_alive():  # 保证只执行一次（判断方法不可靠）
        rcon_client = get_rcon_client()
        rcon_client.run("/stop")
        rcon_client.close()
        t.start()
        # send_dingtalk_message('正在关闭服务器')
        return "start closing"
    return 'closing'


@app.route('/delete')
def delete_container_group():
    instance_id = requests.get('http://100.100.100.200/latest/meta-data/instance-id').text
    request = DeleteContainerGroupRequest(region_id=RegionId, container_group_id=instance_id)
    client = get_eci_client()
    return str(client.delete_container_group(request).status_code)


@app.route('/check')
def check_process():
    if p.poll() != 0 and p.poll() is not None:
        return 'unhealthy:' + str(p.poll()), 500
    return 'healthy:' + str(p.poll())


if __name__ == "__main__":
    pid = os.fork()
    if pid == 0:
        # 启动mc
        p = subprocess.Popen(shlex.split(Command), cwd=McDir, shell=False,
                             stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                             stdin=subprocess.DEVNULL)
        # 更新dns
        if not Debug:
            ip = requests.get('http://100.100.100.200/latest/meta-data/eipv4').text
            requests.get(f'http://dynv6.com/api/update?hostname={Domain}&token={DYNV6Token}&ipv4={ip}')
        t = threading.Thread(target=wait)
        app.run(port=25585, host="0.0.0.0", debug=False)  # debug必须为False
