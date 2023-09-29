#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# @FileName     :   base_client.py
# @Function     :   ChainMaker链客户端基类

import logging
from typing import List, Union, Callable

from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import ec, rsa

from chainmaker.keys import Defaults, AuthType, RuntimeType, AddrType, RechargeGasItem, ArchiveConfig, RPCClientConfig, PKCS11Config
from chainmaker.payload import PayloadBuilder
from chainmaker.protos.accesscontrol.policy_pb2 import Policy
from chainmaker.protos.api.rpc_node_pb2_grpc import RpcNodeStub
from chainmaker.protos.common.block_pb2 import BlockHeader, BlockInfo
from chainmaker.protos.common.contract_pb2 import Contract
from chainmaker.protos.common.request_pb2 import Payload, TxRequest, EndorsementEntry
from chainmaker.protos.common.result_pb2 import TxResponse, Result
from chainmaker.protos.common.transaction_pb2 import TransactionWithRWSet, TransactionInfo
from chainmaker.protos.config.chain_config_pb2 import ChainConfig
from chainmaker.protos.discovery.discovery_pb2 import ChainList, ChainInfo
from chainmaker.protos.store.store_pb2 import BlockWithRWSet
from chainmaker.protos.syscontract.multi_sign_pb2 import MultiSignInfo
from chainmaker.user import User


