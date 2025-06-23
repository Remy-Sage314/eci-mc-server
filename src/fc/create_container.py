# -*- coding: utf-8 -*-
import alibabacloud_eci20180808.client
from alibabacloud_eci20180808.models import (
    CreateContainerGroupRequest, CreateContainerGroupRequestContainer,
    CreateContainerGroupRequestContainerVolumeMount,
    CreateContainerGroupRequestVolume,
    CreateContainerGroupRequestVolumeNFSVolume,
    DescribeContainerGroupsRequest, CreateContainerGroupRequestContainerEnvironmentVar,
)

volume_mount = CreateContainerGroupRequestContainerVolumeMount(
    mount_path='/mc',
    sub_path='mc/',
    read_only=False,
    name='nas-mc'
)
environment_var = CreateContainerGroupRequestContainerEnvironmentVar(
    key='mc_version_to_run'
)
container = CreateContainerGroupRequestContainer(
    volume_mount=[volume_mount],
    image_pull_policy='IfNotPresent',
    name='container-mc',
    image='registry-vpc.cn-hangzhou.aliyuncs.com/bmzhk/mc:latest',
    cpu=2,
    memory=8,
    environment_var=[environment_var]
)
nfs_volume = CreateContainerGroupRequestVolumeNFSVolume(
    path='/',
    read_only=False,
    server='0b83a49991-uqs5.cn-hangzhou.nas.aliyuncs.com'
)
volume = CreateContainerGroupRequestVolume(
    type='NFSVolume',
    nfsvolume=nfs_volume,
    name='nas-mc'
)
create_request = CreateContainerGroupRequest(
    region_id='cn-hangzhou',
    zone_id='cn-hangzhou-k',
    security_group_id='sg-bp17z1tqsnklf5c5n7d0',
    v_switch_id='vsw-bp19befc46buz5uuxg40i',
    container_group_name='mc-container-group',
    restart_policy='Never',
    instance_type='ecs.g8ae.large,ecs.g8a.large,ecs.g8i.large',
    auto_match_image_cache=True,
    spot_strategy='SpotWithPriceLimit',
    spot_price_limit=0.4,
    auto_create_eip=True,
    eip_bandwidth=8,
    eip_isp='BGP',
    container=[container],
    volume=[volume],
    spot_duration=1,
    ram_role_name='EciManagerRole',
    dry_run=False  # 是否预检
)
query_request = DescribeContainerGroupsRequest(region_id='cn-hangzhou', container_group_name='mc-container-group')

def query_exists(client: alibabacloud_eci20180808.client.Client):
    response = client.describe_container_groups(query_request)
    for container_group in response.body.container_groups:
        if container_group.status  == 'Running' or container_group.status  == 'Pending':
            return True
    return False


def create_container_group(client: alibabacloud_eci20180808.client.Client, version='', force=False):
    environment_var.value = version
    if not query_exists(client) or force:
        response = client.create_container_group(create_request)
        return response.status_code
    return 400
