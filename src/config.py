# -*- coding: utf-8 -*-
from pydantic import BaseModel

class _Version(BaseModel):
    WorkingDir: str = None
    Command: str = None


class _Config(BaseModel):
    # dingtalk自定义机器人
    EnableDingtalk: bool = True
    DingtalkSecret: str = None
    RobotUrl: str = None
    # PushApi
    PushApiK: str = None
    # RCON
    RconPassword: str = None
    # DYNV6
    EnableDYNV6: bool = False
    DYNV6Domain: str = None
    DYNV6Token: str = None
    # AliyunDNS
    EnableAliyunDNS: bool = True
    DnsRecordID: str = None
    DnsRoleARN: str = None
    # Aliyun
    ECIEndPoint: str = None
    STSEndPoint: str = None
    DNSEndPoint: str = None
    RegionId: str = None
    # 是否为云环境（仅用于测试）
    IsCloud: bool = True
    # Versions
    Versions: dict[str, _Version] = None
    DefaultVersion: str = None


def get_config():
    with open('/mc/config.json', 'r') as f:
        return _Config.model_validate_json(f.read())

def save_config(config: _Config):
    with open('/mc/config.json', 'w') as f:
        f.write(config.model_dump_json())
