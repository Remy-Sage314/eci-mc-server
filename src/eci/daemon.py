# -*- coding: utf-8 -*-
import shlex
import socket
import subprocess
import threading
import time
from datetime import datetime, timezone
from os import environ

import rcon
from alibabacloud_eci20180808.models import DeleteContainerGroupRequest, DescribeContainerGroupsRequest
from flask import Flask, Response

from utils import *
from message import SendMessageHandler
from config import save_config

app = Flask(__name__)

# 判断端口占用来判断是否已停止
def is_stopped():
    return True if socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect_ex(('localhost', 25565)) != 0 else False


def stop_and_wait():
    """关闭MC服务器并删除容器组，此函数只能执行一次"""
    rcon_client.run("stop")
    rcon_client.close()

    n = 0
    while True:
        if not is_stopped():
            time.sleep(5)
            n += 1
        else:
            logger.info("MC服务器进程已退出喵～")
            delete_container_group()
            return
        if n % 8 == 0 and n <= 16:
            logger.warning(f"MC服务器进程在{5 * n}秒内仍未退出")


@app.route('/stop')
def stop():
    if not thread_stop.is_alive():  # 保证只执行一次
        thread_stop.start()
        return Response('stopping', 200)
    return Response('stopping', status=400)


@app.route('/delete')
def delete_container_group():
    delete_request = DeleteContainerGroupRequest(region_id=Conf.RegionId, container_group_id=instance_id)
    return str(eci_client.delete_container_group(delete_request).status_code)


@app.route('/check')
def check():
    port_status = '，25565端口未占用' if is_stopped() else '，25565端口已占用'
    if mc_process.poll() is None:
        return '进程运行中' + port_status
    return '进程已退出：' + str(mc_process.poll()) + port_status


@app.route('/change_auto_stop')
def change_auto_stop():
    global is_auto_stop
    is_auto_stop = not is_auto_stop
    if is_auto_stop:
        logger.info('已开启自动停止喵～')
        return '已开启自动停止'
    else:
        logger.info('已关闭自动停止喵～')
        return '已关闭自动停止'


def query_eci_status():
    describe_request = DescribeContainerGroupsRequest(region_id=Conf.RegionId, container_group_ids=f'["{instance_id}"]',
                                                      with_event=True)
    while True:
        response = eci_client.describe_container_groups(describe_request)
        logger.debug(response.body.to_map())
        for event in response.body.container_groups[0].events:
            dt = datetime.fromisoformat(event.first_timestamp)
            if (datetime.now(tz=timezone.utc) - dt).seconds > 60:  # 距现在超1分钟的事件跳过
                break

            if event.reason == 'SpotToBeReleased':
                logger.warning('ECI实例即将过期喵～:' + event.message)
                stop()
                return
            elif event.type == 'Warning':  # SpotToBeReleased 属于 Warning
                logger.debug(f'实例警告：{event.message}')
        time.sleep(30)


def auto_stop():
    n = 0
    while True:
        try:
            is_not_anyone_online = rcon_client.run('list').startswith('There are 0 of a max of')
            logger.debug(is_not_anyone_online)
        except (rcon.exceptions.EmptyResponse, BrokenPipeError):  # rcon崩了
            check_response = check()
            if 'stopped' in check_response:
                logger.warning(f'MC的java进程已退出，实例即将删除喵～')
                delete_container_group()
            else:
                logger.warning('rcon异常，自动停止失效，MC的java进程仍在运行，请手动介入喵～')
            return
        else:
            if is_not_anyone_online:
                n += 1
            else:
                n = 0

            if n >= 15:
                n = 0
                if is_auto_stop:
                    stop()
                    return
        time.sleep(20)


if __name__ == "__main__":
        send_message_handler = SendMessageHandler(config=Conf, level=logging.INFO)
        # send_message_handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s"))
        logger = logging.getLogger('send_messages')
        logger.addHandler(send_message_handler)
        logger.setLevel(logging.DEBUG)
        # logger.info('启动中喵～')

        v = Conf.DefaultVersion
        if environ['mc_version_to_run']:
            Conf.DefaultVersion = environ['mc_version_to_run']
            save_config(Conf)
            v = environ['mc_version_to_run']
        version = Conf.Versions[v]
        # 启动mc
        mc_process = subprocess.Popen(shlex.split(version.Command), cwd=version.WorkingDir, shell=False,
                             stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                             stdin=subprocess.DEVNULL)
        if Conf.IsCloud:
            # 更新dns
            ip = requests.get('http://100.100.100.200/latest/meta-data/eipv4').text
            logger.info(f'正在运行的版本： {v}\n实例IP： {ip}\n面板地址： http://{ip}:10086\n'
                        f'调整是否自动停止： http://{ip}:25585/change_auto_stop\n')
            update_dns(ip, logger)

            instance_id = requests.get('http://100.100.100.200/latest/meta-data/instance-id').text
            eci_client = get_ali_client('eci')
            threading.Thread(target=query_eci_status).start()

        is_auto_stop = True
        rcon_client = get_rcon_client()
        logger.info('MC已启动喵～')

        threading.Thread(target=auto_stop).start()
        thread_stop = threading.Thread(target=stop_and_wait)


        app.run(port=25585, host="0.0.0.0", debug=False)
