#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# @FileName     :   cert_manage_api.py
# @Function     :   ChainMaker证书管理接口
import logging
import time
from typing import List, Union

from google.protobuf import json_format

from chainmaker.apis.base_client import BaseClient
from chainmaker.exceptions import RequestError, OnChainFailedError
from chainmaker.keys import SystemContractNames, CertManageMethods
from chainmaker.protos.common.request_pb2 import EndorsementEntry
from chainmaker.protos.common.result_pb2 import TxResponse, CertInfos
from chainmaker.utils import crypto_utils


class CertManageMixIn(BaseClient):
    def enable_cert_hash(self):
        """启用证书hash，会修改实例的enabled_crt_hash值。默认为不启用。
        :raises OnChainFailedError: 证书上链失败
        """
        self.logger.debug("[SDK] begin to EnableCertHash")
        if self.enabled_crt_hash:
            return True
        # 获取 证书 hash（fingerprint）
        chain_config = self.get_chain_config()
        hash_algo = chain_config.crypto.hash
        self.user.get_cert_hash(hash_algo)
        
        # 查询是否已经上链
        on_chain = self._check_cert_hash_on_chain(self.user.cert_hash.hex())
        
        if not on_chain:
            tx_response = self.add_cert()
            logging.debug(f'[SDK] add cert tx_response {json_format.MessageToJson(tx_response)}')
            on_chain = self._retry_check_cert_hash_on_chain(self.user.sign_cert_hash.hex())
        
        if on_chain:
            self.user.enabled_crt_hash = True
            self.user.cert_hash = self.get_cert_hash()
        else:
            raise OnChainFailedError("put cert on chain failed")
    
    def disable_cert_hash(self):
        """
        关闭证书hash，会修改实例的enabled_crt_hash值。
        """
        self.logger.debug("[SDK] begin to DisableCertHash")
        
        self.user.enabled_crt_hash = False
    
    def get_cert_hash(self) -> bytes:
        """
        返回用户的签名证书哈希
        :return: 证书hash值
        """
        self.logger.debug("[SDK] begin to GetCertHash")
        
        if not self.user.sign_cert_hash:
            chain_config = self.get_chain_config()
            hash_type = chain_config.crypto.hash
            self.user.get_cert_hash(hash_type)
        return self.user.sign_cert_hash
    
    def _check_cert_hash_on_chain(self, cert_hash)->bool:
        """
        检查指定证书哈希是否上链
        :param cert_hash: 证书哈希
        :return: 已上链返回True，否则返回False
        :raise: 查询不到证书抛出 RequestError
        """
        res = self.query_cert([cert_hash])
        cert_info = res.cert_infos[0]
        
        return True if cert_info.cert else False
    
    def _retry_check_cert_hash_on_chain(self, cert_hash, timeout: int=None)->bool:
        """
        重试检查指定证书哈希是否上链
        :param cert_hash: 证书哈希
        :param timeout: 检查超时时间
        :return: 已上链返回True，否则返回False
        :raise: 超时查询不到证书抛出 TimeoutError
        """
        if timeout is None:
            timeout = self.tx_check_timeout
        start = time.time()
        err_msg = ''
        while time.time() - start < timeout:
            self.logger.debug('[SDK] 检查 cert_hash="%s"' % cert_hash)
            try:
                return self._check_cert_hash_on_chain(cert_hash)
            except RequestError as ex:
                err_msg = str(ex)
                time.sleep(self.tx_check_interval)
        raise TimeoutError(f'[SDK] 检查 cert_hash="%s" %ss超时: %s' % (cert_hash, self.tx_check_timeout, err_msg))
    
    def add_cert(self, timeout=None, with_sync_result=False) -> TxResponse:
        """添加用户的证书
        :param timeout: 设置请求超时时间
        :param with_sync_result: 同步返回请求结果
        :return: Response
        :raises RequestError: 请求失败
        """
        self.logger.debug("[SDK] begin to AddCert")
        
        payload = self._create_cert_manage_payload(CertManageMethods.CERT_ADD)
        response = self.send_request_with_sync_result(payload, timeout=timeout, with_sync_result=with_sync_result)
        return response
    
    def query_cert(self, cert_hashes: List[str], timeout: int = None) -> CertInfos:
        """查询证书的hash是否已经上链
        :param cert_hashes: 证书hash列表(List)，每个证书hash应转为hex字符串
        :param timeout: 设置请求超时时间
        :return: result_pb2.CertInfos
        :raises 查询不到证书抛出 RequestError
        """
        self.logger.debug("[SDK] begin to QueryCert, [cert_hashes:%s]", cert_hashes)
        
        params = {
            "cert_hashes": ",".join(cert_hashes)
        }
        payload = self.payload_builder.create_query_payload(SystemContractNames.CERT_MANAGE,
                                                            CertManageMethods.CERTS_QUERY,
                                                            params)
        response = self.send_request_with_sync_result(payload, timeout=timeout)
        cert_infos = CertInfos()
        cert_infos.ParseFromString(response.contract_result.result)
        return cert_infos
    
    def delete_cert(self, cert_hashes: List[str], endorse_users: List[EndorsementEntry] = None, timeout=None,
                    with_sync_result=True) -> TxResponse:
        """删除用户的证书
        :param cert_hashes: 证书hash列表, 每个证书hash应转为hex字符串
        :param endorse_users 背书用户,为None时使用self.endorse_users
        :param timeout: 超时时长
        :param with_sync_result: 是否同步返回请求结果
        :return: Response
        :raises RequestError: 请求失败
        """
        self.logger.debug("[SDK] begin to DeleteCert")
        payload = self.create_cert_delete_payload(cert_hashes)
        return self.send_manage_request(payload, endorse_users=endorse_users, timeout=timeout,
                                        with_sync_result=with_sync_result)
        # response = self.send_cert_manage_request(payload, endorsers, timeout=timeout, with_sync_result=with_sync_result)
        # return response
    
    def _create_cert_manage_payload(self, method: str, params: Union[dict, list] = None):
        """创建证书管理payload
        :param method: 方法名。CERTS_FROZEN(证书冻结)/CERTS_UNFROZEN(证书解冻)/CERTS_REVOCATION(证书吊销)
        :param params: 证书管理操作参数，dict格式
        :return: 证书管理payload
        :raises
        """
        
        return self.payload_builder.create_invoke_payload(SystemContractNames.CERT_MANAGE, method, params)
    
    def create_cert_delete_payload(self, cert_hashes: List[str], ) -> TxResponse:
        """生成删除用户的证书待签名Payload
        :param cert_hashes: 证书hash列表, 每个证书hash应转为hex字符串
        :return: Payload
        """
        self.logger.debug("[SDK] begin to create [CertDelete] to be signed payload")
        
        params = {
            "cert_hashes": ",".join(cert_hashes)
        }
        
        return self._create_cert_manage_payload(CertManageMethods.CERTS_DELETE, params)
    
    def create_cert_freeze_payload(self, certs: List[str]):
        """对证书管理的payload 进行签名
        :param certs: 证书列表(List)，证书为证书文件读取后的字符串格式
        :return: Payload

        :raises
        """
        self.logger.debug("[SDK] begin to create [CertFreeze] to be signed payload")
        
        params = {
            "certs": ','.join(certs)
        }
        return self._create_cert_manage_payload(CertManageMethods.CERTS_FREEZE, params)
    
    def create_cert_unfreeze_payload(self, certs: List[str]):
        """对证书管理的payload 进行签名
        :param certs: 证书列表，证书为证书文件读取后的字符串格式
        :return: Payload
        :raises
        """
        self.logger.debug("[SDK] begin to create [CertUnFrozen] to be signed payload")
        
        params = {
            "certs": ','.join(certs)
        }
        return self._create_cert_manage_payload(CertManageMethods.CERTS_UNFREEZE, params)
    
    def create_cert_revoke_payload(self, cert_crl: str):
        """对证书管理的payload 进行签名
        :param cert_crl: 证书吊销列表 文件内容，字符串形式
        :return: Payload
        :raises
        """
        self.logger.debug("[SDK] begin to create [CertManageRevocation] to be signed payload")
        
        params = {
            "cert_crl": cert_crl
        }
        return self._create_cert_manage_payload(CertManageMethods.CERTS_REVOKE, params)
    
    def sign_cert_manage_payload(self, payload) -> EndorsementEntry:
        """
        对证书管理的payload 进行签名
        :param payload_bytes: 待签名的payload字节数组
        :return: paylaod的背书信息
        :raises
        """
        return self.user.endorse(payload)
    
    def send_cert_manage_request(self, payload, endorsers: List[EndorsementEntry], timeout=None,
                                 with_sync_result=False) -> TxResponse:
        """
        发送证书管理请求
        :param payload: 交易payload
        :param endorsers: 背书列表
        :param timeout: 超时时间
        :param with_sync_result: 是否同步交易执行结果。如果不同步，返回tx_id，供异步查询; 同步则循环等待，返回交易的执行结果。
        :return: Response
        :raises RequestError: 请求失败
        """
        response = self.send_request_with_sync_result(payload, endorsers=endorsers, timeout=timeout, with_sync_result=with_sync_result)
        return response
    
    def freeze_cert(self, certs: List[str], endorse_users: List[EndorsementEntry] = None, timeout: int = None,
                    with_sync_result: bool = True)->TxResponse:
        """
        冻结证书
        :param certs: 证书内容列表
        :param endorse_users: 背书用户,为None时使用self.endorse_users
        :param timeout: 超时时间
        :param with_sync_result: 是否同步轮询交易结果
        :return: 交易响应
        """
        payload = self.create_cert_freeze_payload(certs)
        return self.send_manage_request(payload, endorse_users, timeout, with_sync_result)
    
    def unfreeze_cert(self, certs: List[str], endorse_users: List[EndorsementEntry] = None, timeout: int = None,
                      with_sync_result: bool = True)->TxResponse:
        """
        解冻证书
        :param certs: 证书内容
        :param endorse_users: 背书用户
        :param timeout: 超时时间
        :param with_sync_result: 是否同步轮询交易结果
        :return: 交易响应
        """
        payload = self.create_cert_unfreeze_payload(certs)
        return self.send_manage_request(payload, endorse_users, timeout, with_sync_result)
    
    def revoke_cert(self, crt_file: str, ca_key_file: str, ca_crt_file: str,
                    endorse_users: List[EndorsementEntry] = None, timeout: int = None, with_sync_result: bool = True)->TxResponse:
        """
        吊销证书
        :param crt_file: 证书文件路径
        :param ca_key_file: 所属组织ca证书文件路径
        :param ca_crt_file: 所属组织ca私钥文件路径
        :param endorse_users: 背书用户
        :param timeout: 超时时间
        :param with_sync_result: 是否同步轮询交易结果
        :return: 交易响应
        """
        cert_crl = crypto_utils.create_crl_bytes(crt_file, ca_key_file, ca_crt_file)
        payload = self.create_cert_revoke_payload(cert_crl.decode())
        return self.send_manage_request(payload, endorse_users, timeout, with_sync_result)
