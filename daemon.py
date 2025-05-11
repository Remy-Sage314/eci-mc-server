# -*- coding: utf-8 -*-
import time
import subprocess
import os
import threading
import shlex

from flask import Flask, Response
from alibabacloud_eci20180808.models import DeleteContainerGroupRequest

from utils import *
from dingtalk import *

app = Flask(__name__)


@app.route("/send/<string:message>")
def send(message):
    """发送钉钉消息"""
    status = 200
    if EnableDingtalk:
        if EnableDingtalkEnterprise:
            status = send_dingtalk_message_enterprise(message)
        else:
            status = send_dingtalk_message(message)
    return Response(status=status)


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
    client = get_ali_client('eci')
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
        setup_dns()
        t = threading.Thread(target=wait)
        app.run(port=25585, host="0.0.0.0", debug=False)  # debug必须为False
