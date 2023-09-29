#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# @FileName     :   chain_client.py
# @Function     :   ChainMaker链客户端
import os
import time
from pathlib import Path
from typing import Union, List

import grpc
from cryptography.hazmat.primitives.asymmetric import ec, rsa

from chainmaker.conn_pool import ConnectionPool
from chainmaker.node import Node
from chainmaker.user import User
from chainmaker.payload import PayloadBuilder
from chainmaker.apis.archive import ArchiveMixIn
from chainmaker.apis.cert_alias_manage import CertAliasManageMixIn
from chainmaker.apis.cert_manage import CertManageMixIn
from chainmaker.apis.chain_config import ChainConfigMixIn
from chainmaker.apis.gas_manage import GasManageMixIn
from chainmaker.apis.multisign_contract import MultiSignContractMixin
from chainmaker.apis.pubkey_manage import PubkeyManageMixIn
from chainmaker.apis.subscribe import SubscribeMixIn
from chainmaker.apis.system_contract import SystemContractMixIn
from chainmaker.apis.user_contract import UserContractMixIn
from chainmaker.exceptions import ERR_MSG_MAP, RequestError, RpcConnectError, TX_RESPONSE_ERROR_MAP
from chainmaker.keys import AuthType, HashType, Defaults, ArchiveConfig, RPCClientConfig, PKCS11Config
from chainmaker.protos.api.rpc_node_pb2_grpc import RpcNodeStub
from chainmaker.protos.common.request_pb2 import Payload, TxRequest, EndorsementEntry
from chainmaker.protos.common.result_pb2 import TxResponse, TxStatusCode, Result
from chainmaker.utils.file_utils import load_yaml
from chainmaker.utils.log_utils import logger

SDK_CONFIG_USER_CONFIG_FILTER = {"org_id", "user_key_file_path", "user_crt_file_path", "user_sign_key_file_path",
                                 "user_sign_crt_file_path", "crypto", "auth_type", "alias"}


