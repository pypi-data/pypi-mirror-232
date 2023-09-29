#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# @FileName     :   cert_alias_manage.py
# @Function     :   ChainMaker 证书别名接口

from typing import List

from chainmaker.apis.base_client import BaseClient
from chainmaker.keys import SystemContractNames, CertManageMethods
from chainmaker.exceptions import RequestError
from chainmaker.protos.common.request_pb2 import Payload
from chainmaker.protos.common.result_pb2 import AliasInfos
from chainmaker.protos.common.result_pb2 import TxResponse, Result


class CertAliasManageMixIn(BaseClient):
    def enable_alias(self):
        """
        启用证书别名
        :return:
        """
        if self.user.enabled_alias is True:
            self.logger.info('DEBUG: 别名已上链')
            return
        if self.check_alias() is True:
            self.logger.info('DEBUG: 经检查别名已上链')
            # self.enabled_alias = True
            self.user.enabled_alias = True
            return
        
        self.add_alias()
        if self.check_alias():
            self.logger.info('DEBUG: 别名上链成功')
            self.user.enabled_alias = True
    
    def check_alias(self):  # 对应sdk-go getCheckAlias   # ✅
        """
        检查证书别名是否上链
        :return:
        """
        try:
            res = self.query_cert_alias([self.alias])
        except RequestError:
            return False
        
        if len(res.alias_infos) != 1:
            self.logger.info(f'DEBUG: 未找到相关别名 {self.alias}')
            return False
        
        if res.alias_infos[0].alias != self.alias:
            self.logger.info(f'DEBUG: 别名不相同 {res.alias_infos.alias} != {self.alias}')
            return False
        
        if not res.alias_infos[0].now_cert.cert:  # 删除后为 b''
            self.logger.info(f'DEBUG: 别名已删除 {self.alias}')
            return False
        
        return True
    
    def add_alias(self) -> Result:  #  MemberType must be MemberType_CERT
        """
        添加别名 需要cert模式+cc.user.enabled_alias=False
        :return: 响应信息
        """
        self.logger.info('[SDK] begin to add alias')
        params = {'alias': self.alias}
        payload = self._create_cert_manage_payload(CertManageMethods.CERT_ALIAS_ADD, params)
        result = self.send_request_with_sync_result(payload, with_sync_result=True)
        
        # assert 0 == result.contract_result.code
        # assert self.alias.encode()  == result.contract_result.result
        return result
    
    def query_cert_alias(self, aliases: List[str]) -> AliasInfos:  # ✅
        self.logger.info('[SDK] begin to query cert by aliases')
        
        params = {'aliases': ','.join(aliases)}
        payload = self.payload_builder.create_query_payload(SystemContractNames.CERT_MANAGE, CertManageMethods.CERTS_ALIAS_QUERY,
                                                            params)
        response = self.send_request_with_sync_result(payload, with_sync_result=False)
        # assert 0 == response.code, response.result
        alias_infos = AliasInfos()
        alias_infos.ParseFromString(response.contract_result.result)
        return alias_infos
    
    def create_update_cert_by_alias_payload(self, alias: str, new_cert_pem: str) -> Payload:  # ✅
        self.logger.debug('[SDK] create [UpdateCertByAlias] to be signed payload')
        params = {'alias': alias, 'cert': new_cert_pem}
        return self._create_cert_manage_payload(CertManageMethods.CERT_ALIAS_UPDATE, params)
    
    def sign_update_cert_by_alias_payload(self, payload: Payload):
        return self.user.endorse(payload)
    
    def update_cert_by_alias(self, payload: Payload, endorsers: list, timeout: int, with_sync_result: bool):
        return self.send_cert_manage_request(payload, endorsers, timeout, with_sync_result)
    
    def create_delete_cert_alias_payload(self, aliases: List[str]):
        """
        生成删除证书别名待签名Payload 需要cert模式+cc.user.enabled_alias=False
        :param aliases: 证书别名列表
        :return: 待签名Payload
        """
        params = {'aliases': ','.join(aliases)}
        return self._create_cert_manage_payload(CertManageMethods.CERTS_ALIAS_DELETE, params)
    
    def sign_delete_alias_payload(self, payload: Payload):
        return self.user.endorse(payload)
    
    def delete_cert_alias(self, payload, endorsers: list, with_sync_result: bool, timeout: int) -> TxResponse:
        return self.send_cert_manage_request(payload, endorsers, timeout, with_sync_result)
