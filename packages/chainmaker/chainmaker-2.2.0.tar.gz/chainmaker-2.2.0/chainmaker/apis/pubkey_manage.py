#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# @FileName     :   pubkey_manage.py
# @Function     :   ChainMaker 公钥管理接口-仅适用于Public及PermissionWithKey模式

from chainmaker.apis.base_client import BaseClient
from chainmaker.keys import SystemContractNames, PubkeyManageMethods, Role
from chainmaker.protos.common.request_pb2 import Payload
from chainmaker.protos.common.result_pb2 import TxResponse


class PubkeyManageMixIn(BaseClient):
    """公钥管理接口"""

    def _create_pubkey_manage_payload(self, method: str, params: dict)->Payload:
        """
        私有方法-创建公钥管理Payload
        :param method: 对应的公钥管理方法
        :param params: 相关参数
        :return: 生成的payload
        """
        payload = self.payload_builder.create_invoke_payload(SystemContractNames.PUBKEY_MANAGE, method, params)
        return payload

    def create_pubkey_add_payload(self, pubkey: str, org_id: str, role: Role)->Payload:
        """
        创建公钥添加Payload
        :param pubkey: 公钥文件内容
        :param org_id: 组织ID
        :param role: 角色
        :return: 生成的payload
        """
        params = {
            'pubkey': pubkey,
            'org_id': org_id,
            'role': role
        }
        return self._create_pubkey_manage_payload(PubkeyManageMethods.PUBKEY_ADD, params)

    def create_pubkey_delete_payload(self, pubkey: str, org_id: str)->Payload:
        """
        创建公钥删除Payload
        :param pubkey: 公钥
        :param org_id: 组织id
        :return: 生成的payload
        """
        params = {
            'pubkey': pubkey,
            'org_id': org_id,
        }
        return self._create_pubkey_manage_payload(PubkeyManageMethods.PUBKEY_DELETE, params)

    def create_pubkey_query_payload(self, pubkey: str)->Payload:
        """
       创建公钥查询Payload
       :param pubkey: 公钥文件内容
       :return: 生成的payload
       """
        params = {
            'pubkey': pubkey,
        }
        return self.payload_builder.create_query_payload(SystemContractNames.PUBKEY_MANAGE, PubkeyManageMethods.PUBKEY_QUERY, params)
    
    def send_pubkey_manage_request(self, payload, endorsers: list = (), timeout: int = None,
                                   with_sync_result: bool = False)->TxResponse:
        """
        发送公钥管理请求
        :param payload: 公钥管理payload
        :param endorsers: 背书列表
        :param timeout: 超时时间
        :param with_sync_result: 是否同步结果
        :return: 交易响应或事务交易信息
        """
        return self.send_request_with_sync_result(payload, endorsers, timeout, with_sync_result)

    def query_pubkey(self, pubkey: str) -> TxResponse:
        """
        查询搞公钥
        :param pubkey:公钥文件内容
        :return: 交易响应
        """
        payload = self.create_pubkey_query_payload(pubkey)
        return self.send_request_with_sync_result(payload, with_sync_result=False)

    def add_pubkey(self, pubkey: str, org_id: str, role: Role, timeout: int = None,
                   with_sync_result: bool = True) -> TxResponse:
        """
        添加公钥
        :param pubkey: 公钥文件内容
        :param org_id: 组织ID
        :param role: 角色
        :param timeout: 超时时间
        :param with_sync_result: 是否同步轮询交易结果
        :return: 交易响应
        """
        payload = self.create_pubkey_add_payload(pubkey, org_id, role)
        return self.send_manage_request(payload, timeout=timeout, with_sync_result=with_sync_result)

    def del_pubkey(self, pubkey: str, org_id: str, timeout: int = None, with_sync_result: bool = True):
        """
        删除公钥
        :param pubkey: 公钥文件内容
        :param org_id: 组织ID
        :param timeout: 超时时间
        :param with_sync_result: 是否同步轮询交易结果
        :return: 交易响应
        """
        payload = self.create_pubkey_delete_payload(pubkey, org_id)
        return self.send_manage_request(payload, timeout=timeout, with_sync_result=with_sync_result)

