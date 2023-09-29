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
from typing import List, Union

import grpc
from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import ec, rsa

from chainmaker.apis import (
    ArchiveMixIn,
    CertAliasManageMixIn,
    CertManageMixIn,
    ChainConfigMixIn,
    ChainQueryMixIn,
    GasManageMixIn,
    MultiSignContractMixin,
    PubkeyManageMixIn,
    SubscribeManageMixIn,
    SystemContractMixIn,
    TransactionManagerMixIn,
    UserContractMixIn
)
from chainmaker.archive_service import (
    ArchiveService
)
from chainmaker.conn_pool import ConnectionPool
from chainmaker.exceptions import (
    RequestError,
    RpcConnectError,
    TX_RESPONSE_ERROR_MAP
)
from chainmaker.keys import (
    AddrType,
    ArchiveCenterConfig,
    ArchiveConfig,
    AuthType,
    Defaults,
    HashType,
    PKCS11Config,
    RPCClientConfig
)
from chainmaker.node import Node
from chainmaker.payload import PayloadBuilder
from chainmaker.protos.accesscontrol.member_pb2 import Member, MemberType
from chainmaker.protos.api.rpc_node_pb2_grpc import RpcNodeStub
from chainmaker.protos.common.request_pb2 import EndorsementEntry, Payload, TxRequest, TxType
from chainmaker.protos.common.result_pb2 import Result, TxResponse, TxStatusCode
from chainmaker.user import User
from chainmaker.utils.file_utils import load_yaml
from chainmaker.utils.log_utils import logger

SDK_CONFIG_USER_CONFIG_FILTER = {
    "org_id",
    "auth_type",
    "crypto",
    "alias",
    "user_key_file_path",
    "user_crt_file_path",
    "user_key_pwd",  # v2.3.0 新增
    "user_sign_key_file_path",
    "user_sign_crt_file_path",
    "user_sign_key_pwd",  # v2.3.0 新增
    "user_enc_key_file_path",  # v2.3.0 新增
    "user_enc_crt_file_path",  # v2.3.0 新增
    "user_enc_key_pwd",  # v2.3.0 新增
    "enable_normal_key",  # v2.3.0 新增
}


