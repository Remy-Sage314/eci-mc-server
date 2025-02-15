from time import sleep

from rcon.source import Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_eci20180808.client import Client as Eci20180808Client

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


def get_eci_client():
    config = open_api_models.Config(
        access_key_id=AccessKeyID,
        access_key_secret=AccessKeySecret,
        region_id=RegionId,
        endpoint=EndPoint
    )
    eci_client = Eci20180808Client(config)
    return eci_client
