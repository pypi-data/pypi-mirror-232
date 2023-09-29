#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# @FileName     :   common.py
# @Function     :   实用工具方法

import struct
import uuid
from typing import Union

from google.protobuf import json_format
from google.protobuf.message import Message

from chainmaker.protos.common import request_pb2


def gen_rand_tx_id():
    return uuid.uuid4().hex + uuid.uuid4().hex


def gen_rand_contract_name(prefix: str = ''):
    if isinstance(prefix, str):
        return f'{prefix}{str(uuid.uuid4()).replace("-", "")}'


def ensure_bytes(value: Union[bytes, str, bool, int]):
    if isinstance(value, bytes):
        return value
    elif isinstance(value, str):
        return value.encode()
    elif isinstance(value, bool):
        return b'true' if value is True else b'false'
    else:
        return str(value).encode()


def params_map_kvpairs(params: Union[dict, list]) -> list:  # TODO params is list
    if not params:
        return []
    
    if isinstance(params, list) and len(params) > 0 and isinstance(params[0], request_pb2.KeyValuePair):
        return params
    
    if isinstance(params, list):
        pairs = []
        for item in params:
            assert isinstance(item, dict), f'list中每一项应为dict类型: {item}'
            kv = request_pb2.KeyValuePair(key=item.get('key'), value=ensure_bytes(item.get('value')))
            pairs.append(kv)
    
    elif isinstance(params, dict):
        return [request_pb2.KeyValuePair(key=key, value=val if type(val) is bytes else str(val).encode()) for key, val
                in params.items()]
    else:
        raise TypeError("仅支持None, dict或list类型")


def uint64_to_bytes(i: int):
    return struct.pack('<Q', i)


def bool_to_str(b: bool):
    return "true" if b else "false"


def msg_to_bytes(msg: Message) -> bytes:
    """proto消息对象转bytes"""
    return msg.SerializeToString()


def msg_from_bytes(msg: Message, data: bytes) -> Message:
    """proto消息对象从bytes中加载数据"""
    return msg.ParseFromString(data)


def msg_to_json(msg: Message) -> str:
    """proto消息对象转JSON字符串"""
    return json_format.MessageToJson(msg)


def msg_to_dict(msg: Message) -> dict:
    """proto消息对象转字典"""
    return json_format.MessageToDict(msg)