class ChainClient(SystemContractMixIn, UserContractMixIn, ChainConfigMixIn, CertManageMixIn, SubscribeMixIn,
                  ArchiveMixIn, PubkeyManageMixIn, GasManageMixIn, CertAliasManageMixIn, MultiSignContractMixin):
    
    def __init__(self, chain_id, user: User, nodes: List[Node]):
        self.user = user
        self.nodes = nodes
        self.chain_id = chain_id
        
        self.pool = ConnectionPool(user, nodes)
        self.endorse_users = []
        self.payload_builder = PayloadBuilder(self.chain_id)
        self.logger = logger
        
        self.retry_limit = Defaults.RETRY_LIMIT
        self.retry_interval = Defaults.RETRY_INTERVAL
        self.archive_config = None
        self.rpc_client_config = None
        self.pkcs11_config = None
    
    def __repr__(self):
        return f'<ChainClient user={self.user}>'
    
    @classmethod
    def from_conf(cls, sdk_config: Union[dict, str, Path], node_index=Defaults.NODE_INDEX):
        """
        加载sdk_config配置文件并生成链客户端对象
        :param sdk_config: 加载后的sdk_config内容或, sdk_config.yml配置文件路径
        :param node_index: 要连接到节点索引
        :return: ChainClient链客户端对象
        """
        if isinstance(sdk_config, dict):  # 增加支持字典格式的sdk_config
            data = sdk_config
        else:
            assert os.path.isfile(str(sdk_config)), 'FileNotExist: %s' % sdk_config
            data = load_yaml(sdk_config)
        
        config = data['chain_client']
        chain_id = config['chain_id']
        
        user_conf = {key: config.get(key) for key in SDK_CONFIG_USER_CONFIG_FILTER}
        user = User.from_conf(**user_conf)
        
        nodes = [Node.from_conf(**n) for n in config['nodes']]
        
        cc = cls(chain_id, user, nodes)
        
        retry_limit = config.get('retry_limit')
        retry_interval = config.get('retry_interval')
        
        archive_config = config.get('archive')
        rpc_client_config = config.get('rpc_client')
        pkcs11_config = config.get('pkcs11')
        
        if retry_limit is not None and isinstance(retry_limit, int) and retry_limit > 0:
            cc.retry_limit = retry_limit
        
        if retry_interval is not None and isinstance(retry_interval, int) and retry_interval > 0:
            cc.retry_interval = retry_interval // 1000  # 配置中为毫秒
        
        if archive_config and isinstance(archive_config, dict):
            cc.archive_config = ArchiveConfig(**archive_config)
        
        if rpc_client_config and isinstance(rpc_client_config, dict):
            cc.rpc_client_config = RPCClientConfig(**rpc_client_config)
        
        if pkcs11_config and isinstance(pkcs11_config, dict):
            cc.pkcs11_config = PKCS11Config(**pkcs11_config)
        
        if user.alias and isinstance(user.alias, str):  # TODO 检查合法性
            cc.enable_alias()
        
        return cc
    
    @property
    def node(self) -> Node:
        """当前连接节点"""
        return self.pool.node
    
    @property
    def org_id(self) -> str:
        return self.user.org_id
    
    @org_id.setter
    def org_id(self, org_id: str) -> None:
        self.user.org_id = org_id
    
    @property
    def enabled_alias(self) -> bool:
        return self.user.enabled_alias
    
    @property
    def enabled_crt_hash(self) -> bool:
        return self.user.enabled_crt_hash
    
    @enabled_crt_hash.setter
    def enabled_crt_hash(self, is_enable: bool) -> None:
        self.user.enabled_crt_hash = is_enable
    
    @property
    def hash_type(self) -> HashType:
        return self.user.hash_type
    
    @hash_type.setter
    def hash_type(self, hash_type: HashType) -> None:
        self.user.hash_type = hash_type
    
    @property
    def auth_type(self) -> AuthType:
        return self.user.auth_type
    
    @auth_type.setter
    def auth_type(self, auth_type: AuthType) -> None:
        self.user.auth_type = auth_type
    
    @property
    def user_cert_hash(self) -> bytes:
        return self.user.cert_hash
    
    @user_cert_hash.setter
    def user_cert_hash(self, cert_hash: bytes) -> None:
        self.user.cert_hash = cert_hash
    
    @property
    def alias(self) -> str:
        return self.user.alias
    
    @alias.setter
    def alias(self, alias: str):
        if isinstance(alias, str) and len(alias) > 0:
            self.user.alias = alias
    
    def _get_client(self, node_index: int = None) -> RpcNodeStub:
        """
        根据策略或去连接
        :param node_index: 节点索引
        :return:
        """
        return self.pool.get_client(node_index)
    
    def _create_endorsers(self, payload: Payload, endorse_users: List[User] = None) -> List[EndorsementEntry]:
        """
        根据背书用户创建背书
        :param payload: 待签名请求负荷
        :param endorse_users: 背书用户列表
        :return: 背书列表
        """
        if endorse_users is None:
            endorse_users = self.endorse_users
        payload_bytes = payload.SerializeToString()
        endorsers = [user.endorse(payload_bytes) for user in endorse_users or []]
        return endorsers
    
    def create_endorsers(self, payload: Payload, endorsers_config: List[dict]) -> List[EndorsementEntry]:
        """
        根据背书用户创建背书
        :param payload: 待签名请求负荷
        :param endorsers_config: 用户组织、签名证书等配置列表
        :return: 背书列表
        """
        endorse_users = [User.from_conf(**item) for item in endorsers_config]
        return self._create_endorsers(payload, endorse_users)
    
    def get_sync_result(self, tx_id: str, interval: int = Defaults.TX_CHECK_INTERVAL,
                        timeout: int = Defaults.TX_CHECK_TIMEOUT) -> Result:
        """
        通过交易id轮询交易结果直到可以查询到交易结果或者超时
        :param tx_id: 交易ID
        :param interval: 轮询间隔
        :param timeout: 超时时间
        :return: 交易结果Result对象
        :raise: 超时未查询到交易信息则抛出 TimeoutError
        """
        start = time.time()
        err_msg = ''
        while time.time() - start < self.tx_check_timeout:
            try:
                transaction_info = self.get_tx_by_tx_id(tx_id)
                return transaction_info.transaction.result
            except RequestError as ex:
                err_msg = str(ex)
                time.sleep(self.tx_check_interval)
        raise TimeoutError(
            f'[SDK] get tx_id="%s" transaction info %ss timeout: %s' % (tx_id, self.tx_check_timeout, err_msg))
    
    def _generate_tx_request(self, payload, endorsers=()) -> TxRequest:
        payload_bytes = payload.SerializeToString()
        sender = self.user.endorse(payload_bytes)
        tx_request = TxRequest(
            payload=payload,
            sender=sender,
            endorsers=endorsers
        )
        # self.logger.debug('[SDK] Generate txRequest: %s', json_format.MessageToJson(tx_request))
        
        return tx_request
    
    def _send_request_with_timeout(self, payload: Payload, endorsers: List[EndorsementEntry] = None,
                                   timeout: int = None) -> TxResponse:
        """
        发送带超时时间的交易请求
        :param payload: 待签名请求Payload
        :param endorsers: 背书列表
        :param timeout: 超时时间
        :return: 交易响应TxResponse对象
        :raise 连接异常时抛出 InactiveRpcError
        """
        # 构造请求结构
        if timeout is None:
            timeout = self.request_timeout or Defaults.REQUEST_TIMEOUT
        tx_request = self._generate_tx_request(payload, endorsers)
        return self._get_client().SendRequest(tx_request, timeout=timeout)
    
    def _send_request_with_retry_connect(self, payload: Payload, endorsers: List[EndorsementEntry] = None,
                                         timeout: int = None) -> TxResponse:
        """
        发送带重连的交易请求
        基于self._send_request_with_timeout
        :param payload: 待签名请求Payload
        :param endorsers: 背书列表
        :param timeout: 超时时间
        :return: 交易响应TxResponse对象
        :raise 重连超过retry_limit限制仍无法成功时抛出 RpcConnectError
        """
        
        err_msg = ''
        for i in range(self.retry_limit):
            try:
                return self._send_request_with_timeout(payload, endorsers, timeout)
            except grpc._channel._InactiveRpcError as ex:
                err_msg = ERR_MSG_MAP.get(ex.details(), ex.details())
                time.sleep(self.retry_interval // 1000)  # 毫秒
        else:
            node = self.node
            raise RpcConnectError('RPC服务<%s enable_tls=%s>不可用: %s' % (node.addr, node.enable_tls, err_msg))
    
    def send_request(self, payload: Payload, endorsers: List[EndorsementEntry] = None,
                     timeout: int = None) -> TxResponse:
        """
        发送交易请求并检查是否成功
        带重连机制，基于 self._send_request_with_retry_connect
        :param payload: 待签名请求Payload
        :param endorsers: 背书列表
        :param timeout: 超时时间
        :return: 交易响应TxResponse对象
        :raise 重连超过retry_limit限制仍无法成功时抛出 RpcConnectError
        :raise: RequestError错误子类，如InvalidParameter等
        """
        tx_response = self._send_request_with_retry_connect(payload, endorsers, timeout)
        if tx_response.code != TxStatusCode.SUCCESS:
            err_class = TX_RESPONSE_ERROR_MAP.get(tx_response.code)
            raise err_class(TxStatusCode.Name(tx_response.code), tx_response.message)
        return tx_response
    
    def _update_tx_response_with_result(self, tx_response: TxResponse, result: Result) -> TxResponse:
        """
        更新交易响应，将轮询得到的交易结果中的信息添加到交易响应中
        :param tx_response: 原交易响应
        :param result: self.get_sync_result轮询得到到交易结果
        :return: 包含交易结果的交易响应
        """
        tx_response.code = result.code
        tx_response.message = result.message
        tx_response.contract_result.code = result.contract_result.code
        tx_response.contract_result.result = result.contract_result.result
        tx_response.contract_result.message = result.contract_result.message
        tx_response.contract_result.gas_used = result.contract_result.gas_used
        for contract_event in result.contract_result.contract_event:
            tx_response.contract_result.contract_event.append(contract_event)
        
        return tx_response
    
    def send_request_with_sync_result(self, payload: Payload, endorsers: List[EndorsementEntry] = None,
                                      timeout: int = None,
                                      with_sync_result: bool = None) -> TxResponse:
        """
        发送请求并支持轮询交易结果
        :param payload: 待签名请求Payload
        :param timeout: 超时时间
        :param with_sync_result: 是否同步获取交易结果，默认为False
        :param endorsers: 背书配置
        :return: 交易响应TxResponse对象
        :raise: RequestError错误子类，如InvalidParameter等
        :raise: 在指定时间（self.check_tx_timeout）内未获取到结果抛出，TimeoutError
        """
        if with_sync_result is None:
            with_sync_result = Defaults.WITH_SYNC_RESULT
        
        tx_response = self.send_request(payload, endorsers, timeout)
        
        if with_sync_result is True:
            tx_response.tx_id = payload.tx_id
            result = self.get_sync_result(payload.tx_id)
            tx_response = self._update_tx_response_with_result(tx_response, result)
        return tx_response
    
    def send_manage_request(self, payload: Payload, endorse_users: List[User] = None, timeout: int = None,
                            with_sync_result: bool = True) -> TxResponse:
        """
        发送带默认背书的管理请求
        :param payload: 待签名请求Payload
        :param endorse_users: 背书用户列表，默认为None并使用self.endorse_users
        :param timeout: 超时时间
        :param with_sync_result: 是否同步交易结果，默认为True
        :return: 交易响应TxResponse
        """
        if endorse_users is None:
            endorse_users = self.endorse_users  # 背书用户
        
        endorsers = self._create_endorsers(payload, endorse_users)
        tx_response = self.send_request_with_sync_result(payload, endorsers, timeout, with_sync_result)
        # check_response(tx_response)
        return tx_response
    
    def stop(self) -> None:
        """停止客户端-关闭所有channel连接"""
        self.pool.close()
    
    def get_chainmaker_server_version(self) -> str:
        """获取chainmaker版本号"""
        client = self._get_client()
        req = TxRequest()
        res = client.GetChainMakerVersion(req)
        return res.version
    
    def get_enabled_crt_hash(self) -> bool:  # TODO Test
        """
        是否启用了证书哈希
        :return:
        """
        return self.enabled_crt_hash
    
    def get_user_cert_hash(self) -> bytes:
        """获取用户证书哈希"""
        return self.user.cert_hash
    
    def get_hash_type(self) -> HashType:
        """获取用户证书加密哈希类型"""
        return self.user.hash_type
    
    def get_auth_type(self) -> AuthType:
        """获取链授权类型"""
        return self.user.auth_type
    
    def get_public_key(self) -> Union[ec.EllipticCurvePublicKey, rsa.RSAPublicKey]:
        """获取当前用户公钥"""
        return self.public_key
    
    def get_private_key(self) -> Union[ec.EllipticCurvePrivateKey, rsa.RSAPrivateKey]:
        """获取当前用户私钥"""
        return self.private_key
    
    def get_pkcs11_config(self) -> PKCS11Config:
        return self.pkcs11_config
