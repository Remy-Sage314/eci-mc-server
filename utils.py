from time import sleep

from rcon.source import Client
import requests
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_eci20180808.client import Client as Eci20180808Client
from alibabacloud_credentials.client import Client as CredClient
from alibabacloud_credentials.models import Config as CredConfig

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


def get_eci_client(ak_id=None, ak_secret=None):
    if ak_id and ak_secret:
        config = open_api_models.Config(
            access_key_id=ak_id,
            access_key_secret=ak_secret,
            region_id=RegionId,
            endpoint=EndPoint
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
            endpoint=EndPoint
        )

    eci_client = Eci20180808Client(config)
    return eci_client


def setup_dns():
    ip = requests.get('http://100.100.100.200/latest/meta-data/eipv4').text
    requests.get(f'http://dynv6.com/api/update?hostname={Domain}&token={DYNV6Token}&ipv4={ip}')
