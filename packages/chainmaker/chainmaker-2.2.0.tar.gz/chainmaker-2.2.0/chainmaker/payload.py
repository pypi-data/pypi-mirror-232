#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# @FileName     :   payload.py
# @Function     :   ChainMaker生成Payload


import time
from typing import Union

from chainmaker.keys import RuntimeType, ParamKeys, SystemContractNames
from chainmaker.protos.common.request_pb2 import Payload, TxType, KeyValuePair
from chainmaker.utils import common


class PayloadBuilder:
    """Payload构建者"""
    def __init__(self, chain_id):
        self.chain_id = chain_id
    
    def _create_payload(self, tx_type: TxType, contract_name: str, method: str, params: Union[dict, list] = None,
                        tx_id="", seq=0) -> Payload:
        pairs = common.params_map_kvpairs(params)
        return Payload(
            chain_id=self.chain_id,
            tx_type=tx_type,
            tx_id=tx_id if tx_id else common.gen_rand_tx_id(),
            timestamp=int(time.time()),
            contract_name=contract_name,
            method=method,
            parameters=pairs,
            sequence=seq
        )
    
    def create_invoke_payload(self, contract_name: str, method: str, params: Union[dict, list] = None, tx_id="", seq=0):
        return self._create_payload(TxType.INVOKE_CONTRACT, contract_name, method, params, tx_id, seq)

    def create_query_payload(self, contract_name: str, method: str, params: Union[list, dict] = None, tx_id="", seq=0):
        return self._create_payload(TxType.QUERY_CONTRACT, contract_name, method, params, tx_id, seq)
    
    def create_subscribe_payload(self, contract_name: str, method: str, params: Union[list, dict] = None, tx_id="",
                                 seq=0):
        return self._create_payload(TxType.SUBSCRIBE, contract_name, method, params, tx_id, seq)
    
    def create_archive_payload(self, contract_name: str, method: str, params: Union[list, dict] = None, tx_id: str = "",
                               seq: int = 0):
        return self._create_payload(TxType.ARCHIVE, contract_name, method, params, tx_id, seq)
    
    def create_contract_manage_payload(self, method: str, contract_name: str = None, version: str = None,
                                       byte_code: bytes = None, runtime_type: RuntimeType = None, kvs: list = None,
                                       seq: int = 0):
        kvs = kvs or []
        if contract_name is not None:
            kvs.append(KeyValuePair(key=ParamKeys.CONTRACT_NAME, value=contract_name.encode()))
        if version is not None:
            kvs.append(KeyValuePair(key=ParamKeys.CONTRACT_VERSION, value=version.encode()))
        if runtime_type is not None:
            kvs.append(KeyValuePair(key=ParamKeys.CONTRACT_RUNTIME_TYPE, value=runtime_type.encode()))
        if byte_code is not None:
            if runtime_type == 'EVM':
                byte_code = bytes.fromhex(byte_code.decode())  # EMV byte_code需要转为hex
            kvs.append(KeyValuePair(key=ParamKeys.CONTRACT_BYTECODE, value=byte_code))
        return self.create_invoke_payload(SystemContractNames.CONTRACT_MANAGE, method, kvs, seq=seq)


