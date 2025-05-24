# -*- coding: utf-8 -*-
import logging
import time
import subprocess
import os
import threading
import shlex

from flask import Flask, request, Response
from alibabacloud_eci20180808.models import DeleteContainerGroupRequest

from utils import *
from dingtalk import send_dingtalk_message
from config import *

app = Flask(__name__)


def wait_close():
    time.sleep(5) # 等待looping释放rcon client
    rcon_client = get_rcon_client()
    rcon_client.run("stop")
    rcon_client.close()

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
    if request.args.get('close_plan') and not close_plan:
        return Response(status=403)

    if not t.is_alive():  # 保证只执行一次（判断方法不可靠）
        t.start()
        # send_dingtalk_message('正在关闭服务器')
        return "start closing"
    return 'closing'


@app.route('/delete')
def delete_container_group():
    instance_id = requests.get('http://100.100.100.200/latest/meta-data/instance-id').text
    delete_request = DeleteContainerGroupRequest(region_id=RegionId, container_group_id=instance_id)
    client = get_ali_client('eci')
    return str(client.delete_container_group(delete_request).status_code)


@app.route('/check')
def check_process():
    if p.poll() != 0 and p.poll() is not None:
        return 'unhealthy:' + str(p.poll()), 500
    return 'healthy:' + str(p.poll())


@app.route('/change_close_plan')
def change_close_plan():
    global close_plan
    close_plan = not close_plan
    m = f"已切换关闭计划为{str(close_plan)}"
    send_dingtalk_message(m)
    return m


if __name__ == "__main__":
    pid = os.fork()
    if pid == 0:
        # 启动mc
        p = subprocess.Popen(shlex.split(Command), cwd=WorkingDir, shell=False,
                             stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                             stdin=subprocess.DEVNULL)
        # 更新dns
        ip = requests.get('http://100.100.100.200/latest/meta-data/eipv4').text
        send_dingtalk_message(ip)
        setup_dns(ip)
        t = threading.Thread(target=wait_close)
        close_plan = True
        app.logger.setLevel(logging.DEBUG)
        app.run(port=25585, host="0.0.0.0", debug=False)  # debug必须为False
