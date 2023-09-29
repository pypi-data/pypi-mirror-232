#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# @FileName     :   subscribe.py
# @Function     :   ChainMaker 订阅接口
from typing import List, Callable, Iterable, Union, Generator


from chainmaker.apis.base_client import BaseClient
from chainmaker.protos.common.result_pb2 import ContractEventInfoList
from chainmaker.protos.common.block_pb2 import BlockInfo, BlockHeader
from chainmaker.protos.store.store_pb2 import BlockWithRWSet
from chainmaker.protos.common.transaction_pb2 import Transaction
from chainmaker.protos.common.request_pb2 import Payload
from chainmaker.utils import common
from chainmaker.keys import ParamKeys, SystemContractNames, SubscribeManageMethods, Defaults


class SubscribeMixIn(BaseClient):
    def subscribe_block(self, start_block: int, end_block: int, with_rw_set=False, only_header=False,
                        timeout: int = Defaults.SUBSCRIBE_TIMEOUT) -> Generator[
        Union[BlockInfo, BlockWithRWSet, BlockHeader], None, None]:
        """
        订阅区块
        :param start_block: 订阅的起始区块
        :param end_block: 订阅的结束区块
        :param with_rw_set: 是否包含读写集
        :param only_header: 是否只订阅区块头
        :param timeout: 订阅尚未产生区块的等待超时时间, 默认60s
        :return: 生成器，如果only_header=True,其中每一项为BlockHeader
                        另外如果with_rw_set=True,其中每一项为BlockWithRWSet
                        否则其中每一项为BlockInfo
        """
        payload = self.create_subscribe_block_payload(start_block, end_block, with_rw_set, only_header)
        response_iterator = self._get_subscribe_stream(payload, timeout)
        for response in response_iterator:
            if only_header is True:
                msg_obj = BlockHeader()
            elif with_rw_set is True:
                msg_obj = BlockWithRWSet()
            else:
                msg_obj = BlockInfo()
            
            msg_obj.ParseFromString(response.data)
            yield msg_obj
    
    def subscribe_tx(self, start_block: int, end_block: int, contract_name: str, tx_ids: List[str],
                     timeout: int = None) -> Generator[Transaction, None, None]:
        payload = self.create_subscribe_tx_payload(start_block, end_block, contract_name, tx_ids)
        response_iterator = self._get_subscribe_stream(payload, timeout)
        for response in response_iterator:
            transaction = Transaction()
            transaction.ParseFromString(response.data)
            yield transaction
    
    def subscribe_contract_event(self, start_block, end_block, topic: str, contract_name: str,
                                 timeout: int = Defaults.SUBSCRIBE_TIMEOUT) -> Generator[ContractEventInfoList, None, None]:
        payload = self.create_subscribe_contract_event_payload(start_block, end_block, contract_name, topic)
        response_iterator = self._get_subscribe_stream(payload, timeout)
        
        for response in response_iterator:
            contract_event_info_list = ContractEventInfoList()
            contract_event_info_list.ParseFromString(response.data)
            yield contract_event_info_list
    
    def subscribe(self, payload: Payload, timeout: int = Defaults.SUBSCRIBE_TIMEOUT, callback: Callable = None) -> None:
        """
        订阅区块、交易、合约事件
        :param payload: 订阅Payload
        :param timeout: 订阅待产生区块等待超时时间
        :param callback: 回调函数，默认为self._callback
        :return: None
        """
        callback = callback or self._callback
        response_iterator = self._get_subscribe_stream(payload, timeout)
        for response in response_iterator:
            callback(response.data)
    
    def _get_subscribe_stream(self, payload: Payload, timeout: int) -> Iterable:
        """
        获取可迭代的订阅流数据
        :param payload: 请求负荷
        :return: 可迭代的订阅流数据 grpc._channel._MultiThreadedRendezvous对象, 已知所有订阅信息产生(达到集合点)后才返回全部数据
        """
        request = self._generate_tx_request(payload)
        response_iterator = self._get_client().Subscribe(request, timeout)
        return response_iterator
    
    def create_subscribe_block_payload(self, start_block: int, end_block: int, with_rw_set=False,
                                       only_header=False) -> Payload:
        """
        创建订阅区块请求负荷
        :param start_block: 订阅的起始区块
        :param end_block: 订阅的结束区块
        :param with_rw_set: 是否包含读写集
        :param only_header: 是否只订阅区块头
        :return: 请求负荷
        """
        params = {
            ParamKeys.START_BLOCK: common.uint64_to_bytes(start_block),
            ParamKeys.END_BLOCK: common.uint64_to_bytes(end_block),
            ParamKeys.WITH_RWSET: common.bool_to_str(with_rw_set),
            ParamKeys.ONLY_HEADER: common.bool_to_str(only_header),
        }
        payload = self.payload_builder.create_subscribe_payload(SystemContractNames.SUBSCRIBE_MANAGE,
                                                                SubscribeManageMethods.SUBSCRIBE_BLOCK, params)
        return payload
    
    def create_subscribe_tx_payload(self, start_block: int, end_block: int, contract_name: str,
                                    tx_ids: List[str]) -> Payload:
        """
        创建订阅区块交易请求负荷
        :param start_block: 订阅的起始区块
        :param end_block: 订阅的结束区块
        :param contract_name: 合约名称
        :param tx_ids: 交易id列表
        :return:
        """
        params = {
            ParamKeys.START_BLOCK: common.uint64_to_bytes(start_block),
            ParamKeys.END_BLOCK: common.uint64_to_bytes(end_block),
            ParamKeys.CONTRACT_NAME: contract_name,
            ParamKeys.TX_IDS: ','.join(tx_ids),
        }
        return self.payload_builder.create_subscribe_payload(SystemContractNames.SUBSCRIBE_MANAGE,
                                                             SubscribeManageMethods.SUBSCRIBE_TX, params)
    
    def create_subscribe_contract_event_payload(self, start_block: int, end_block: int,
                                                contract_name: str, topic: str) -> Payload:
        """
        创建订阅合约事件请求负荷
        :param start_block: 订阅的起始区块
        :param end_block: 订阅的结束区块
        :param contract_name: 合约名称
        :param topic: 主题
        :return: 请求负荷
        """
        params = {
            ParamKeys.START_BLOCK: common.uint64_to_bytes(start_block),
            ParamKeys.END_BLOCK: common.uint64_to_bytes(end_block),
            ParamKeys.TOPIC: topic,
            ParamKeys.CONTRACT_NAME: contract_name,
        }
        return self.payload_builder.create_subscribe_payload(SystemContractNames.SUBSCRIBE_MANAGE,
                                                             SubscribeManageMethods.SUBSCRIBE_CONTRACT_EVENT, params)
    
    def _callback(self, data: bytes):
        """示例回调方法"""
        print('receive data', data)