class BaseClient(object):
    # common config
    logger: logging.Logger
    conn: List[List[RpcNodeStub]]
    
    chain_id: str
    org_id: str
    user_crt_bytes: bytes
    user_crt: x509.Certificate
    private_key: Union[ec.EllipticCurvePrivateKey, rsa.RSAPrivateKey]
    
    # cert hash config
    enabled_crt_hash: bool = Defaults.ENABLED_CRT_HASH
    user_crt_hash: bytes = b''  # 对应的user.sign_cert_hash
    
    # cert alias config
    enabled_alias: bool = Defaults.ENABLED_ALIAS
    alias: str = None
    
    # archive config
    archive_config: ArchiveConfig
    
    # grpc client config
    # rpc_client_config: dict = dict(max_send_message_size=Defaults.GRPC_MAX_SEND_MESSAGE_LENGTH,
    #                                max_receive_message_size=Defaults.GRPC_MAX_RECEIVE_MESSAGE_LENGTH)
    #
    rpc_client_config: RPCClientConfig = RPCClientConfig(Defaults.GRPC_MAX_SEND_MESSAGE_LENGTH, Defaults.GRPC_MAX_RECEIVE_MESSAGE_LENGTH)
    
    public_key: Union[ec.EllipticCurvePublicKey, rsa.RSAPublicKey]
    pk_bytes: bytes
    hash_type: str = Defaults.HASH_TYPE
    auth_type: AuthType = Defaults.AUTH_TYPE
    
    # retry config
    retry_limit: int = Defaults.RETRY_LIMIT
    retry_interval: int = Defaults.RETRY_LIMIT
    
    pkcs11_config: PKCS11Config
    
    # additional
    request_timeout: int = Defaults.REQUEST_TIMEOUT
    tx_check_interval: int = Defaults.TX_CHECK_INTERVAL
    tx_check_timeout: int = Defaults.TX_CHECK_TIMEOUT
    with_sync_result: bool = Defaults.WITH_SYNC_RESULT
    endorse_users: List[User] = Defaults.ENDORSE_USERS
    
    user: User
    payload_builder: PayloadBuilder
    
    def _get_client(self) -> RpcNodeStub: ...
    
    def _generate_tx_request(self, payload: Payload)->TxRequest:
        """
        生成交易请求
        :param payload:
        :return:
        """
    
    def get_sync_result(self, tx_id: str, intervel: int = None, timeout: int = None) -> Result:
        """
        轮询获取交易结果
        :param tx_id: 交易ID
        :return: 交易结果
        """
    
    def send_request(self, payload: Payload, endorsers: List[EndorsementEntry] = None, timeout: int = None)->TxResponse:
        """
        发送请求
        :param payload:
        :param endorsers:
        :param timeout:
        :return:
        """
    def send_request_with_sync_result(self, payload: Payload, endorsers: List[EndorsementEntry] = None, timeout: int = None,
                                      with_sync_result: bool = True)->TxResponse:
        """
        发送请求并执行轮询交易结果
        :param payload: 请求数据
        :param timeout: 超时时间
        :param with_sync_result: 是否同步获取交易结果，默认为False
        :param endorsers: 背书配置
        :return: 响应对象
        :raise: RequestError
        :raise: TimeoutError
        """
        
    def send_manage_request(self, payload, endorse_users: List[User]=None, timeout: int=None, with_sync_result: bool=True)->TxResponse:
        """
        发送管理(带背书)请求
        :param payload: 待签名payload
        :param endorse_users: 背书用户
        :param timeout: 超时时间
        :param with_sync_result: 是否同步查询交易结果
        :return: 交易响应
        """
    
    # 用户合约 ----------------------------------------------------------------------------------------------------------
    def create_contract_create_payload(self, contract_name: str, version: str, byte_code_or_file_path: str,
                                       runtime_type: RuntimeType,
                                       params: Union[dict, list]) -> Payload:
        """生成合约创建待签名Payload
        :param str contract_name: 合约名
        :param str version: 合约版本
        :param str byte_code_or_file_path: 合约字节码：可以是字节码；合约文件路径；或者 hex编码字符串；或者 base64编码字符串。
        :param RuntimeType runtime_type: RuntimeType.WASMER
        :param dict params: 合约参数，dict类型，key 和 value 尽量为字符串
        :return: Payload
        :raises ValueError: 如果byte_code不能转成合约字节码将抛出ValueError
        """
    
    def create_contract_upgrade_payload(self, contract_name: str, version: str, byte_code_or_file_path: str,
                                        runtime_type: RuntimeType,
                                        params: Union[dict, list]) -> Payload:
        """生成合约升级待签名Payload
        :param str contract_name: 合约名
        :param str version: 合约版本
        :param str byte_code_or_file_path: 合约字节码：可以是字节码；合约文件路径；或者 hex编码字符串；或者 base64编码字符串。
        :param RuntimeType runtime_type:
            eg. 'INVALID', 'NATIVE', 'WASMER', 'WXVM', 'GASM', 'EVM', 'DOCKER_GO', 'DOCKER_JAVA'
        :param dict params: 合约参数，dict类型，key 和 value 尽量为字符串
        :return: Payload
        :raises ValueError: 如果 byte_code 不能转成合约字节码
        """
    
    def create_contract_freeze_payload(self, contract_name: str) -> Payload:
        """生成合约冻结待签名Payload
        :param str contract_name: 合约名
        :return: Payload
        """
    
    def create_contract_unfreeze_payload(self, contract_name: str) -> Payload:
        """生成合约解冻待签名Payload
        :param str contract_name: 合约名
        :return: Payload
        """
    
    def create_contract_revoke_payload(self, contract_name: str) -> Payload:
        """生成合约吊销待签名Payload
        :param str contract_name: 合约名
        :return: Payload
        """
    
    def sign_contract_manage_payload(self, payload: Payload):
        """对 合约管理的 payload 字节数组进行签名，返回签名后的payload字节数组
        :param Payload payload: 交易 payload
        :return: Payload 的字节数组
        :raises DecodeError: 如果 byte_code 解码失败
        """
    
    def send_contract_manage_request(self, payload: Payload, endorsers: List[EndorsementEntry],
                                     timeout: int, with_sync_result: bool) -> TxResponse:
        """发送合约管理的请求

        :param list endorsers: 背书列表
        :param Payload payload: 请求的 payload
        :param int timeout: 超时时间
        :param bool with_sync_result: 是否同步交易执行结果。如果不同步，返回tx_id，供异步查询; 同步则循环等待，返回交易的执行结果。
        :return: TxResponse
        :raises RequestError: 请求失败
        """
    
    def invoke_contract(self, contract_name: str, method: str, params: Union[dict, list],
                        tx_id: str,
                        timeout: int,
                        with_sync_result: bool) -> TxResponse:
        """调用 用户合约 接口
        :param str contract_name: 合约名
        :param str method: 调用合约方法名
        :param dict params: 调用参数，参数类型为dict
        :param str tx_id: 交易id，如果交易id为空/空字符串，则创建新的tx_id
        :param int timeout: 超时时间，默认为 3s
        :param bool with_sync_result: 是否同步交易执行结果。如果不同步，返回tx_id，供异步查询; 同步则循环等待，返回交易的执行结果。
        :return: TxResponse
        :raises RequestError: 请求失败
        """
    
    def invoke_contract_with_limit(self, contract_name: str, method: str, params: Union[dict, list], tx_id: str,
                                   timeout: int, with_sync_result: bool, gas_limit: int) -> TxResponse:  # TODO Test
        """调用 用户合约 接口
        :param str contract_name: 合约名
        :param str method: 调用合约方法名
        :param dict params: 调用参数，参数类型为dict
        :param str tx_id: 交易id，如果交易id为空/空字符串，则创建新的tx_id
        :param int timeout: 超时时间，默认为 3s
        :param bool with_sync_result: 是否同步交易执行结果。如果不同步，返回tx_id，供异步查询; 同步则循环等待，返回交易的执行结果。
        :param gas_limit: Gas交易限制
        :return: TxResponse
        :raises RequestError: 请求失败
        """
    
    def query_contract(self, contract_name: str, method: str, params: Union[dict, list], timeout: int) -> TxResponse:
        """查询 用户合约 接口
        :param str contract_name: 合约名
        :param str method: 调用合约方法名
        :param dict params: 调用参数，参数类型为dict
        :param int timeout: 超时时间，默认为 3s
        :return: TxResponse
        :raises RequestError: 请求失败
        """
    
    def get_tx_request(self, contract_name: str, method: str, params: Union[dict, list],
                       tx_id: str) -> TxRequest:
        """
        获取交易请求体
        :param str contract_name: 合约名
        :param str method: 调用合约方法名
        :param dict params: 调用参数，参数类型为dict
        :param str tx_id: 交易id，如果交易id为空/空字符串，则创建新的tx_id

        :return: Request

        """
    
    def send_tx_request(self, tx_request, timeout: int, with_sync_result: bool) -> TxResponse:
        """发送交易请求体

        :param tx_request: 请求体
        :param int timeout: 超时时间
        :param bool with_sync_result: 是否同步交易执行结果。如果不同步，返回tx_id，供异步查询; 同步则循环等待，返回交易的执行结果。
        :return: Response
        :raises RequestError: 请求失败
        """
    
    # 系统合约 ----------------------------------------------------------------------------------------------------------
    def get_chain_info(self) -> ChainInfo:
        """查询链信息
        :return: discovery_pb2.ChainInfo
        :raises RequestError: 请求失败
        """
    
    def get_tx_by_tx_id(self, tx_id: str) -> TransactionInfo:
        """根据交易id 查询交易详情
        :param str tx_id: 交易id，类型为字符串
        :return: Result
        :raises RequestError: 请求失败
        """
    
    def get_tx_with_rwset_by_tx_id(self, tx_id: str) -> TransactionWithRWSet:
        """根据交易ID获取带读写集交易详情
        :param tx_id: 交易ID，类型为字符串
        :return: transaction_pb2.Result
        :raises RequestError: 请求失败
        """
    
    def get_block_by_height(self, block_height: int, with_rw_set: bool) -> BlockInfo:
        """根据区块高度查询区块详情
        :param int block_height: 区块高度
        :param bool with_rw_set: 是否返回读写集数据, 默认不返回。
        :return: BlockInfo
        :raises RequestError: 请求失败
        """
    
    def get_block_by_hash(self, block_hash: str, with_rw_set: bool) -> BlockInfo:
        """根据区块 Hash 查询区块详情
        :param str block_hash: 区块Hash
        :param bool with_rw_set: 是否返回读写集数据
        :return: BlockInfo
        :raises RequestError: 请求失败
        """
    
    def get_block_by_tx_id(self, tx_id: str, with_rw_set: bool) -> BlockInfo:
        """根据交易id 查询交易所在区块详情
        :param str tx_id: 交易id
        :param bool with_rw_set: 是否返回读写集数据
        :return: BlockInfo
        :raises RequestError: 请求失败
        """
    
    def get_last_config_block(self, with_rw_set: bool) -> BlockInfo:
        """查询最新的配置块
        :param bool with_rw_set: 是否返回读写集数据
        :return: BlockInfo
        :raises RequestError: 请求失败
        """
    
    def get_last_block(self, with_rw_set: bool) -> BlockInfo:
        """查询最新的块
        :param bool with_rw_set: 是否返回读写集数据
        :return: BlockInfo
        :raises RequestError: 请求失败
        """
    
    def get_node_chain_list(self) -> ChainList:
        """查询节点加入的链信息，返回chain id 清单
        :return:
        :raises RequestError: 请求失败
        """
    
    def get_full_block_by_height(self, block_height: int) -> BlockWithRWSet:
        """根据区块高度查询区块所有数据
        :param int block_height: 区块高度
        :return: BlockInfo
        :raises RequestError: 请求失败
        """
    
    def get_block_height_by_tx_id(self, tx_id: str) -> int:
        """根据交易ID查询区块高度
        :param str tx_id: 交易id
        :return: 区块高度
        :raises RequestError: 请求失败
        """
    
    def get_block_height_by_hash(self, block_hash: str) -> int:
        """根据区块hash查询区块高度
        :param str block_hash: 区块Hash
        :return: 区块高度
        :raises RequestError: 请求失败
        """
    
    def get_archived_block_height(self) -> int:
        """查询已归档的区块高度
        :return: 区块高度
        :raises RequestError: 请求失败
        """
    
    def get_current_block_height(self) -> int:
        """
        查询当前区块高度
        :return: 区块高度
        """
    
    def get_block_header_by_height(self, block_height: int) -> BlockHeader:
        """
        根据高度获取区块头
        :param int block_height: 区块高度
        :return: 区块头
        """
    
    def invoke_system_contract(self, contract_name: str, method: str, params: Union[dict, list], tx_id: str,
                               timeout: int) -> TxResponse:
        """
        调用系统合约
        :param str contract_name: 系统合约名称
        :param str method: 系统合约方法
        :param str tx_id: 交易ID
        :param dict params: 参数
        :param int timeout: 超时时间
        :return: 响应信息
        """
    
    def query_system_contract(self, contract_name: str, method: str, params: Union[dict, list], tx_id: str,
                              timeout: int) -> TxResponse:
        """
        查询系统合约
        :param str contract_name: 系统合约名称
        :param str method: 系统合约方法
        :param str tx_id: 交易ID
        :param dict params: 参数
        :param int timeout: 超时时间
        :return: 响应信息
        """
    
    def get_merkle_path_by_tx_id(self, tx_id: str) -> bytes:
        """
        根据交易ID获取Merkle树路径
        :param tx_id: 交易ID
        :return: Merkle树路径
        """
    
    def create_native_contract_access_grant_payload(self, grant_contract_list: List[str]) -> Payload:
        """
        生成原生合约授权访问待签名Payload
        :param grant_contract_list: 授予权限的访问合约列表 # TODO 确认 合约状态必须是FROZEN
        :return: 待签名Payload
        """
    
    def create_native_contract_access_revoke_payload(self, revoke_contract_list: List[str]) -> Payload:
        """
        生成原生合约吊销授权访问待签名Payload
        :param revoke_contract_list: 吊销授予权限的访问合约列表
        :return: 待签名Payload
        """
    
    def get_contract_info(self, contract_name: str) -> Contract:
        """
        获取合约信息
        :param contract_name: 用户合约名称
        :return: 合约信息
        :raise: RequestError: 请求出错
        :raise: AssertionError: 响应失败
        """
    
    def get_contract_list(self) -> List[Contract]:
        """
        获取合约列表
        :return: 合约列表
        """
    
    def get_disabled_native_contract_list(self) -> List[str]:
        """
        获取禁用原生合约名称列表
        :return:
        """
    
    # 链配置 ------------------------------------------------------------------------------------------------------------
    def get_chain_config(self) -> ChainConfig:
        """
        获取链配置
        :return: ChainConfig
        :raises RequestError: 请求失败
        """
    
    def get_chain_config_by_block_height(self, block_height: int) -> int:
        """根据指定区块高度查询最近链配置
        如果当前区块就是配置块，直接返回当前区块的链配置
        :param int block_height: 块高
        :return: chain_config_pb2.ChainConfig
        :raises RequestError: 请求失败
        """
    
    def get_chain_config_sequence(self) -> int:
        """查询最新链配置序号Sequence
        :return: 最新配置序号
        :raises RequestError: 请求失败
        """
    
    def sign_chain_config_payload(self, payload: Payload) -> Payload:
        """对链配置的payload 进行签名
        如果当前区块就是配置块，直接返回当前区块的链配置
        :param Payload payload: 交易payload
        :return: 签名的背书
        :raises
        """
    
    def send_chain_config_update_request(self, payload: Payload, endorsers: List[EndorsementEntry], timeout: int,
                                         with_sync_result: bool) -> TxResponse:
        """
        发送链配置更新请求
        :param payload: 请求体
        :param endorsers: 背书列表
        :param timeout: 超时时间
        :param with_sync_result: 是否同步交易结果
        :return:
        """
    
    def create_chain_config_core_update_payload(self, tx_scheduler_timeout: int,
                                                tx_scheduler_validate_timeout: int) -> Payload:
        """更新Core模块待签名payload生成
        :param tx_scheduler_timeout: 交易调度器从交易池拿到交易后, 进行调度的时间，其值范围为[0, 60]，若无需修改，请置为-1
        :param tx_scheduler_validate_timeout: 交易调度器从区块中拿到交易后, 进行验证的超时时间，其值范围为[0, 60]，若无需修改，请置为-1
        :return: Payload
        :raises InvalidParametersError: 无效参数
        """
    
    def create_chain_config_block_update_payload(self, tx_timestamp_verify: bool, tx_timeout: int,
                                                 block_tx_capacity: int, block_size: int,
                                                 block_interval: int, tx_parameter_size: int) -> Payload:
        """更新区块生成模块待签名payload生成
        :param tx_timestamp_verify: 是否需要开启交易时间戳校验
        :param tx_timeout: 交易时间戳的过期时间(秒)，其值范围为[600, +∞)（若无需修改，请置为-1）
        :param block_tx_capacity: 区块中最大交易数，其值范围为(0, +∞]（若无需修改，请置为-1）
        :param block_size: 区块最大限制，单位MB，其值范围为(0, +∞]（若无需修改，请置为-1）
        :param block_interval: 出块间隔，单位:ms，其值范围为[10, +∞]（若无需修改，请置为-1）
        :return: Payload
        :raises InvalidParametersError: 无效参数
        """
    
    def create_chain_config_trust_root_add_payload(self, trust_root_org_id: str, trust_root_crts: List[str]) -> Payload:
        """添加信任组织根证书待签名payload生成
        :param str trust_root_org_id: 组织Id
        :param trust_root_crts: 根证书列表
        :return: Payload
        :raises InvalidParametersError: 无效参数
        """
    
    def create_chain_config_trust_root_update_payload(self, trust_root_org_id: str,
                                                      trust_root_crts: List[str]) -> Payload:
        """更新信任组织根证书待签名payload生成
        :param str trust_root_org_id: 组织Id
        :param trust_root_crts: 根证书列表
        :return: Payload
        :raises InvalidParametersError: 无效参数
        """
    
    def create_chain_config_trust_root_delete_payload(self, trust_root_org_id: str) -> Payload:
        """删除信任组织根证书待签名payload生成
        :param str trust_root_org_id: 组织Id
        :return: Payload
        :raises InvalidParametersError: 无效参数
        """
    
    def create_chain_config_trust_member_add_payload(self, trust_member_org_id: str, trust_member_node_id: str,
                                                     trust_member_info: str, trust_member_role: str,
                                                     ) -> Payload:
        """
        生成链配置添加三方TRUST_MEMBER待签名Payload
        :param trust_member_org_id: 组织ID
        :param trust_member_node_id: 节点ID
        :param trust_member_info: 节点信息
        :param trust_member_role: 节点角色
        :return: 待签名Payload
        :raises InvalidParametersError: 无效参数
        """
    
    def create_chain_config_trust_member_delete_payload(self, trust_member_info: str) -> Payload:
        """
        生成链配置删除三方TRUST_MEMBER待签名Payload
        :param trust_member_info: 节点证书信息
        :return: 待签名Payload
        :raises InvalidParametersError: 无效参数
        """
    
    def create_chain_config_permission_add_payload(self, permission_resource_name: str, policy: Policy) -> Payload:
        """添加权限配置待签名payload生成
        :param str permission_resource_name: 权限名
        :param policy: 权限规则
        :return: Payload
        :raises InvalidParametersError: 无效参数
        """
    
    def create_chain_config_permission_update_payload(self, permission_resource_name, policy) -> Payload:
        """更新权限配置待签名payload生成
        :param str permission_resource_name: 权限名
        :param policy: 权限规则
        :return: Payload
        :raises InvalidParametersError: 无效参数
        """
    
    def create_chain_config_permission_delete_payload(self, permission_resource_name: str) -> Payload:
        """删除权限配置待签名payload生成
        :param str permission_resource_name: 权限名
        :return: Payload
        :raises InvalidParametersError: 无效参数
        """
    
    def create_chain_config_consensus_node_id_add_payload(self, node_org_id: str, node_ids: List[str]) -> Payload:
        """添加共识节点地址待签名payload生成
        :param str node_org_id: 节点组织Id
        :param node_ids: 节点Id
        :return: Payload
        :raises InvalidParametersError: 无效参数
        """
    
    def create_chain_config_consensus_node_id_update_payload(self, node_org_id: str, node_old_id: str,
                                                             node_new_id: str) -> Payload:
        """更新共识节点地址待签名payload生成
        :param str node_org_id: 节点组织Id
        :param node_old_id: 节点原Id
        :param node_new_id: 节点新Id
        :return: Payload
        :raises InvalidParametersError: 无效参数
        """
    
    def create_chain_config_consensus_node_id_delete_payload(self, node_org_id: str, node_id: str) -> Payload:
        """删除共识节点地址待签名payload生成
        :param str node_org_id: 节点组织Id
        :param node_id: 节点Id
        :return: Payload
        :raises InvalidParametersError: 无效参数
        """
    
    def create_chain_config_consensus_node_org_add_payload(self, node_org_id: str, node_ids: List[str]) -> Payload:
        """添加共识节点待签名payload生成

        :param str node_org_id: 节点组织Id
        :param node_ids: 节点Id

        :return: Payload

        :raises InvalidParametersError: 无效参数
        """
    
    def create_chain_config_consensus_node_org_update_payload(self, node_org_id: str, node_ids: List[str]) -> Payload:
        """更新共识节点待签名payload生成
        :param str node_org_id: 节点组织Id
        :param node_ids: 节点Id
        :return: Payload
        :raises InvalidParametersError: 无效参数
        """
    
    def create_chain_config_consensus_node_org_delete_payload(self, node_org_id: str) -> Payload:
        """删除共识节点待签名payload生成
        :param str node_org_id: 节点组织Id
        :return: Payload
        :raises InvalidParametersError: 无效参数
        """
    
    def create_chain_config_consensus_ext_add_payload(self, params: Union[dict, list]) -> Payload:
        """添加共识扩展字段待签名payload生成
        :param dict params: 字段key、value对
        :return: Payload
        :raises InvalidParametersError: 无效参数
        """
    
    def create_chain_config_consensus_ext_update_payload(self, params: Union[dict, list]) -> Payload:
        """更新共识扩展字段待签名payload生成
        :param dict params: 字段key、value对
        :return: Payload
        :raises InvalidParametersError: 无效参数
        """
    
    def create_chain_config_consensus_ext_delete_payload(self, keys: List[str]) -> Payload:
        """删除共识扩展字段待签名payload生成
        :param keys: 待删除字段
        :return: Payload
        :raises InvalidParametersError: 无效参数
        """
    
    def create_chain_config_alter_addr_type_payload(self, addr_type: AddrType) -> Payload:
        """
        生成链配置变更地址类型待签名Payload
        :param addr_type: 地址类型 "0": chainmaker  "1": zxl
        :return: 待签名Payload
        """
    
    def create_chain_config_enable_or_disable_gas_payload(self) -> Payload:
        """
        生成链配置切换启用/禁用Gas待签名Payload
        :return: 待签名Payload
        """
    
    # 证书管理 ----------------------------------------------------------------------------------------------------------
    def enable_cert_hash(self):
        """
        启用证书hash，会修改实例的enabled_cert_hash值。默认为不启用。
        :raises OnChainFailedError: 证书上链失败
        """
    
    def disable_cert_hash(self):
        """
        关闭证书hash，会修改实例的enabled_cert_hash值。
        """
    
    def add_cert(self, timeout: int, with_sync_result: bool) -> TxResponse:
        """
        添加用户的证书
        :param int timeout: 设置请求超时时间
        :param bool with_sync_result: 同步返回请求结果
        :return: TxResponse
        :raises RequestError: 请求失败
        """
    
    def query_cert(self, cert_hashes: List[bytes], timeout: int) -> TxResponse:
        """
        查询证书的hash是否已经上链
        :param list cert_hashes: 证书hash列表(List)
        :param int timeout: 设置请求超时时间
        :return: TxResponse
        :raises RequestError: 请求失败
        """
    
    def delete_cert(self, cert_hashes: List[bytes], endorsers: List[EndorsementEntry],
                    timeout: int, with_sync_result: bool) -> TxResponse:
        """
        删除用户的证书
        :param cert_hashes: 证书hash列表
        :param int timeout: 超时时长
        :param bool with_sync_result: 是否同步返回请求结果
        :return: Response
        :raises RequestError: 请求失败
        """
    
    def get_cert_hash(self):
        """返回用户的签名证书hash
        :return: 证书hash值
        """
    
    def create_cert_delete_payload(self, cert_hashes: List[str], ) -> Payload:
        """生成删除用户的证书待签名Payload
        :param cert_hashes: 证书hash列表, 每个证书hash应转为hex字符串
        :return: Payload
        """
    
    def create_cert_freeze_payload(self, certs: List[str]) -> Payload:
        """对证书管理的payload 进行签名
        :param list certs: 证书列表(List)，证书为字符串格式
        :return: Payload
        :raises
        """
    
    def create_cert_unfreeze_payload(self, certs: List[str]) -> Payload:
        """对证书管理的payload 进行签名
        :param list certs: 证书列表，证书为字符串格式
        :return: Payload
        :raises
        """
    
    def create_cert_revoke_payload(self, cert_crl: str) -> Payload:
        """对证书管理的payload 进行签名
        :param str cert_crl: 证书吊销列表，字符串形式
        :return: Payload
        :raises
        """
    
    def sign_cert_manage_payload(self, payload: Payload) -> Payload:
        """对证书管理的payload 进行签名
        :param Payload payload:
        :param payload_bytes: 待签名的payload字节数组
        :return: paylaod的背书信息
        :raises
        """
    
    def send_cert_manage_request(self, payload: Payload, endorsers: List[EndorsementEntry],
                                 timeout: int, with_sync_result: bool) -> TxResponse:
        """
        发送证书管理请求
        :param Payload payload: 交易payload
        :param list endorsers: 背书列表
        :param int timeout: 超时时间
        :param bool with_sync_result: 是否同步交易执行结果。如果不同步，返回tx_id，供异步查询; 同步则循环等待，返回交易的执行结果。
        :return: Response
        :raises RequestError: 请求失败
        """
    
    # 订阅 --------------------------------------------------------------------------------------------------------------
    def subscribe_block(self, start_block: int, end_block: int, with_rw_set: bool, only_header: bool,
                        callback: Callable) -> List[BlockInfo]:
        """
        订阅区块
        :param start_block: 订阅的起始区块
        :param end_block: 订阅的结束区块
        :param with_rw_set: 是否包含读写集
        :param only_header: 是否只订阅区块头
        :param callback: 回调函数
        :return:
        """
    
    def subscribe_tx(self, start_block: int, end_block: int, contract_name: str, tx_ids: List[str],
                     callback: Callable):
        """"""
    
    def subscribe_contract_event(self, start_block: int, end_block: int, topic: str, contract_name: str,
                                 callback: Callable):
        """"""
    
    def subscribe(self, payload: Payload, callback):
        """"""
    
    # Hibe -------------------------------------------------------------------------------------------------------------
    def create_hibe_init_params_tx_payload_params(self, order_id: str, hibe_params: list):
        """

        :param order_id:
        :param hibe_params:
        :return:
        """
    
    def create_hibe_tx_payload_param_with_hibe_params(self, plaintext: list, receiver_ids: list,
                                                      params_bytes_list: list, tx_id: str, key_type: str):
        """
        
        :param plaintext:
        :param receiver_ids:
        :param params_bytes_list:
        :param tx_id:
        :param key_type:
        :return:
        """
    
    def create_hibe_tx_payload_param_without_hibe_params(self, contract_name: str, query_params_method: str,
                                                         plaintext: list, receiver_ids: list, receiver_oreg_ids: list,
                                                         tx_id: str, key_type: str, timeout: int):
        """

        :param contract_name:
        :param query_params_method:
        :param plaintext:
        :param receiver_ids:
        :param receiver_oreg_ids:
        :param tx_id:
        :param key_type:
        :param timeout:
        :return:
        """
    
    def query_hibe_params_with_org_id(self, contract_name: str, method: str, org_id: str, timeout: int):
        """

        :param contract_name:
        :param method:
        :param org_id:
        :param timeout:
        :return:
        """
    
    def decrypt_hibe_tx_by_tx_id(self, local_id: str, hibe_params: list, hibe_prv_key: list, tx_id: str,
                                 key_type) -> bytes:
        """

        :param local_id:
        :param hibe_params:
        :param hibe_prv_key:
        :param tx_id:
        :param key_type:
        :return:
        """
    
    # 归档 -------------------------------------------------------------------------------------------------------------
    def create_archive_block_payload(self, target_block_height):
        """

        :param target_block_height:
        :return:
        """
    
    def create_restore_block_payload(self, full_block: bytes):
        """

        :param full_block:
        :return:
        """
    
    def sign_archive_payload(self, payload):
        """

        :param payload:
        :return:
        """
    
    def send_archive_block_request(self, merge_signed_payload_bytes, timeout=None):
        """

        :param merge_signed_payload_bytes:
        :param timeout:
        :return:
        """
    
    def send_restore_block_request(self, merge_signed_payload_bytes):
        """

        :param merge_signed_payload_bytes:
        :return:
        """
    
    def get_archived_tx_by_tx_id(self, tx_id) -> Result:
        """根据交易id查询已归档的交易
        :param tx_id: 交易id
        :return: 交易详情
        :raises RequestError: 请求失败
        """
    
    def get_archived_full_block_by_height(self, block_height) -> BlockInfo:
        """根据区块高度，查询已归档的完整区块（包含合约event info）
        :param block_height: 区块高度
        :return: 区块详情 BlockInfo
        :raises RequestError: 请求失败
        """
    
    def get_archived_block_by_height(self, block_height, with_rwset) -> BlockInfo:
        """根据区块高度，查询已归档的区块
        :param block_height: 区块高度
        :return: 区块详情 BlockInfo
        :raises RequestError: 请求失败
        """
    
    def get_archived_block_by_hash(self, block_hash, with_rwset) -> BlockInfo:
        """根据区块hash查询已归档的区块
        :param block_hash: 区块hash
        :param with_rwset: 是否包含读写集
        :return: 区块详情 BlockInfo
        :raises RequestError: 请求失败
        """
    
    def get_archived_block_by_tx_id(self, tx_id, with_rwset) -> BlockInfo:
        """根据交易id查询已归档的区块
        :param tx_id: 交易id
        :param with_rwset: 是否包含读写集
        :return: 区块详情 BlockInfo
        :raises RequestError: 请求失败
        """
    
    # 隐私合约 ----------------------------------------------------------------------------------------------------------
    def save_data(self, contract_name: str, contract_version: str, is_deployment: bool, code_hash: bytes,
                  report_hash: bytes, result,
                  coder_header: bytes, tx_id: str, rwset, sign: bytes, events, private_req: bytes,
                  with_sync_result: bool, timeout: int) -> TxResponse:
        """

        :param contract_name:
        :param contract_version:
        :param is_deployment:
        :param code_hash:
        :param report_hash:
        :param result:
        :param coder_header:
        :param tx_id:
        :param rwset:
        :param sign:
        :param events:
        :param private_req:
        :param with_sync_result:
        :param timeout:
        :return:
        """
    
    def save_remote_attestation_proof(self, proof: str, tx_id: str,
                                      with_sync_result: bool) -> TxResponse:
        """

        :param proof:
        :param tx_id:
        :param with_sync_result:
        :return:
        """
    
    def create_save_enclave_ca_cert_payload(self, enclave_ca_cert: str, tx_id: str) -> Payload:
        """

        :param enclave_ca_cert:
        :param tx_id:
        :return:
        """
    
    def get_enclave_ca_cert(self) -> bytes:
        """

        :return:
        """
    
    def check_caller_cert_auth(self, payload: str, org_ids: List[str], sign_pairs) -> TxResponse:
        """

        :param payload:
        :param org_ids:
        :param sign_pairs:
        :return:
        """
    
    def get_enclave_report(self, enclave_id: str) -> bytes:
        """

        :param enclave_id:
        :return:
        """
    
    def get_enclave_proof(self, enclave_id: str) -> bytes:
        """

        :param enclave_id:
        :return:
        """
    
    def get_data(self, contract_name: str, key: str) -> bytes:
        """

        :param contract_name:
        :param key:
        :return:
        """
    
    def save_dir(self, order_id: str, tx_id: str, private_dir,
                 timeout: int, with_sync_result: bool) -> TxResponse:
        """

        :param order_id:
        :param tx_id:
        :param private_dir:
        :param with_sync_result:
        :param timetou:
        :return:
        """
    
    def get_contract(self, contract_name: str, code_hash: str):
        """

        :param contract_name:
        :param code_hash:
        :return:
        """
    
    def get_dir(self, order_id: str) -> bytes:
        """

        :param order_id:
        :return:
        """
    
    def create_save_enclave_report_payload(self, enclave_id: str, report: str, tx_id: str) -> Payload:
        """

        :param enclave_id:
        :param report:
        :param tx_id:
        :return:
        """
    
    def get_enclave_encrypt_pubkey(self, enclave_id: str) -> bytes:
        """

        :param enclave_id:
        :return:
        """
    
    def get_enclave_verification_pubkey(self, enclave_id: str) -> bytes:
        """

        :param enclave_id:
        :return:
        """
    
    def get_enclave_challenge(self, enclave_id: str) -> bytes:
        """

        :param enclave_id:
        :return:
        """
    
    def get_enclave_signature(self, enclave_id: str) -> bytes:
        """

        :param enclave_id:
        :return:
        """
    
    # 连接 -------------------------------------------------------------------------------------------------------------
    def stop(self):
        """

        :return:
        """
    
    # 版本信息 ----------------------------------------------------------------------------------------------------------
    def get_chainmaker_server_version(self):
        """

        :return:
        """
    
    # 公钥管理 ----------------------------------------------------------------------------------------------------------
    def create_pubkey_add_payload(self, pubkey: str, org_id: str, role: str):
        """
        创建公钥添加Payload
        :param pubkey: 公钥
        :param org_id: 组织id
        :param role: 角色
        :return: 生成的payload
        """
    
    def create_pubkey_delete_payload(self, pubkey: str, org_id: str):
        """
        创建公钥删除Payload
        :param pubkey: 公钥
        :param org_id: 组织id
        :return: 生成的payload
        """
    
    def create_pubkey_query_payload(self, pubkey: str):
        """
       创建公钥删除Payload
       :param pubkey: 公钥
       :param org_id: 组织id
       :return: 生成的payload
       """
    
    def send_pubkey_manage_request(self, payload, endorsers: List[EndorsementEntry],
                                   timeout: int, with_sync_result: bool) -> TxResponse:
        """
        发送公钥管理请求
        :param payload: 公钥管理payload
        :param endorsers: 背书列表
        :param timeout: 超时时间
        :param with_sync_result: 是否同步结果
        :return: 交易响应或事务交易信息
        """
    
    # 多签 -------------------------------------------------------------------------------------------------------------
    def multi_sign_contract_req(self, payload: Payload, timeout: int = None, with_sync_result: bool = False):
        """
        发起多签请求
        :param payload: 待签名payload
        :param timeout: 请求超时时间
        :param with_sync_result: 是否同步获取交易结果
        :return: 交易响应或交易信息
        """
    
    def multi_sign_contract_vote(self, multi_sign_req_payload, endorser: User, is_agree: bool = True,
                                 timeout: int = None, with_sync_result: bool = False) -> TxResponse:
        """
        对请求payload发起多签投票
        :param multi_sign_req_payload: 待签名payload
        :param endorser: 投票用户对象
        :param is_agree: 是否同意，true为同意，false则反对
        :param timeout: 请求超时时间
        :param with_sync_result: 是否同步获取交易结果
        :return: 交易响应或交易信息
        """
    
    def multi_sign_contract_vote_tx_id(self, tx_id, endorser: User, is_agree: bool,
                                       timeout: int = None, with_sync_result: bool = False) -> TxResponse:
        """
        对交易ID发起多签投票
        :param tx_id: 交易ID
        :param endorser: 投票用户对象
        :param is_agree: 是否同意，true为同意，false则反对
        :param timeout: 请求超时时间
        :param with_sync_result: 是否同步获取交易结果
        :return: 交易响应或交易信息
        """
    
    def multi_sign_contract_query(self, tx_id: str) -> MultiSignInfo:
        """
        根据交易ID查询多签状态
        :param tx_id: 交易ID
        :return: 多签信息
        """
    
    def create_multi_sign_req_payload(self, params: Union[list, dict]) -> Payload:
        """
        根据发起多签请求所需的参数构建payload
        :param params: 发起多签请求所需的参数
        :return: 待签名Payload
        """
    
    # Gas管理 ----------------------------------------------------------------------------------------------------------
    def get_gas_admin(self) -> str:
        """
        查询Gas管理员地址
        :return: Gas管理员账户地址
        """
    
    def get_gas_balance(self, address: str) -> int:
        """
        获取Gas账户余额
        :param address: 账户地址
        :return:
        """
    
    def get_gas_account_status(self, address: str) -> bool:
        """
        查询Gas账户状态
        :param address: 账户地址
        :return: 正常是返回True, 冻结返回False
        """
    
    def create_set_gas_admin_payload(self, address: str) -> Payload:
        """
        创建设置Gas管理员Payload
        :param address: 管理员账户地址
        :return: Payload
        """
    
    def create_recharge_gas_payload(self, recharge_gas_list: List[RechargeGasItem]) -> Payload:
        """
        创建Gas充值Payload
        :param recharge_gas_list: 充值列表
        :return: Payload
        """
    
    def create_refund_gas_payload(self, address: str, amount: int) -> Payload:
        """
        创建Gas退款Payload
        :param address: 账户地址
        :param amount: 退款额度
        :return: Payload
        """
    
    def create_frozen_gas_account_payload(self, address: str) -> Payload:
        """
        创建冻结账户Payload
        :param address: 账户地址
        :return: Payload
        """
    
    def create_unfrozen_gas_account_payload(self, address: str) -> Payload:
        """
        创建解冻账户Payload
        :param address: 账户地址
        :return: Payload
        """
    
    def send_gas_manage_request(self, payload: Payload, endorsers: List[EndorsementEntry],
                                timeout: int, with_sync_result: bool) -> TxResponse:
        """
        发送Gas管理请求
        :param Payload payload: Payload
        :param list endorsers: 背书列表
        :param int timeout: 超时时间
        :param bool with_sync_result: 是否同步轮询结果
        :return: 响应信息
        """
    
    @staticmethod
    def attach_gas_limit(payload: Payload, limit: int) -> Payload:
        """
        设置Gas转账限制
        :param Payload payload: Payload
        :param limit: Gas交易限制
        :return: Payload
        """
    
    # 证书别名管理 -------------------------------------------------------------------------------------------------------
    def add_alias(self) -> TxResponse:
        """"""
    
    def query_cert_alias(self, aliases: List[str]):
        """"""
    
    def create_update_cert_by_alias_payload(self, alias: str, new_cert_pem: str) -> Payload:
        """"""
    
    def sign_update_cert_by_alias_payload(self, payload: Payload) -> bytes:
        """"""
    
    def update_cert_by_alias(self, payload: Payload, endorsers: List[EndorsementEntry],
                             timeout: int, with_sync_result: bool) -> TxResponse:
        """"""
    
    def create_delete_cert_alias_payload(self, aliases: List[str]) -> Payload:
        """"""
    
    def sign_delete_alias_payload(self, payload: Payload) -> bytes:
        """"""
    
    def delete_cert_alias(self, payload: Payload, endorsers: List[EndorsementEntry],
                          timeout: int, with_sync_result: bool) -> TxResponse:
        """"""
