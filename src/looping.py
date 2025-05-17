# -*- coding: utf-8 -*-
import time
from datetime import datetime, timezone

from alibabacloud_eci20180808.models import DescribeContainerGroupsRequest
import rcon.exceptions

from utils import *

rcon_client = get_rcon_client()
requests.get("http://localhost:25585/send/MC服务器已启动")

instance_id = requests.get('http://100.100.100.200/latest/meta-data/instance-id').text
request = DescribeContainerGroupsRequest(region_id=RegionId, container_group_ids=f'["{instance_id}"]', with_event=True)
eci_client = get_ali_client('eci')
n = 0
messages = []
is_not_anyone_online = None


def send(msg):
    if msg not in messages:
        requests.get(f"http://localhost:25585/send/{msg}")
        messages.append(msg)


while True:
    response = eci_client.describe_container_groups(request)

    for event in response.body.container_groups[0].events:
        dt = datetime.fromisoformat(event.first_timestamp)
        if (datetime.now(tz=timezone.utc) - dt).seconds > 60:  # 距现在超1分钟的事件跳过
            break

        if event.reason == 'SpotToBeReleased':
            message = 'ECI实例即将过期:' + event.message
            send(message)
            requests.get(f"http://localhost:25585/stop_mc")
        elif event.type == 'Warning':  # 防止重复消息
            message = f'实例警告：{event.message}'
            send(message)

    try:
        is_not_anyone_online = rcon_client.run('list').startswith('There are 0 of a max of')
    except (rcon.exceptions.EmptyResponse, BrokenPipeError):  # rcon崩了
        check_response = requests.get(f"http://localhost:25585/check")
        if 'unhealthy' in check_response.text:
            send(f'rcon异常且{check_response.text}，实例即将删除')
            requests.get("http://localhost:25585/delete")
        else:
            send('rcon异常，自动关闭功能失效，MC服务器仍在运行，请手动介入')
        break
    else:
        if is_not_anyone_online:
            n += 1
        else:
            n = 0

        if n >= 15:
            rcon_client.close()
            requests.get("http://localhost:25585/stop_mc")
            break

    time.sleep(20)

while True:
    time.sleep(60)