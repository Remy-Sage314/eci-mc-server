from time import sleep

from rcon.source import Client
import requests

from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_credentials.client import Client as CredClient
from alibabacloud_credentials.models import Config as CredConfig

from alibabacloud_eci20180808.client import Client as Eci20180808Client
from alibabacloud_sts20150401.client import Client as Sts20150401Client
from alibabacloud_alidns20150109.client import Client as DNSClient
from alibabacloud_dingtalk.robot_1_0.client import Client as DingtalkRobotClient
from alibabacloud_dingtalk.oauth2_1_0.client import Client as DingtalkOauthClient

from alibabacloud_sts20150401 import models as sts_models
from alibabacloud_alidns20150109 import models as dns_models
from alibabacloud_dingtalk.robot_1_0 import models as ding_robot_models
from alibabacloud_dingtalk.oauth2_1_0 import models as ding_oauth_models


from config import *


def get_rcon_client():
    client = Client('127.0.0.1', 25575, passwd=RconPassword)
    while True:
        try:
            client.__enter__()
            break
        except ConnectionError:
            sleep(3)
    return client


DingtalkAK = None
def get_dingtalk_ak():
    global DingtalkAK
    if not DingtalkAK:
        client = get_ali_client('dingtalk_oauth')
        get_access_token_request = ding_oauth_models.GetAccessTokenRequest(
            app_key=DingtalkClientID,
            app_secret=DingtalkClientSecret
        )
        DingtalkAK = client.get_access_token(get_access_token_request).body.access_token
    return DingtalkAK

def get_ali_client(client_type, ak_id=None, ak_secret=None, security_token=None):
    if ak_id and ak_secret:
        config = open_api_models.Config(
            access_key_id=ak_id,
            access_key_secret=ak_secret,
            security_token=security_token,
            region_id=RegionId,
        )
    else:
        credentials_config = CredConfig(
            type='ecs_ram_role',  # 凭证类型。
            role_name='EciManagerRole'
        )
        credentials_client = CredClient(credentials_config)
        config = open_api_models.Config(
            credential=credentials_client,
            region_id=RegionId,
        )

    if client_type.startswith('dingtalk'):
        config.credential = None
        config.protocol = 'https'
        config.region_id = 'central'

    match client_type:
        case 'eci':
            config.endpoint = ECIEndPoint
            return Eci20180808Client(config)
        case 'sts':
            config.endpoint = STSEndPoint
            return Sts20150401Client(config)
        case 'dns':
            config.endpoint = DNSEndPoint
            return DNSClient(config)
        case 'dingtalk_robot':
            return DingtalkRobotClient(config)
        case 'dingtalk_oauth':
            return DingtalkOauthClient(config)
        case _:
            raise ValueError('Unknown client type')


def setup_dns():
    ip = requests.get('http://100.100.100.200/latest/meta-data/eipv4').text
    # dynv6
    status = requests.get(f'http://dynv6.com/api/update?hostname={DYNV6Domain}&token={DYNV6Token}&ipv4={ip}')
    if status.status_code == 200:
        print('dynv6 update successfully')

    # aliyun
    try:
        sts_client = get_ali_client('sts')
        assumerole_request = sts_models.AssumeRoleRequest(
            role_session_name='Eci',
            role_arn=DnsRoleARN
        )
        res = sts_client.assume_role(assumerole_request).body.credentials

        dns_client = get_ali_client('dns', res.access_key_id, res.access_key_secret, res.security_token)
        update_domain_record_request = dns_models.UpdateDomainRecordRequest(
            record_id=DnsRecordID,
            rr='@',
            value=ip,
            type='A'
        )
        status = dns_client.update_domain_record(update_domain_record_request).status_code
    except Exception as e:
        print(e)
    else:
        if status == 200:
            print('aliyun dns update successfully')
