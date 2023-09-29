#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# @FileName     :   result_utils.py
# @Function     :   ChainMaker 结果处理实用方法
import base64
from typing import Union

from google.protobuf import json_format

from chainmaker.protos.common.result_pb2 import TxResponse, Result
from chainmaker.protos.common.transaction_pb2 import TransactionWithRWSet, TransactionInfo

SUCCESS_CODE = 0


def result_is_ok(response: Union[TxResponse, Result]) -> bool:
    """
    检查合约是否成功
    :param Union[TxResponse, Transaction] resp: 响应信息
    :param need_contract_result: 是否需要交易合约结果
    :return: 成功返回True, 否则返回False
    """
    if hasattr(response, 'code') and SUCCESS_CODE != response.code:
        return False
    
    if isinstance(response, TxResponse):
        if hasattr(response, 'result') and hasattr(response.result, 'code') and SUCCESS_CODE != response.result.code:
            return False
        if hasattr(response, 'contract_result') and SUCCESS_CODE != response.contract_result.code:
            return False
    
    if isinstance(response, Result):
        result = response
        if SUCCESS_CODE != result.code:
            return False
        if hasattr(result, 'contract_result') and SUCCESS_CODE != result.contract_result.code:
            return False
        
    if isinstance(response, TransactionInfo):
        result = response.transaction.result
        if SUCCESS_CODE != result.code:
            return False
        if hasattr(result, 'contract_result') and SUCCESS_CODE != result.contract_result.code:
            return False
        
    
    
    return True


def check_response(response: Union[TxResponse, Result]):
    """
    检查合约是否成功
    :param Union[TxResponse, Transaction] resp: 响应信息
    :param need_contract_result: 是否需要交易合约结果
    :return: None
    """
    assert result_is_ok(response), f'响应失败: {response}'
 
    
def msg_to_dict(msg) -> dict:
    """
    proto消息体转字典
    :param msg: 消息体，如TxResponse, Result, BlockInfo等
    :return: 字典，bytes类型会转为base64字符串
    """
    return json_format.MessageToDict(msg)


def msg_to_json(msg) -> str:
    """
    proto消息体转JSON字符串
    :param msg: 消息体，如TxResponse, Result, BlockInfo等
    :return: JSON字符串，bytes类型会转为base64字符串
    """
    return json_format.MessageToJson(msg)


def bytes_to_hex(data: bytes) -> str:
    """
    用于result中的bytes转16进制字符串
    :param data: 二进制数据，如bytes_to_hex(block_info.block.header.block_hash)可以得到区块哈希
    :return: 16进制字符串
    """
    return data.hex()


def bytes_to_str(data: bytes) -> str:
    """
    用于result中的bytes转字符串
    :param data:bytes字符串
    :return: 对应的字符串
    """
    return data.decode()


def bytes_to_int(data: bytes) -> int:
    """
    用于result中的bytes转整形
    :param data: bytes字符串
    :return: 整形
    :raises ValueError 如果bytes不是纯数字形式
    """
    return int(data.hex(), 16)


def base64_to_hex(data: str) -> str:
    """
    用于将MessageToDict或MessageToJson转换后的结果中的base64还原成bytes并转为16进制字符串
    :param data: 由bytes转为的base64字符串
    :return: 16进制字符串
    """
    return base64.b64decode(data).hex()


def base64_to_str(data: str) -> str:
    """
    用于将MessageToDict或MessageToJson转换后的结果中的base64还原成bytes并转为字符串
    :param data: 由bytes转为的base64字符串
    :return: 原字符串
    """
    return base64.b64decode(data).decode()


def base64_to_int(data: str) -> int:
    """
    用于将MessageToDict或MessageToJson转换后的结果中的base64还原成bytes并转为整形
    :param data: 由bytes转为的base64字符串
    :return: 整数
    """
    return int(base64.b64decode(data).hex(), 16)