class ChainClient(
    ChainQueryMixIn,
    SystemContractMixIn,
    UserContractMixIn,
    ChainConfigMixIn,
    CertManageMixIn,
    SubscribeManageMixIn,
    ArchiveMixIn,
    PubkeyManageMixIn,
    GasManageMixIn,
    CertAliasManageMixIn,
    MultiSignContractMixin,
    TransactionManagerMixIn,
):

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

        # v2.3.0 增加
        self.signer = user

        # v2.32 增加
        self.payer = None  # Default payer
        self.archive_center_query_first = None
        self.archive_center_config = None
        self._archive_service: ArchiveService = None


    def __repr__(self):
        return f'<ChainClient user={self.user}>'

    @property
    def role(self):
        """
        v2.3.0 新增
        :return:
        """
        return self.user.role

    @property
    def uid(self):
        """
        用户Id, 即ski(subject key identifier)
        v2.3.0 新增
        :return:
        """
        return self.user.uid

    @property
    def address(self) -> str:
        """
        用户账户地址
        v2.3.0 新增
        """
        self.user.addr_type = self.get_chain_config().vm.addr_type
        return self.user.address

    @property
    def addr_type(self) -> AddrType:
        """[只读]地址类型
        v2.3.0 新增
        """
        self.user.addr_type = self.get_chain_config().vm.addr_type
        return self.user.addr_type

    @property
    def member_id(self) -> str:
        """[只读]从用户签名证书或公钥中获取用户通用名称
        v2.3.0 新增
        """
        return self.user.member_id

    @property
    def member_type(self) -> MemberType:
        """[只读]当前签名类型-可通过cc.change_member_type()修改
        v2.3.0 新增
        """
        return self.user.member_type

    @property
    def member_info(self) -> bytes:
        """[只读]当用户证书或公钥二进制信息
        v2.3.0 新增
        """
        return self.user.member_info

    @property
    def certificate(self) -> x509.Certificate:
        """[只读]用户签名证书
        v2.3.0 新增
        """
        return self.user.certificate

    @property
    def private_key(self) -> Union[rsa.RSAPrivateKey, ec.EllipticCurvePrivateKey]:
        """[只读]用户私钥对象
        v2.3.0 新增
        """
        return self.user.private_key

    @property
    def public_key(self) -> Union[rsa.RSAPublicKey, ec.EllipticCurvePublicKey]:
        """[只读]用户公钥对象
        v2.3.0 新增
        """
        return self.user.public_key

    @property
    def public_bytes(self) -> bytes:
        """[只读]用户公钥二进制内容
        v2.3.0 新增
        """
        return self.user.public_bytes

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
        cc.archive_center_query_first = config.get('archive_center_query_first')
        archive_center_config = config.get('archive_center_config')

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

        if archive_center_config and isinstance(archive_center_config, dict):
            cc.archive_center_config = ArchiveCenterConfig(**archive_center_config)

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
        self.user._hash_type = hash_type

    @property
    def auth_type(self) -> AuthType:
        return self.user.auth_type

    @auth_type.setter
    def auth_type(self, auth_type: AuthType) -> None:
        self.user.auth_type = auth_type

    @property
    def user_cert_hash(self) -> bytes:
        """客户端用户证书哈希二进制"""
        return self.user.cert_hash

    @user_cert_hash.setter
    def user_cert_hash(self, cert_hash: bytes) -> None:
        self.user.cert_hash = cert_hash

    @property
    def alias(self) -> str:
        """
        客户端用户别名
        """
        return self.user.alias

    @alias.setter
    def alias(self, alias: str):
        if isinstance(alias, str) and len(alias) > 0:
            self.user.alias = alias

    @property
    def is_enabled_normal_key(self) -> bool:
        """
        sdk_config.yml是否设置了enable_normal_key
        v2.3.0 新增
        :return: sdk_config.yml设置了enable_normal_key返回True，否则返回False
        """
        return self.user.enable_normal_key is True

    @property
    def is_archive_center_query_first(self) -> bool:
        """
        sdk_config.yml是否设置了archive_center_query_first=true
        v2.3.2 新增
        :return: sdk_config.yml开启archive_center_query_first返回True,否则返回False
        """
        return self.archive_center_query_first is True

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

    def _generate_tx_request(self, payload, endorsers: List[EndorsementEntry] = None, signer: User = None, payer: User = None) -> TxRequest:
        """
        生成交易请求
        :param payload: 待签名Payload
        :param endorsers: 背书列表
        :param signer: 签名用户 v2.3.0 增加
        :param payer: 代扣Gas用户 v2.3.2 增加
        :return: 交易请求
        """
        payload_bytes = payload.SerializeToString()
        # v2.3.0 修改
        signer = signer or self.signer
        sender = signer.endorse(payload_bytes)

        tx_request = TxRequest(
            payload=payload,
            sender=sender,
            endorsers=endorsers,
        )
        # v2.3.2 增加
        payer = payer or self.payer
        if payer is not None:
            tx_request.payer = payer.endorse(payload_bytes)

        return tx_request

    def _send_request_with_timeout(self, payload: Payload, endorsers: List[EndorsementEntry] = None,
                                   timeout: int = None, gas_limit: int = None, signer: User = None,
                                   payer: User = None) -> TxResponse:
        """
        发送带超时时间的交易请求
        :param payload: 待签名请求Payload
        :param endorsers: 背书列表
        :param timeout: 超时时间
        :param gas_limit: Gas消耗限额 v2.3.0 增加
        :param signer: 签名用户 v2.3.0 增加
        :param payer: 代扣Gas用户 v2.3.2 增加
        :return: 交易响应TxResponse对象
        :raise 连接异常时抛出 InactiveRpcError
        """
        # v2.3.2 修改
        if timeout is None or timeout <= 0:
            timeout = self._get_timeout(payload.tx_type)

        # v2.3.0 修改
        if gas_limit is not None:
            self.attach_gas_limit(payload, gas_limit)

        # v2.3.0 修改 v2.3.2 修改
        tx_request = self._generate_tx_request(payload, endorsers, signer=signer, payer=payer)

        return self._get_client().SendRequest(tx_request, timeout=timeout)

    def _get_timeout(self, tx_type: TxType) -> int:
        """
        根据交易类型获取sdk_config.py中rpc_client配置的超时时间
        :param tx_type: 交易类型
        :return: 超时时间(秒)
        """
        if self.rpc_client_config is None:
            return Defaults.RPC_GET_TX_TIMEOUT if tx_type == TxType.QUERY_CONTRACT else Defaults.RPC_SEND_TX_TIMEOUT
        if tx_type == TxType.QUERY_CONTRACT:
            return self.rpc_client_config.get_tx_timeout or Defaults.RPC_GET_TX_TIMEOUT
        return self.rpc_client_config.send_tx_timeout or Defaults.RPC_SEND_TX_TIMEOUT

    def _send_request_with_retry_connect(self, payload: Payload, endorsers: List[EndorsementEntry] = None,
                                         timeout: int = None, gas_limit: int = None, signer: User = None,
                                         payer: User = None) -> TxResponse:
        """
        发送带重连的交易请求
        基于self._send_request_with_timeout
        :param payload: 待签名请求Payload
        :param endorsers: 背书列表
        :param timeout: 超时时间
        :param gas_limit: Gas消耗限额 v2.3.0 增加
        :param signer: 指定签名用户 v2.3.0 增加
        :param payer: 代扣Gas用户  v2.3.2 增加
        :return: 交易响应TxResponse对象
        :raise 重连超过retry_limit限制仍无法成功时抛出 RpcConnectError
        """
        err_msg = ''
        for i in range(self.retry_limit):
            try:
                return self._send_request_with_timeout(payload, endorsers=endorsers, timeout=timeout,
                                                       gas_limit=gas_limit, signer=signer, payer=payer)
            except grpc.RpcError as ex:
                # err_msg = ERR_MSG_MAP.get(ex.details(), ex.details())
                err_msg = str(ex)
                time.sleep(self.retry_interval // 1000)  # 毫秒
        else:
            node = self.node
            raise RpcConnectError('RPC服务<%s enable_tls=%s>不可用: %s' % (node.addr, node.enable_tls, err_msg))

    def send_request(self, payload: Payload, endorsers: List[EndorsementEntry] = None,
                     timeout: int = None, gas_limit: int = None, signer: User = None, payer: User = None) -> TxResponse:
        """
        发送交易请求并检查是否成功
        带重连机制，基于 self._send_request_with_retry_connect
        :param payload: 待签名请求Payload
        :param endorsers: 背书列表
        :param timeout: 超时时间
        :param gas_limit: Gas消耗限额 v2.3.0 增加
        :param signer: 指定签名用户 v2.3.0 增加
        :param payer: 代扣Gas用户  v2.3.2 增加
        :return: 交易响应TxResponse对象
        :raise 重连超过retry_limit限制仍无法成功时抛出 RpcConnectError
        :raise: RequestError错误子类，如InvalidParameter等
        """
        tx_response = self._send_request_with_retry_connect(payload, endorsers, timeout=timeout, gas_limit=gas_limit,
                                                            signer=signer, payer=payer)
        if tx_response.code != TxStatusCode.SUCCESS:
            err_class = TX_RESPONSE_ERROR_MAP.get(tx_response.code)
            raise err_class(TxStatusCode.Name(tx_response.code), tx_response.message)
        return tx_response


    @staticmethod
    def _update_tx_response_with_result(tx_response: TxResponse, result: Result) -> TxResponse:
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
                                      timeout: int = None, with_sync_result: bool = None,
                                      gas_limit: int = None, signer: User = None, payer: User = None) -> TxResponse:
        """
        发送请求并支持轮询交易结果
        :param payload: 待签名请求Payload
        :param endorsers: 背书配置
        :param timeout: 超时时间
        :param with_sync_result: 是否同步获取交易结果，默认为False
        :param gas_limit: Gas消耗限额 v2.3.0 增加
        :param signer: 指定签名用户 v2.3.0 增加
        :param payer: 代扣Gas用户  v2.3.2 增加
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
                            with_sync_result: bool = True, gas_limit: int = None, signer: User = None,
                            payer: User = None) -> TxResponse:
        """
        发送带默认背书的管理请求
        :param payload: 待签名请求Payload
        :param endorse_users: 背书用户列表，默认为None并使用self.endorse_users
        :param timeout: 超时时间
        :param with_sync_result: 是否同步交易结果，默认为True
        :param gas_limit: Gas消耗限额 v2.3.0 增加
        :param signer: 指定签名用户 v2.3.0 增加
        :param payer: 代扣Gas用户  v2.3.2 增加
        :return: 交易响应TxResponse
        """
        if endorse_users is None:
            endorse_users = self.endorse_users  # 背书用户

        endorsers = self._create_endorsers(payload, endorse_users)
        tx_response = self.send_request_with_sync_result(payload, endorsers, timeout=timeout,
                                                         with_sync_result=with_sync_result, gas_limit=gas_limit,
                                                         signer=signer, payer=payer)
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
        """
        获取sdk_config.yml中的pkcs11配置
        :return: pkcs11配置对象
        """
        return self.pkcs11_config

    def new_access_member(self) -> Member:
        """
        生成新的TxRequest需要的Member对象
        v2.3.0 新增
        :return:
        """
        return self.user.member

