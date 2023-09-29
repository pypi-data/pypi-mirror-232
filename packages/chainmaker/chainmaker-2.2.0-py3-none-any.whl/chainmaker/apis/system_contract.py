#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# @FileName     :   system_contract.py
# @Function     :   ChainMaker系统合约(链查询相关)接口
import json
from typing import List, Union

from chainmaker.apis.base_client import BaseClient
from chainmaker.keys import ParamKeys, Defaults
from chainmaker.keys import SystemContractNames, ChainQueryMethods, ContractManageMethods
from chainmaker.protos.common.block_pb2 import BlockHeader, BlockInfo
from chainmaker.protos.common.contract_pb2 import Contract
from chainmaker.protos.common.request_pb2 import Payload
from chainmaker.protos.common.result_pb2 import TxResponse
from chainmaker.protos.common.transaction_pb2 import TransactionInfo, TransactionWithRWSet
from chainmaker.protos.discovery.discovery_pb2 import ChainList, ChainInfo
from chainmaker.protos.store.store_pb2 import BlockWithRWSet
from chainmaker.utils import common
from chainmaker.utils.result_utils import check_response as check_response
from chainmaker.exceptions import ContractFail


class SystemContractMixIn(BaseClient):
    def get_chain_info(self) -> ChainInfo:
        """查询链信息
        :return: ChainInfo
        :raises RequestError: 请求失败
        """
        self.logger.debug('[SDK] begin to GetChainInfo')
        payload = self.payload_builder.create_query_payload(SystemContractNames.CHAIN_QUERY,
                                                            ChainQueryMethods.GET_CHAIN_INFO)
        response = self.send_request(payload)
        data = response.contract_result.result
        chain_info = ChainInfo()
        chain_info.ParseFromString(data)
        return chain_info
    
    def get_tx_by_tx_id(self, tx_id: str) -> TransactionInfo:
        """根据交易ID获取带读写集交易详情
        :param tx_id: 交易ID，类型为字符串
        :return: Result
        :raises RequestError: 请求失败
        """
        self.logger.debug("[SDK] begin to GetTxByTxId, [tx_id:%s]", tx_id)
        
        params = {"txId": tx_id}
        payload = self.payload_builder.create_query_payload(SystemContractNames.CHAIN_QUERY,
                                                            ChainQueryMethods.GET_TX_BY_TX_ID,
                                                            params)
        
        tx_response = self.send_request(payload)
        data = tx_response.contract_result.result
        
        transaction_info = TransactionInfo()
        transaction_info.ParseFromString(data)
        return transaction_info
    
    def get_tx_with_rwset_by_tx_id(self, tx_id: str) -> TransactionWithRWSet:
        """根据交易ID获取带读写集交易详情
        :param tx_id: 交易ID，类型为字符串
        :return: Result
        :raises RequestError: 请求失败
        """
        self.logger.debug("[SDK] begin to GetTxWithRWSetByTxId, [tx_id:%s]", tx_id)
        params = {"txId": tx_id, "withRWSet": "true"}
        payload = self.payload_builder.create_query_payload(SystemContractNames.CHAIN_QUERY,
                                                            ChainQueryMethods.GET_TX_BY_TX_ID,
                                                            params)
        
        response = self.send_request(payload)
        
        data = response.contract_result.result
        transaction_info = TransactionWithRWSet()
        transaction_info.ParseFromString(data)
        
        return transaction_info
    
    def get_block_by_height(self, block_height: int, with_rw_set: bool = False) -> BlockInfo:
        """根据区块高度查询区块详情
        :param block_height: 区块高度
        :param with_rw_set: 是否返回读写集数据, 默认不返回。
        :return: 区块信息BlockInfo对象
        :raises RequestError: 请求失败，块已归档是抛出ContractFile
        """
        self.logger.debug("[SDK] begin to GetBlockByHeight, [block_height:%d]/[with_rw_set:%s]", block_height,
                          with_rw_set)
        
        params = {"blockHeight": str(block_height),
                  "withRWSet": common.bool_to_str(with_rw_set),
                  }
        payload = self.payload_builder.create_query_payload(SystemContractNames.CHAIN_QUERY,
                                                            ChainQueryMethods.GET_BLOCK_BY_HEIGHT, params)
        
        response = self.send_request(payload)
        
        data = response.contract_result.result
        res = BlockInfo()
        
        res.ParseFromString(data)
        
        return res
    
    def get_block_by_hash(self, block_hash: str, with_rw_set: bool = False) -> BlockInfo:
        """根据区块 Hash 查询区块详情
        :param block_hash: 区块Hash, 二进制hash.hex()值，
                           如果拿到的block_hash字符串是base64值, 需要用 base64.b64decode(block_hash).hex()
        :param with_rw_set: 是否返回读写集数据
        :return: BlockInfo
        :raises RequestError: 请求失败
        """
        self.logger.debug("[SDK] begin to GetBlockByHash, [block_hash:%s]/[with_rw_set:%s]", block_hash, with_rw_set)
        
        params = {ParamKeys.blockHash: str(block_hash),
                  ParamKeys.withRWSet: common.bool_to_str(with_rw_set)}
        payload = self.payload_builder.create_query_payload(SystemContractNames.CHAIN_QUERY,
                                                            ChainQueryMethods.GET_BLOCK_BY_HASH,
                                                            params)
        
        response = self.send_request(payload)
        
        data = response.contract_result.result
        res = BlockInfo()
        res.ParseFromString(data)
        return res
    
    def get_block_by_tx_id(self, tx_id: str, with_rw_set: bool = False) -> BlockInfo:
        """根据交易id 查询交易所在区块详情

        :param tx_id: 交易ID
        :param with_rw_set: 是否返回读写集数据

        :return: BlockInfo

        :raises RequestError: 请求失败
        """
        self.logger.debug("[SDK] begin to GetBlockByTxId, [tx_id:%s]/[with_rw_set:%s]", tx_id, with_rw_set)
        
        params = {ParamKeys.txId: str(tx_id),
                  ParamKeys.withRWSet: common.bool_to_str(with_rw_set)}
        payload = self.payload_builder.create_query_payload(SystemContractNames.CHAIN_QUERY,
                                                            ChainQueryMethods.GET_BLOCK_BY_TX_ID,
                                                            params)
        
        response = self.send_request(payload)
        
        data = response.contract_result.result
        res = BlockInfo()
        res.ParseFromString(data)
        return res
    
    def get_last_config_block(self, with_rw_set: bool = False) -> BlockInfo:
        """查询最新的配置块
        :param with_rw_set: 是否返回读写集数据
        :return: BlockInfo
        :raises RequestError: 请求失败
        """
        self.logger.debug("[SDK] begin to GetLastConfigBlock, [with_rw_set:%s]", with_rw_set)
        
        params = {ParamKeys.withRWSet: common.bool_to_str(with_rw_set)}
        payload = self.payload_builder.create_query_payload(SystemContractNames.CHAIN_QUERY,
                                                            ChainQueryMethods.GET_LAST_CONFIG_BLOCK, params)
        response = self.send_request(payload)
        
        data = response.contract_result.result
        res = BlockInfo()
        res.ParseFromString(data)
        return res
    
    def get_last_block(self, with_rw_set: bool = False) -> BlockInfo:
        """查询最新的块
        :param with_rw_set: 是否返回读写集数据
        :return: BlockInfo
        :raises RequestError: 请求失败
        """
        self.logger.debug("[SDK] begin to GetLastBlock, [with_rw_set:%s]", with_rw_set)
        
        params = {ParamKeys.withRWSet: common.bool_to_str(with_rw_set)}
        payload = self.payload_builder.create_query_payload(SystemContractNames.CHAIN_QUERY,
                                                            ChainQueryMethods.GET_LAST_BLOCK,
                                                            params)
        
        response = self.send_request(payload)
        
        data = response.contract_result.result
        block_info = BlockInfo()
        block_info.ParseFromString(data)
        return block_info
    
    def get_node_chain_list(self) -> ChainList:
        """查询节点加入的链信息，返回chain id 清单
        :return: 链列表
        :raises RequestError: 请求失败
        """
        self.logger.debug("[SDK] begin to GetNodeChainList")
        
        payload = self.payload_builder.create_query_payload(SystemContractNames.CHAIN_QUERY,
                                                            ChainQueryMethods.GET_NODE_CHAIN_LIST)
        response = self.send_request(payload)
        data = response.contract_result.result
        chain_list = ChainList()
        chain_list.ParseFromString(data)
        return chain_list
    
    def get_full_block_by_height(self, block_height: int) -> BlockWithRWSet:
        """根据区块高度查询区块所有数据
        :param block_height: 区块高度
        :return: BlockInfo
        :raises RequestError: 请求失败
        """
        self.logger.debug("[SDK] begin to GetFullBlockHeight, [block_height:%d]", block_height)
        
        params = {ParamKeys.blockHeight: str(block_height)}
        payload = self.payload_builder.create_query_payload(SystemContractNames.CHAIN_QUERY,
                                                            ChainQueryMethods.GET_FULL_BLOCK_BY_HEIGHT, params)
        response = self.send_request(payload)
        
        block_with_rw_set = BlockWithRWSet()
        block_with_rw_set.ParseFromString(response.contract_result.result)
        return block_with_rw_set
    
    def get_block_height_by_tx_id(self, tx_id: str) -> int:
        """根据交易ID查询区块高度
        :param tx_id: 交易ID
        :return: 区块高度
        :raises RequestError: 请求失败
        """
        self.logger.debug("[SDK] begin to GetBlockHeightByTxId, [tx_id:%s]", tx_id)
        
        params = {ParamKeys.txId: tx_id}
        payload = self.payload_builder.create_query_payload(SystemContractNames.CHAIN_QUERY,
                                                            ChainQueryMethods.GET_BLOCK_HEIGHT_BY_TX_ID, params)
        response = self.send_request(payload)
        
        data = response.contract_result.result
        
        return int(data)
    
    def get_block_height_by_hash(self, block_hash: str) -> int:
        """根据区块hash查询区块高度
        :param block_hash: 区块Hash 二进制hash.hex()值,
               如果拿到的block_hash字符串是base64值, 需要用 base64.b64decode(block_hash).hex()
        :return: 区块高度
        :raises RequestError: 请求失败
        """
        self.logger.debug("[SDK] begin to GetBlockHeightByHash, [block_hash:%s]", block_hash)
        
        params = {ParamKeys.blockHash: block_hash}
        payload = self.payload_builder.create_query_payload(SystemContractNames.CHAIN_QUERY,
                                                            ChainQueryMethods.GET_BLOCK_HEIGHT_BY_HASH, params)
        response = self.send_request(payload)
        data = response.contract_result.result
        
        return int(data)
    
    def get_archived_block_height(self) -> int:
        """查询已归档的区块高度
        :return: 区块高度
        :raises RequestError: 请求失败
        """
        self.logger.debug("[SDK] begin to GetArchiveBlockHeight")
        payload = self.payload_builder.create_query_payload(SystemContractNames.CHAIN_QUERY,
                                                            ChainQueryMethods.GET_ARCHIVED_BLOCK_HEIGHT)
        response = self.send_request(payload)
        self.logger.debug('Response: %s', response)
        data = response.contract_result.result
        
        return int(data)
    
    def get_block_height(self, tx_id: str = None, block_hash: str = None) -> int:  # todo
        """
        根据交易id或区块hash查询区块高度
        :param tx_id: 交易ID
        :param block_hash: 区块hash
        :return: 区块高度
        """
        if tx_id is None and block_hash is None:
            raise ValueError('tx_id和block_hash最少需要其中一个')
        return self.get_block_height_by_tx_id(tx_id) if tx_id else self.get_block_height_by_hash(block_hash)
    
    def get_current_block_height(self) -> int:
        """
        查询当前区块高度
        :return: 区块高度
        """
        self.logger.debug("[SDK] begin to GetCurrentBlockHeight")
        return self.get_last_block(with_rw_set=False).block.header.block_height
    
    def get_block_header_by_height(self, block_height) -> BlockHeader:
        """
        根据高度获取区块头
        :param block_height: 区块高度
        :return: 区块头
        """
        self.logger.debug("[SDK] begin to GetBlockHeaderByHeight, [block_height:%d]", block_height)
        
        return self.get_block_by_height(block_height).block.header
    
    def invoke_system_contract(self, contract_name: str, method: str, params: dict = None,
                               tx_id: str = "", timeout: int = None, with_sync_result=False) -> TxResponse:
        self.logger.debug("[SDK] begin to InvokeSystemContract, [contract_name:%s]/[method:%s]/[params:%s]",
                          contract_name, method, params)
        if timeout is None:
            timeout = Defaults.REQUEST_TIMEOUT
        payload = self.payload_builder.create_invoke_payload(contract_name, method, params, tx_id)
        response = self.send_request_with_sync_result(payload, timeout=timeout, with_sync_result=with_sync_result)
        return response
    
    def query_system_contract(self, contract_name: str, method: str, params: Union[dict, list] = None,
                              tx_id: str = "", timeout: int = None) -> TxResponse:
        self.logger.debug("[SDK] begin to QuerySystemContract, [contract_name:%s]/[method:%s]/[params:%s]",
                          contract_name, method, params)
        if timeout is None:
            timeout = Defaults.REQUEST_TIMEOUT
        payload = self.payload_builder.create_query_payload(contract_name, method, params)
        response = self.send_request(payload, timeout=timeout)
        return response
    
    def get_merkle_path_by_tx_id(self, tx_id: str) -> bytes:
        """
        根据交易ID获取Merkle树路径
        :param tx_id: 交易ID
        :return: Merkle树路径
        """
        self.logger.debug("[SDK] begin to GetMerklePathByTxId, [tx_id:%s]", tx_id)
        
        params = {ParamKeys.txId: tx_id}
        payload = self.payload_builder.create_query_payload(SystemContractNames.CHAIN_QUERY,
                                                            ChainQueryMethods.GET_MERKLE_PATH_BY_TX_ID, params)
        response = self.send_request(payload)
        return response.contract_result.result
    
    def _create_native_contract_access_payload(self, method: str, access_contract_list: List[str]) -> Payload:
        """
        内部方法: 生成原生合约访问待签名Payload
        :param method: 合约方法
        :param access_contract_list: 访问合约列表
        :return: 待签名Payload
        """
        params = {ParamKeys.NATIVE_CONTRACT_NAME: json.dumps(access_contract_list)}
        
        payload = self.payload_builder.create_invoke_payload(SystemContractNames.CONTRACT_MANAGE, method, params)
        
        return payload
    
    def create_native_contract_access_grant_payload(self, grant_contract_list: List[str]) -> Payload:
        """
        生成系统合约授权访问待签名Payload
        :param List[str] grant_contract_list: 授予权限的访问系统合约名称列表 # TODO 确认 合约状态必须是FROZEN
        :return: 待签名Payload
        """
        self.logger.debug("[SDK] begin to create [NativeContractAccess] to be signed payload")
        
        return self._create_native_contract_access_payload(ContractManageMethods.GRANT_CONTRACT_ACCESS,
                                                           grant_contract_list)
    
    def create_native_contract_access_revoke_payload(self, revoke_contract_list: List[str]) -> Payload:
        """
        生成原生合约吊销授权访问待签名Payload
        :param revoke_contract_list: 吊销授予权限的访问合约列表
        :return: 待签名Payload
        """
        self.logger.debug("[SDK] begin to create [NativeContractRevoke] to be signed payload")
        return self._create_native_contract_access_payload(ContractManageMethods.REVOKE_CONTRACT_ACCESS,
                                                           revoke_contract_list)
    
    def _parse_contract(self, contract_data: dict) -> Contract:
        """
        将二进制格式合约数据解析成合约结构体
        :param dict contract_data: 合约数据
        :return: 合约Contract对象
        :raise: 当数据不是JSON格式时，抛出json.decoder.JSONDecodeError
        """
       
        if contract_data.get('creator', {}).get('member_info'):
            contract_data['creator']['member_info'] = contract_data['creator']['member_info'].encode()
        contract = Contract(**contract_data)
        return contract
    
    def get_contract_info(self, contract_name: str) -> Union[Contract, None]:
        """
        获取合约信息
        :param contract_name: 用户合约名称
        :return: 合约存在则返回合约信息Contract对象，合约不存在抛出ContractFail
        :raise: RequestError: 请求出错
        :raise: AssertionError: 响应code不为0,检查响应时抛出断言失败
        :raise: 当数据不是JSON格式时，抛出json.decoder.JSONDecodeError
        """
        self.logger.debug("[SDK] begin to GetContractInfo, [contract_name:%s]", contract_name)
        
        params = {ParamKeys.CONTRACT_NAME: contract_name}
        
        payload = self.payload_builder.create_query_payload(SystemContractNames.CONTRACT_MANAGE,
                                                            ContractManageMethods.GET_CONTRACT_INFO, params)
        try:
            tx_response = self.send_request(payload)
        except ContractFail:
            return None
            
        check_response(tx_response)
        data = tx_response.contract_result.result
        contract_data = json.loads(data)
        return self._parse_contract(contract_data)
    
    def get_contract_list(self) -> List[Contract]:
        """
        获取合约列表
        :return: 合约Contract对象列表
        :raise: RequestError: 请求出错
        :raise: AssertionError: 响应code不为0,检查响应时抛出断言失败
        :raise: 当数据不是JSON格式时，抛出json.decoder.JSONDecodeError
        """
        self.logger.debug("[SDK] begin to GetContractList")
        payload = self.payload_builder.create_query_payload(SystemContractNames.CONTRACT_MANAGE,
                                                            ContractManageMethods.GET_CONTRACT_LIST)
        
        response = self.send_request(payload)
        contract_list = json.loads(response.contract_result.result)
        contracts = [self._parse_contract(contract_data) for contract_data in contract_list]
        return contracts
    
    def get_disabled_native_contract_list(self) -> List[str]:
        """
        获取禁用系统合约名称列表
        :return: 禁用合约名称列表
        """
        self.logger.debug("[SDK] begin to GetDisabledNativeContractList")
        payload = self.payload_builder.create_query_payload(SystemContractNames.CONTRACT_MANAGE,
                                                            ContractManageMethods.GET_DISABLED_CONTRACT_LIST)
        
        response = self.send_request(payload)
        return json.loads(response.contract_result.result) or []
