# -*- coding: utf-8 -*-
import logging
from time import sleep
import traceback

from rcon.source import Client
import requests
from Tea.exceptions import UnretryableException, TeaException

from config import get_config
Conf = get_config()

def get_rcon_client():
    client = Client('127.0.0.1', 25575, passwd=Conf.RconPassword)
    while True:
        try:
            client.__enter__()
            break
        except ConnectionError:
            sleep(3)
    return client



def get_ali_client(client_type: str, ak_id=None, ak_secret=None, security_token=None):
    from alibabacloud_tea_openapi import models as open_api_models
    if ak_id and ak_secret:
        config = open_api_models.Config(
            access_key_id=ak_id,
            access_key_secret=ak_secret,
            security_token=security_token,
            region_id=Conf.RegionId,
        )
    else:
        from alibabacloud_credentials.client import Client as CredClient
        from alibabacloud_credentials.models import Config as CredConfig
        credentials_config = CredConfig(
            type='ecs_ram_role',  # 凭证类型。
            role_name='EciManagerRole'
        )
        credentials_client = CredClient(credentials_config)
        config = open_api_models.Config(
            credential=credentials_client,
            region_id=Conf.RegionId,
        )


    match client_type:
        case 'eci':
            from alibabacloud_eci20180808.client import Client as Eci20180808Client
            config.endpoint = Conf.ECIEndPoint
            return Eci20180808Client(config)
        case 'sts':
            from alibabacloud_sts20150401.client import Client as Sts20150401Client
            config.endpoint = Conf.STSEndPoint
            return Sts20150401Client(config)
        case 'dns':
            from alibabacloud_alidns20150109.client import Client as DNSClient
            config.endpoint = Conf.DNSEndPoint
            return DNSClient(config)
        case _:
            raise ValueError('Unknown client type')


def update_dns(ip, logger: logging.Logger):
    # dynv6
    if Conf.EnableDYNV6:
        status = requests.get(f'http://dynv6.com/api/update?hostname={Conf.DYNV6Domain}&token={Conf.DYNV6Token}&ipv4={ip}')
        if status.status_code == 200:
            logger.debug('dynv6 dns update successfully')

    # aliyun
    if Conf.EnableAliyunDNS:
        try:
            from alibabacloud_sts20150401 import models as sts_models
            sts_client = get_ali_client('sts')
            assumerole_request = sts_models.AssumeRoleRequest(
                role_session_name='mc_ddns',
                role_arn=Conf.DnsRoleARN
            )
            res = sts_client.assume_role(assumerole_request).body.credentials

            from alibabacloud_alidns20150109 import models as dns_models
            dns_client = get_ali_client('dns', res.access_key_id, res.access_key_secret, res.security_token)
            update_domain_record_request = dns_models.UpdateDomainRecordRequest(
                record_id=Conf.DnsRecordID,
                rr='mc',
                value=ip,
                type='AAAA'
            )
            status = dns_client.update_domain_record(update_domain_record_request).status_code
        except Exception as e:
            if 'LastOperationNotFinished' not in str(e):
                logger.warning(e)
        else:
            if status == 200:
                logger.debug('aliyun dns update successfully')

class HandleAliException:
    def __init__(self, logger):
        self.logger = logger

    @staticmethod
    def __enter__():
        return

    def __exit__(self, exc_type, exc_val, exc_tb):
        if isinstance(exc_val, (TeaException, UnretryableException)):
            self.logger.warning(f"Exception Type: {exc_type}, Exception Value: {exc_val},"
                                f" Detailed Traceback: {"".join(traceback.format_tb(exc_tb))}")
        return True
