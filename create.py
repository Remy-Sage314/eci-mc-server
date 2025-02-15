#!/home/happy68/.virtualenvs/a/bin/python3
from alibabacloud_eci20180808.models import (
    CreateContainerGroupRequest, CreateContainerGroupRequestContainer,
    CreateContainerGroupRequestContainerReadinessProbe,
    CreateContainerGroupRequestContainerReadinessProbeHttpGet,
    CreateContainerGroupRequestContainerVolumeMount,
    CreateContainerGroupRequestVolume,
    CreateContainerGroupRequestVolumeNFSVolume
)

from utils import get_eci_client

http_get = CreateContainerGroupRequestContainerReadinessProbeHttpGet(
    scheme='HTTP',
    path='/check',
    port=25585
)
readiness_probe = CreateContainerGroupRequestContainerReadinessProbe(
    http_get=http_get,
    initial_delay_seconds=10,
    period_seconds=60
)
volume_mount = CreateContainerGroupRequestContainerVolumeMount(
    mount_path='opt/mc',
    read_only=False,
    sub_path='mc/',
    name='nas-mc'
)
container = CreateContainerGroupRequestContainer(
    readiness_probe=readiness_probe,
    volume_mount=[volume_mount],
    image_pull_policy='IfNotPresent',
    name='container-mc',
    image='registry-vpc.cn-hangzhou.aliyuncs.com/bmzhk/mc:2',
    cpu=2,
    memory=8
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
request = CreateContainerGroupRequest(
    region_id='cn-hangzhou',
    zone_id='cn-hangzhou-k',
    security_group_id='sg-bp17z1tqsnklf5c5n7d0',
    v_switch_id='vsw-bp19befc46buz5uuxg40i',
    container_group_name='mc-container-group',
    restart_policy='Never',
    instance_type='ecs.g8a.large,ecs.g8i.large',
    auto_match_image_cache=True,
    spot_strategy='SpotWithPriceLimit',
    spot_price_limit=0.4,
    auto_create_eip=True,
    eip_bandwidth=5,
    eip_isp='BGP',
    container=[container],
    volume=[volume],
    spot_duration=1,
    dry_run=False  # 是否预检
)

if __name__ == '__main__':
    client = get_eci_client()
    response = client.create_container_group(request)
    print(response.body.container_group_id)
