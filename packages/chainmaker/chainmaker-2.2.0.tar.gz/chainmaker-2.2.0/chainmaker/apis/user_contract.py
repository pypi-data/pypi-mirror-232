#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# @FileName     :   user_contract.py
# @Function     :   ChainMaker用户合约接口
from typing import Union, List

from chainmaker.apis.base_client import BaseClient
from chainmaker.exceptions import RequestError
from chainmaker.keys import ContractManageMethods
from chainmaker.keys import RuntimeType
from chainmaker.protos.common.request_pb2 import Payload, TxRequest, EndorsementEntry
from chainmaker.protos.common.result_pb2 import TxResponse, TxStatusCode
from chainmaker.utils import common, file_utils


class UserContractMixIn(BaseClient):
    def create_contract_create_payload(self, contract_name: str, version: str, byte_code_or_file_path: str,
                                       runtime_type: RuntimeType,
                                       params: dict) -> Payload:
        """生成 创建合约的payload
        :param contract_name: 合约名
        :param version: 合约版本
        :param byte_code_or_file_path: 合约字节码：可以是字节码；合约文件路径；或者 hex编码字符串；或者 base64编码字符串。
        :param runtime_type: contract_pb2.RuntimeType.WASMER
        :param params: 合约参数，dict类型，key 和 value 尽量为字符串
        :return: Payload
        :raises ValueError: 如果 byte_code 不能转成合约字节码
        """
        self.logger.debug("[SDK] create [ContractCreate] to be signed payload")
        
        byte_code = file_utils.load_byte_code(byte_code_or_file_path)
        if not byte_code:
            raise ValueError("can't get contract bytes code from byte_code param")
        kvs = common.params_map_kvpairs(params)
        return self.payload_builder.create_contract_manage_payload(ContractManageMethods.INIT_CONTRACT,
                                                                   contract_name,
                                                                   version,
                                                                   byte_code,
                                                                   runtime_type,
                                                                   kvs)
    
    def create_contract_upgrade_payload(self, contract_name: str, version: str, byte_code_or_file_path: str,
                                        runtime_type: RuntimeType,
                                        params: dict) -> Payload:
        """生成 升级合约的payload
        :param contract_name: 合约名
        :param version: 合约版本
        :param byte_code_or_file_path: 合约字节码：可以是字节码；合约文件路径；或者 hex编码字符串；或者 base64编码字符串。
        :param runtime_type: contract_pb2.RuntimeType.WASMER
            eg. 'INVALID', 'NATIVE', 'WASMER', 'WXVM', 'GASM', 'EVM', 'DOCKER_GO', 'DOCKER_JAVA'
        :param params: 合约参数，dict类型，key 和 value 尽量为字符串
        :return: Payload
        :raises ValueError: 如果 byte_code 不能转成合约字节码
        """
        self.logger.debug("[SDK] create [ContractUpgrade] to be signed payload")
        
        byte_code = file_utils.load_byte_code(byte_code_or_file_path)
        if not byte_code:
            raise ValueError("can't get contract bytes code from byte_code param")
        kvs = common.params_map_kvpairs(params)
        return self.payload_builder.create_contract_manage_payload(ContractManageMethods.UPGRADE_CONTRACT,
                                                                   contract_name,
                                                                   version,
                                                                   byte_code,
                                                                   runtime_type,
                                                                   kvs)
    
    def create_contract_freeze_payload(self, contract_name: str) -> Payload:
        """生成 冻结合约的payload
        :param contract_name: 合约名
        :return: Payload
        """
        self.logger.debug("[SDK] create [ContractFreeze] to be signed payload")
        
        return self.payload_builder.create_contract_manage_payload(ContractManageMethods.FREEZE_CONTRACT,
                                                                   contract_name)
    
    def create_contract_unfreeze_payload(self, contract_name: str) -> Payload:
        """生成 解冻合约的payload
        :param contract_name: 合约名
        :return: Payload
        """
        self.logger.debug("[SDK] create [ContractUnfreeze] to be signed payload")
        
        return self.payload_builder.create_contract_manage_payload(ContractManageMethods.UNFREEZE_CONTRACT,
                                                                   contract_name)
    
    def create_contract_revoke_payload(self, contract_name: str) -> Payload:
        """生成 吊销合约的payload
        :param contract_name: 合约名
        :return: Payload
        """
        self.logger.debug("[SDK] create [ContractRevoke] to be signed payload")
        
        return self.payload_builder.create_contract_manage_payload(ContractManageMethods.REVOKE_CONTRACT,
                                                                   contract_name)
    
    def sign_contract_manage_payload(self, payload: Payload) -> bytes:
        """对 合约管理的 payload 字节数组进行签名，返回签名后的payload字节数组
        :param payload: 交易 payload
        :return: Payload 的字节数组
        :raises DecodeError: 如果 byte_code 解码失败
        """
        
        return self.user.endorse(payload)
    
    def send_contract_manage_request(self, payload: Payload, endorsers: List[EndorsementEntry], timeout: int = None,
                                     with_sync_result: bool = None) -> TxResponse:
        """发送合约管理的请求
        :param endorsers: 背书列表
        :param payload: 请求的 payload
        :param timeout: 超时时间
        :param with_sync_result: 是否同步交易执行结果。如果不同步，返回tx_id，供异步查询; 同步则循环等待，返回交易的执行结果。
        :return: TxResponse
        :raises RequestError: 请求失败
        """
        response = self.send_request_with_sync_result(payload, timeout=timeout, with_sync_result=with_sync_result, endorsers=endorsers)
        return response
    
    def invoke_contract(self, contract_name: str, method: str, params: dict = None, tx_id: str = "",
                        timeout: int = None,
                        with_sync_result: bool = None) -> TxResponse:
        """调用 用户合约 接口
        :param contract_name: 合约名
        :param method: 调用合约方法名
        :param params: 调用参数，参数类型为dict
        :param tx_id: 交易id，如果交易id为空/空字符串，则创建新的tx_id
        :param timeout: 超时时间，默认为 3s
        :param with_sync_result: 是否同步交易执行结果。如果不同步，返回tx_id，供异步查询; 同步则循环等待，返回交易的执行结果。
        :return: TxResponse
        :raises RequestError: 请求失败
        """
        self.logger.debug("[SDK] begin to INVOKE contract, [contract_name:%s]/[method:%s]/[tx_id:%s]/[params:%s]",
                          contract_name, method, tx_id, params)
        
        if not tx_id:
            tx_id = common.gen_rand_tx_id()
        
        pairs = common.params_map_kvpairs(params)
        payload = self.payload_builder.create_invoke_payload(contract_name, method, pairs, tx_id)
        
        response = self.send_request_with_sync_result(payload, timeout=timeout, with_sync_result=with_sync_result)
        return response
    
    def invoke_contract_with_limit(self, contract_name: str, method: str, params: dict = None, tx_id: str = "",
                                   timeout: int = None,
                                   with_sync_result: bool = None, gas_limit: int = None) -> TxResponse:
        """调用 用户合约 接口
        :param contract_name: 合约名
        :param method: 调用合约方法名
        :param params: 调用参数，参数类型为dict
        :param tx_id: 交易id，如果交易id为空/空字符串，则创建新的tx_id
        :param timeout: 超时时间，默认为 3s
        :param with_sync_result: 是否同步交易执行结果。如果不同步，返回tx_id，供异步查询; 同步则循环等待，返回交易的执行结果。
        :param gas_limit: Gas交易限制
        :return: TxResponse
        :raises RequestError: 请求失败
        """
        self.logger.debug("[SDK] begin to INVOKE contract, [contract_name:%s]/[method:%s]/[tx_id:%s]/[params:%s]",
                          contract_name, method, tx_id, params)
        if not tx_id:
            tx_id = common.gen_rand_tx_id()
        
        pairs = common.params_map_kvpairs(params)
        payload = self.payload_builder.create_invoke_payload(contract_name, method, pairs, tx_id)
        self.attach_gas_limit(payload, gas_limit)
        
        response = self.send_request_with_sync_result(payload, timeout=timeout, with_sync_result=with_sync_result)
        return response
    
    def query_contract(self, contract_name: str, method: str, params: Union[dict, list] = None,
                       timeout: int = None) -> TxResponse:
        """查询 用户合约 接口
        :param contract_name: 合约名
        :param method: 调用合约方法名
        :param params: 调用参数，参数类型为dict
        :param timeout: 超时时间，默认为 3s
        :return: TxResponse
        :raises RequestError: 请求失败
        """
        self.logger.debug("[SDK] begin to QUERY contract, [contract_name:%s]/[method:%s]/[params:%s]",
                          contract_name, method, params)
        tx_id = common.gen_rand_tx_id()
        payload = self.payload_builder.create_query_payload(contract_name, method, params, tx_id)
        response = self.send_request_with_sync_result(payload, timeout=timeout)
        
        return response
    
    def get_tx_request(self, contract_name: str, method: str, params: Union[dict, list] = None,
                       tx_id: str = "") -> TxRequest:
        """
        获取交易请求体
        :param contract_name: 合约名
        :param method: 调用合约方法名
        :param params: 调用参数，参数类型为dict
        :param tx_id: 交易id，如果交易id为空/空字符串，则创建新的tx_id
        :return: Request
        """
        self.logger.debug("[SDK] begin to create TxRequest, [contract_name:%s]/[method:%s]/[tx_id:%s]/[params:%s]",
                          contract_name, method, tx_id, params)
        if not tx_id:
            tx_id = common.gen_rand_tx_id()
        
        pairs = common.params_map_kvpairs(params)
        payload = self.payload_builder.create_invoke_payload(contract_name, method, pairs, tx_id)
        
        return self._generate_tx_request(payload)
    
    def send_tx_request(self, tx_request, timeout=None, with_sync_result=None) -> TxResponse:
        """发送请求
        :param tx_request: 请求体
        :param timeout: 超时时间
        :param with_sync_result: 是否同步交易执行结果。如果不同步，返回tx_id，供异步查询; 同步则循环等待，返回交易的执行结果。
        :return: Response
        :raises RequestError: 请求失败
        """
        response = self._get_client().SendRequest(tx_request, timeout=timeout)
        
        # 判断结果是否正确
        if response.code == TxStatusCode.SUCCESS:
            if with_sync_result:
                response = self.get_sync_result(tx_request.payload.tx_id)
            return response
        else:
            raise RequestError(err_code=response.code, err_msg=TxStatusCode.Name(response.code) + response.message)
    
