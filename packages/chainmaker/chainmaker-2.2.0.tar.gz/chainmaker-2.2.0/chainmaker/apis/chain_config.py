#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# @FileName     :   chain_config.py
# @Function     :   ChainMaker 链配置接口
from typing import List

from chainmaker.apis.base_client import BaseClient
from chainmaker.keys import SystemContractNames, ChainConfigMethods
from chainmaker.exceptions import InvalidParametersError
from chainmaker.protos.accesscontrol import policy_pb2
from chainmaker.protos.common.request_pb2 import Payload
from chainmaker.protos.config.chain_config_pb2 import ChainConfig
from chainmaker.keys import AddrType, ParamKeys, Rule


class ChainConfigMixIn(BaseClient):
    
    def get_chain_config(self) -> ChainConfig:
        """查询 chain config
        :return: ChainConfig
        :raises RequestError: 请求失败
        """
        # contract_name = SystemContract.CHAIN_CONFIG
        # method = "GET_CHAIN_CONFIG"
        self.logger.debug("[SDK] begin to get chain config")
        payload = self.payload_builder.create_query_payload(SystemContractNames.CHAIN_CONFIG, ChainConfigMethods.GET_CHAIN_CONFIG)
        response = self.send_request_with_sync_result(payload)
        
        data = response.contract_result.result
        chain_config = ChainConfig()
        chain_config.ParseFromString(data)
        
        return chain_config
    
    def get_chain_config_by_block_height(self, block_height: int) -> ChainConfig:
        """根据指定区块高度查询最近链配置
        如果当前区块就是配置块，直接返回当前区块的链配置
        :param block_height: 块高
        :return: ChainConfig
        :raises RequestError: 请求失败
        """
        self.logger.debug("[SDK] begin to get chain config by block height [%d]", block_height)
        params = {ParamKeys.block_height: str(block_height)}
        payload = self.payload_builder.create_query_payload(SystemContractNames.CHAIN_CONFIG,
                                                            ChainConfigMethods.GET_CHAIN_CONFIG_AT, params)
        response = self.send_request_with_sync_result(payload)
        
        data = response.contract_result.result
        chain_config = ChainConfig()
        chain_config.ParseFromString(data)
        
        return chain_config
    
    def get_chain_config_sequence(self) -> int:
        """查询最新链配置序号Sequence
        :return: 最新配置序号
        :raises RequestError: 请求失败
        """
        self.logger.debug("[SDK] begin to get chain config sequence")
        chain_config = self.get_chain_config()
        return int(chain_config.sequence)
    
    def sign_chain_config_payload(self, payload_bytes) -> Payload:
        """对链配置的payload 进行签名
        如果当前区块就是配置块，直接返回当前区块的链配置
        :param payload_bytes: payload.SerializeToString() 序列化后的payload bytes数据
        :return: 签名的背书
        :raises
        """
        return self.user.endorse(payload_bytes)
    
    def send_chain_config_update_request(self, payload: Payload, endorsers: list, timeout: int = None,
                                         with_sync_result: bool = True): 
        return self.send_request_with_sync_result(payload, endorsers=endorsers, timeout=timeout, with_sync_result=with_sync_result)
    
    def create_chain_config_core_update_payload(self, tx_scheduler_timeout: int = None,
                                                tx_scheduler_validate_timeout: int = None) -> Payload:
        """更新Core模块待签名payload生成
        :param tx_scheduler_timeout: 交易调度器从交易池拿到交易后, 进行调度的时间，其值范围为[0, 60]，若无需修改，请置为-1
        :param tx_scheduler_validate_timeout: 交易调度器从区块中拿到交易后, 进行验证的超时时间，其值范围为[0, 60]，若无需修改，请置为-1
        :return: request_pb2.SystemContractPayload
        :raises InvalidParametersError: 无效参数
        """
        self.logger.debug("[SDK] begin to create [CoreUpdate] to be signed payload")
        
        if tx_scheduler_timeout and tx_scheduler_timeout > 60:
            raise InvalidParametersError("[tx_scheduler_timeout] should be [0,60]")
        if tx_scheduler_validate_timeout and tx_scheduler_validate_timeout > 60:
            raise InvalidParametersError("[tx_scheduler_validate_timeout] should be [0,60]")
        
        if tx_scheduler_timeout < 0 and tx_scheduler_validate_timeout < 0:
            raise InvalidParametersError("update nothing")
        
        seq = self.get_chain_config_sequence()
        params = {}
        if tx_scheduler_timeout:
            params[ParamKeys.tx_scheduler_timeout] = str(tx_scheduler_timeout)
        if tx_scheduler_validate_timeout:
            params[ParamKeys.tx_scheduler_validate_timeout] = str(tx_scheduler_validate_timeout)
        
        return self.payload_builder.create_invoke_payload(SystemContractNames.CHAIN_CONFIG, ChainConfigMethods.CORE_UPDATE,
                                                          params, seq=seq + 1)
    
    def create_chain_config_block_update_payload(self, tx_timestamp_verify: bool = None, tx_timeout: int = None,
                                                 block_tx_capacity: int = None, block_size: int = None,
                                                 block_interval: int = None, tx_parameter_size=None) -> Payload:
        """更新区块生成模块待签名payload生成
        :param tx_timestamp_verify: 是否需要开启交易时间戳校验
        :param tx_timeout: 交易时间戳的过期时间(秒)，其值范围为[600, +∞)（若无需修改，请置为-1）
        :param block_tx_capacity: 区块中最大交易数，其值范围为(0, +∞]（若无需修改，请置为-1）
        :param block_size: 区块最大限制，单位MB，其值范围为(0, +∞]（若无需修改，请置为-1）
        :param block_interval: 出块间隔，单位:ms，其值范围为[10, +∞]（若无需修改，请置为-1）
        :param tx_parameter_size: 交易参数大小
        :return: request_pb2.SystemContractPayload
        :raises InvalidParametersError: 无效参数
        """
        self.logger.debug("[SDK] begin to create [BlockUpdate] to be signed payload")
        if tx_timestamp_verify is False:
            tx_timestamp_verify = "false"
        if tx_timestamp_verify is True:
            tx_timestamp_verify = "true"
        
        if tx_timeout and tx_timeout < 600:
            raise InvalidParametersError("[tx_timeout] should be [600, +∞)")
        if block_tx_capacity and block_tx_capacity < 1:
            raise InvalidParametersError("[block_tx_capacity] should be (0, +∞]")
        if block_size and block_size < 1:
            raise InvalidParametersError("[block_size] should be (0, +∞]")
        if block_interval and block_interval < 10:
            raise InvalidParametersError("[block_interval] should be [10, +∞]")
        if tx_parameter_size and tx_parameter_size < 1:
            raise InvalidParametersError("[tx_parameter_size] should be (0, +∞]")
        
        seq = self.get_chain_config_sequence()
        params = {}
        
        if tx_timestamp_verify is not None:
            params[ParamKeys.tx_timestamp_verify] = str(tx_timestamp_verify)
        if tx_timeout:
            params[ParamKeys.tx_timeout] = str(tx_timeout)
        if block_tx_capacity:
            params[ParamKeys.block_tx_capacity] = str(block_tx_capacity)
        if block_size:
            params[ParamKeys.block_size] = str(block_size)
        if block_interval:
            params[ParamKeys.block_interval] = str(block_interval)
        if tx_parameter_size:
            params[ParamKeys.tx_parameter_size] = str(tx_parameter_size)
        
        return self.payload_builder.create_invoke_payload(SystemContractNames.CHAIN_CONFIG, ChainConfigMethods.BLOCK_UPDATE,
                                                          params, seq=seq + 1)
    
    def create_chain_config_trust_root_add_payload(self, trust_root_org_id: str,
                                                   trust_root_crts: List[str]) -> Payload:
        """添加信任组织根证书待签名payload生成
        :param str trust_root_org_id: 组织Id  eg. 'wx-or5.chainmaker.org'
        :param List[str] trust_root_crts: 根证书文件内容列表
           eg. [open('./testdata/crypto-config/wx-org5.chainmaker.org/ca/ca.crt').read()]
        :return: Payload
        :raises RequestError: 无效参数
        """
        self.logger.debug("[SDK] begin to create [TrustRootAdd] to be signed payload")
        seq = self.get_chain_config_sequence()
        params = {
            ParamKeys.org_id: str(trust_root_org_id),
            ParamKeys.root: ','.join(trust_root_crts)
        }
        return self.payload_builder.create_invoke_payload(SystemContractNames.CHAIN_CONFIG, ChainConfigMethods.TRUST_ROOT_ADD,
                                                          params, seq=seq + 1)
    
    def create_chain_config_trust_root_update_payload(self, trust_root_org_id: str,
                                                      trust_root_crts: List[str]) -> Payload:
        """更新信任组织根证书待签名payload生成
        :param str trust_root_org_id: 组织Id
        :param List[str] trust_root_crts: 根证书内容列表
        :return: Payload
        :raises RequestError: 无效参数
        """
        self.logger.debug("[SDK] begin to create [TrustRootUpdate] to be signed payload")
        
        seq = self.get_chain_config_sequence()
        params = {
            ParamKeys.org_id: str(trust_root_org_id),
            ParamKeys.root: ','.join(trust_root_crts)
        }
        return self.payload_builder.create_invoke_payload(SystemContractNames.CHAIN_CONFIG, ChainConfigMethods.TRUST_ROOT_UPDATE,
                                                          params, seq=seq + 1)
    
    def create_chain_config_trust_root_delete_payload(self, trust_root_org_id) -> Payload:
        """删除信任组织根证书待签名payload生成
        :param trust_root_org_id: 组织Id
        :return: request_pb2.SystemContractPayload
        :raises InvalidParametersError: 无效参数
        """
        self.logger.debug("[SDK] begin to create [TrustRootDelete] to be signed payload")
        
        seq = self.get_chain_config_sequence()
        params = {
            ParamKeys.org_id: str(trust_root_org_id),
        }
        return self.payload_builder.create_invoke_payload(SystemContractNames.CHAIN_CONFIG, ChainConfigMethods.TRUST_ROOT_DELETE,
                                                          params, seq=seq + 1)
    
    def create_chain_config_trust_member_add_payload(self, trust_member_org_id: str, trust_member_node_id: str,
                                                     trust_member_info: str, trust_member_role: str,
                                                     ) -> Payload: 
        """
        生成添加三方TRUST_ROOT待签名Payload
        :param trust_member_org_id: 组织ID
        :param trust_member_node_id: 节点ID
        :param trust_member_info: 节点信息
        :param trust_member_role: 节点角色
        :return: 待签名Payload
        :raises InvalidParametersError: 无效参数
        """
        self.logger.debug("[SDK] begin to create [TrustMemberAdd] to be signed payload")
        seq = self.get_chain_config_sequence()
        params = {
            ParamKeys.org_id: trust_member_org_id,
            ParamKeys.node_id: trust_member_node_id,
            ParamKeys.member_info: trust_member_info,
            ParamKeys.role: trust_member_role,
        }
        return self.payload_builder.create_invoke_payload(SystemContractNames.CHAIN_CONFIG, ChainConfigMethods.TRUST_MEMBER_ADD,
                                                          params, seq=seq + 1)
    
    def create_chain_config_trust_member_delete_payload(self, trust_member_info: str) -> Payload: 
        """
        生成删除三方TRUST_ROOT待签名Payload
        :param trust_member_info: 节点证书信息
        :return: 待签名Payload
        :raises InvalidParametersError: 无效参数
        """
        self.logger.debug("[SDK] begin to create [TrustMemberDelete] to be signed payload")
        seq = self.get_chain_config_sequence()
        params = {
            ParamKeys.member_info: trust_member_info,
        }
        return self.payload_builder.create_invoke_payload(SystemContractNames.CHAIN_CONFIG,
                                                          ChainConfigMethods.TRUST_MEMBER_DELETE, params, seq=seq + 1)
    
    def create_chain_config_permission_add_payload(self, permission_resource_name, policy) -> Payload:
        """添加权限配置待签名payload生成
        :param permission_resource_name: 权限名
        :param policy: 权限规则
        :return: request_pb2.SystemContractPayload
        :raises InvalidParametersError: 无效参数
        """
        self.logger.debug("[SDK] begin to create [PermissionAdd] to be signed payload")
        seq = self.get_chain_config_sequence()
        params = {
            permission_resource_name: policy.SerializeToString(),
        }
        return self.payload_builder.create_invoke_payload(SystemContractNames.CHAIN_CONFIG, ChainConfigMethods.PERMISSION_ADD,
                                                          params, seq=seq + 1)
    
    def create_chain_config_permission_update_payload(self, permission_resource_name,
                                                      policy: policy_pb2.Policy) -> Payload:  # todo policy->dict
        """更新权限配置待签名payload生成
        :param permission_resource_name: 权限名
        :param policy: 权限规则
        :return: request_pb2.SystemContractPayload
        :raises InvalidParametersError: 无效参数
        """
        self.logger.debug("[SDK] begin to create [PermissionUpdate] to be signed payload")
        
        seq = self.get_chain_config_sequence()
        params = {
            permission_resource_name: policy.SerializeToString(),
        }
        return self.payload_builder.create_invoke_payload(SystemContractNames.CHAIN_CONFIG, ChainConfigMethods.PERMISSION_UPDATE,
                                                          params, seq=seq + 1)
    
    def create_chain_config_permission_delete_payload(self, permission_resource_name) -> Payload:
        """删除权限配置待签名payload生成
        :param permission_resource_name: 权限名
        :return: request_pb2.SystemContractPayload
        :raises InvalidParametersError: 无效参数
        """
        self.logger.debug("[SDK] begin to create [PermissionDelete] to be signed payload")
        seq = self.get_chain_config_sequence()
        params = {
            permission_resource_name: "",
        }
        return self.payload_builder.create_invoke_payload(SystemContractNames.CHAIN_CONFIG, ChainConfigMethods.PERMISSION_DELETE,
                                                          params, seq=seq + 1)
    
    def create_chain_config_consensus_node_id_add_payload(self, node_org_id: str,
                                                          node_ids: list) -> Payload:
        """添加共识节点地址待签名payload生成
        :param node_org_id: 节点组织Id eg. 'wx-org5.chainmaker.org'
        :param node_ids: 节点Id列表 eg. ['QmcQHCuAXaFkbcsPUj7e37hXXfZ9DdN7bozseo5oX4qiC4']
        :return: request_pb2.SystemContractPayload
        :raises InvalidParametersError: 无效参数
        """
        self.logger.debug("[SDK] begin to create [ConsensusNodeAddrAdd] to be signed payload")
        seq = self.get_chain_config_sequence()
        params = {
            ParamKeys.org_id: node_org_id,
            ParamKeys.node_ids: ",".join(node_ids),
        }
        return self.payload_builder.create_invoke_payload(SystemContractNames.CHAIN_CONFIG, ChainConfigMethods.NODE_ID_ADD,
                                                          params, seq=seq + 1)
    
    def create_chain_config_consensus_node_id_update_payload(self, node_org_id: str, node_old_id: str,
                                                             node_new_id: str) -> Payload:
        """更新共识节点地址待签名payload生成
        :param node_org_id: 节点组织Id
        :param node_old_id: 节点原Id
        :param node_new_id: 节点新Id
        :return: request_pb2.SystemContractPayload
        :raises InvalidParametersError: 无效参数
        """
        self.logger.debug("[SDK] begin to create [ConsensusNodeAddrUpdate] to be signed payload")
        seq = self.get_chain_config_sequence()
        params = {
            ParamKeys.org_id: node_org_id,
            ParamKeys.node_id: node_old_id,
            ParamKeys.new_node_id: node_new_id,
        }
        return self.payload_builder.create_invoke_payload(SystemContractNames.CHAIN_CONFIG, ChainConfigMethods.NODE_ID_UPDATE,
                                                          params, seq=seq + 1)
    
    def create_chain_config_consensus_node_id_delete_payload(self, node_org_id: str,
                                                             node_id: str) -> Payload:
        """删除共识节点地址待签名payload生成
        :param node_org_id: 节点组织Id
        :param node_id: 节点Id
        :return: request_pb2.SystemContractPayload
        :raises InvalidParametersError: 无效参数
        """
        self.logger.debug("[SDK] begin to create [ConsensusNodeAddrDelete] to be signed payload")
        
        seq = self.get_chain_config_sequence()
        params = {
            ParamKeys.org_id: node_org_id,
            ParamKeys.node_id: node_id
        }
        return self.payload_builder.create_invoke_payload(SystemContractNames.CHAIN_CONFIG, ChainConfigMethods.NODE_ID_DELETE,
                                                          params, seq=seq + 1)
    
    def create_chain_config_consensus_node_org_add_payload(self, node_org_id: str,
                                                           node_ids: list) -> Payload:
        """添加共识节点待签名payload生成
        :param node_org_id: 节点组织Id
        :param node_ids: 节点Id
        :return: request_pb2.SystemContractPayload
        :raises InvalidParametersError: 无效参数
        """
        self.logger.debug("[SDK] begin to create [ConsensusNodeOrgAdd] to be signed payload")
        
        seq = self.get_chain_config_sequence()
        params = {
            ParamKeys.org_id: node_org_id,
            ParamKeys.node_ids: ",".join(node_ids),
        }
        return self.payload_builder.create_invoke_payload(SystemContractNames.CHAIN_CONFIG, ChainConfigMethods.NODE_ORG_ADD,
                                                          params, seq=seq + 1)
    
    def create_chain_config_consensus_node_org_update_payload(self, node_org_id: str,
                                                              node_ids: list) -> Payload:
        """更新共识节点待签名payload生成
        :param node_org_id: 节点组织Id
        :param node_ids: 节点Id
        :return: request_pb2.SystemContractPayload
        :raises InvalidParametersError: 无效参数
        """
        self.logger.debug("[SDK] begin to create [ConsensusNodeOrgUpdate] to be signed payload")
        seq = self.get_chain_config_sequence()
        params = {
            ParamKeys.org_id: node_org_id,
            ParamKeys.node_ids: ",".join(node_ids),
        }
        return self.payload_builder.create_invoke_payload(SystemContractNames.CHAIN_CONFIG, ChainConfigMethods.NODE_ORG_UPDATE,
                                                          params, seq=seq + 1)
    
    def create_chain_config_consensus_node_org_delete_payload(self, node_org_id) -> Payload:
        """删除共识节点待签名payload生成
        :param node_org_id: 节点组织Id
        :return: request_pb2.SystemContractPayload
        :raises InvalidParametersError: 无效参数
        """
        self.logger.debug("[SDK] begin to create [ConsensusNodeOrgDelete] to be signed payload")
        seq = self.get_chain_config_sequence()
        params = {
            ParamKeys.org_id: node_org_id,
        }
        return self.payload_builder.create_invoke_payload(SystemContractNames.CHAIN_CONFIG, "NODE_ORG_DELETE", params,
                                                          seq=seq + 1)
    
    def create_chain_config_consensus_ext_add_payload(self, params) -> Payload:
        """添加共识扩展字段待签名payload生成
        :param params: 字段key、value对
        :return: request_pb2.SystemContractPayload
        :raises InvalidParametersError: 无效参数
        """
        self.logger.debug("[SDK] begin to create [ConsensusExtAdd] to be signed payload")
        
        seq = self.get_chain_config_sequence()
        return self.payload_builder.create_invoke_payload(SystemContractNames.CHAIN_CONFIG, ChainConfigMethods.CONSENSUS_EXT_ADD,
                                                          params, seq=seq + 1)
    
    def create_chain_config_consensus_ext_update_payload(self, params) -> Payload:
        """更新共识扩展字段待签名payload生成
        :param params: 字段key、value对
        :return: request_pb2.SystemContractPayload
        :raises InvalidParametersError: 无效参数
        """
        self.logger.debug("[SDK] begin to create [ConsensusExtUpdate] to be signed payload")
        
        seq = self.get_chain_config_sequence()
        return self.payload_builder.create_invoke_payload(SystemContractNames.CHAIN_CONFIG,
                                                          ChainConfigMethods.CONSENSUS_EXT_UPDATE, params, seq=seq + 1)
    
    def create_chain_config_consensus_ext_delete_payload(self, keys) -> Payload:
        """删除共识扩展字段待签名payload生成
        :param keys: 待删除字段
        :return: request_pb2.SystemContractPayload
        :raises InvalidParametersError: 无效参数
        """
        self.logger.debug("[SDK] begin to create [ConsensusExtDelete] to be signed payload")
        
        seq = self.get_chain_config_sequence()
        params = {k: "" for k in keys}
        return self.payload_builder.create_invoke_payload(SystemContractNames.CHAIN_CONFIG,
                                                          ChainConfigMethods.CONSENSUS_EXT_DELETE, params, seq=seq + 1)
    
    @staticmethod
    def create_policy(rule: Rule, org_list: list = None, role_list: list = None):
        return policy_pb2.Policy(
            rule=rule,
            org_list=org_list,
            role_list=role_list
        )
    
    def create_chain_config_alter_addr_type_payload(self, addr_type: AddrType) -> Payload:
        """
        生成链配置变更地址类型待签名Payload
        :param addr_type: 地址类型
        :return:
        """
        self.logger.debug("[SDK] begin to create [AlterAddrType] to be signed payload")
        addr_type = str(addr_type)
        if addr_type not in ['0', '1', '2']:
            raise ValueError("unknown addr type [%s], only support: 0-ChainMaker; 1-ZXL; 2-ETHEREUM" % addr_type)
        seq = self.get_chain_config_sequence()
        params = {ParamKeys.addr_type: addr_type}
        return self.payload_builder.create_invoke_payload(SystemContractNames.CHAIN_CONFIG, ChainConfigMethods.ALTER_ADDR_TYPE,
                                                          params,
                                                          seq=seq + 1)
    
    def create_chain_config_enable_or_disable_gas_payload(self) -> Payload: 
        self.logger.debug("[SDK] begin to create [EnableOrDisable] to be signed payload")
        seq = self.get_chain_config_sequence()
        return self.payload_builder.create_invoke_payload(SystemContractNames.CHAIN_CONFIG,
                                                          ChainConfigMethods.ENABLE_OR_DISABLE_GAS, params=None, seq=seq + 1)
