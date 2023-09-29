#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# @FileName     :   user.py
# @Function     :   ChainMaker客户端User对象
from typing import Union

from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa

from chainmaker.keys import Defaults, AuthType, HashType
from chainmaker.protos.accesscontrol import member_pb2
from chainmaker.protos.common.request_pb2 import EndorsementEntry
from chainmaker.utils import crypto_utils, file_utils



class User(object):
    """客户端用户"""
    def __init__(self, org_id: str = None,
                 sign_key_bytes: bytes = None,
                 sign_cert_bytes: bytes = None,
                 tls_key_bytes: bytes = None,
                 tls_cert_bytes: bytes = None,
                 auth_type: AuthType = None,
                 hash_type: HashType = None,
                 alias: str = None):
        """
        客户端用户对象初始化方法
        :param org_id: 组织ID, 在Public模式下允许为空
        :param sign_key_bytes: PEM格式用户签名私钥文件二进制内容
        :param sign_cert_bytes: PEM格式用户签名证书文件二进制内容
        :param tls_key_bytes: PEM格式用户tls私钥文件二进制内容
        :param tls_cert_bytes: PEM格式用户tls证书文件二进制内容
        :param auth_type: 授权类型，默认为AuthType.PermissionedWithCert
        :param hash_type: 哈希类型，默认为HashType.SHA256
        :param alias: 证书别名，默认为None
        """
        self.org_id = org_id
        self.sign_key_bytes = sign_key_bytes
        self.sign_cert_bytes = sign_cert_bytes
        self.tls_key_bytes = tls_key_bytes
        self.tls_cert_bytes = tls_cert_bytes
        self.auth_type = auth_type or Defaults.AUTH_TYPE
        self.hash_type = hash_type or Defaults.HASH_TYPE
        self.alias = alias
        
        self.sign_key = serialization.load_pem_private_key(self.sign_key_bytes, password=None)
        self.sign_cert = x509.load_pem_x509_certificate(self.sign_cert_bytes) if self.sign_cert_bytes else None
        self.tls_key = serialization.load_pem_private_key(self.tls_key_bytes, password=None) if self.tls_key_bytes else None
        self.tls_cert = x509.load_pem_x509_certificate(self.tls_cert_bytes) if self.tls_cert_bytes else None
        
        self.sign_cert_hash = b''
        self.enabled_alias = Defaults.ENABLED_ALIAS
        self.enabled_crt_hash = Defaults.ENABLED_CRT_HASH

        # 额外属性，可以用于给该属性赋值以标识用户
        self.user_id = None
        self.user_role = None
    
    def __repr__(self):
        return f'<{self.user_id}>' if self.user_id else '<User>'
        # return f'<User org_id={self.org_id}>' if self.org_id else '<User>'
    
    def __eq__(self, other):
        if hasattr(other, 'sign_key_bytes'):
            return self.sign_key_bytes == other.sign_key_bytes
        return False
    
    @classmethod
    def from_conf(cls, org_id: str = "",
                  user_sign_key_file_path: str = None,
                  user_sign_crt_file_path: str = None,
                  user_key_file_path: str = None,
                  user_crt_file_path: str = None,
                  crypto: dict = None,
                  auth_type: AuthType = None,
                  alias: str = None):
        
        sign_key_bytes = file_utils.read_file_bytes(user_sign_key_file_path)
        sign_cert_bytes = file_utils.read_file_bytes(user_sign_crt_file_path)
        tls_key_bytes = file_utils.read_file_bytes(user_key_file_path)
        tls_cert_bytes = file_utils.read_file_bytes(user_crt_file_path)
        
        user = cls(org_id, sign_key_bytes, sign_cert_bytes, tls_key_bytes, tls_cert_bytes)
        
        if isinstance(crypto, dict):
            user.hash_type = crypto.get('hash') or Defaults.HASH_TYPE
        
        if isinstance(auth_type, str) and auth_type.lower() == 'public':
            user.auth_type = AuthType.Public
        elif isinstance(auth_type, str) and auth_type.lower() == 'permissionedwithkey':
            user.auth_type = AuthType.PermissionedWithKey
        else:
            user.auth_type = Defaults.AUTH_TYPE
        
        if isinstance(alias, str):  # 证书别名
            user.alias = alias
        
        return user
    
    # 生成背书
    def endorse(self, payload_bytes: bytes) -> EndorsementEntry:
        """
        生成背书
        :param payload_bytes: payload.SerializeToString() 序列化后的payload bytes数据
        :param enabled_crt_hash: 是否只用证书的hash值
        :return:
        """
        sign_bytes = crypto_utils.sign(self.sign_key, self.sign_cert, payload_bytes,
                                       auth_type=self.auth_type, hash_type=self.hash_type)
        
        # 构造sender
        if self.auth_type == AuthType.PermissionedWithCert:
            # 使用别名
            if self.enabled_alias is True and isinstance(self.alias, str) and len(self.alias) > 0:
                member_type, member_info = member_pb2.MemberType.ALIAS, self.alias.encode()
            
            elif self.enabled_crt_hash is True and isinstance(self.cert_hash, bytes) and len(self.cert_hash) > 0:
                member_type, member_info = member_pb2.MemberType.CERT_HASH, self.cert_hash
            else:
                member_type, member_info = member_pb2.MemberType.CERT, self.sign_cert_bytes
        else:
            member_type, member_info = member_pb2.MemberType.PUBLIC_KEY, self.public_bytes
        
        signer = member_pb2.Member(
            org_id=self.org_id,
            member_info=member_info,
            member_type=member_type,
        )
        
        sender = EndorsementEntry(
            signer=signer,
            signature=sign_bytes,
        )
        return sender
    
    @property
    def certificate(self) -> x509.Certificate:
        return self.sign_cert
    
    @property
    def private_key(self) -> Union[rsa.RSAPrivateKey, ec.EllipticCurvePrivateKey]:
        return self.sign_key
    
    @property
    def public_key(self) -> Union[rsa.RSAPublicKey, ec.EllipticCurvePublicKey]:
        return self.private_key.public_key()
    
    @property
    def public_bytes(self):
        return self.public_key.public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo)
    
    def get_cert_hash(self, hash_type: HashType = None) -> bytes:
        """
        更加哈希类型设置当前证书哈希
        :param hash_type:
        :return:
        """
        hash_type = hash_type or self.hash_type
        self.sign_cert_hash = crypto_utils.get_cert_hash(self.sign_cert, hash_type)
        return self.sign_cert_hash
    @property
    def cert_hash(self) -> bytes:
        """获取证书哈希"""
        if not self.sign_cert_hash:
            self.get_cert_hash(self.hash_type)
        return self.sign_cert_hash
    
    @cert_hash.setter
    def cert_hash(self, cert_hash: bytes) -> None:
        """获取证书哈希"""
        self.sign_cert_hash = cert_hash
    
    def get_address(self, addr_type: int = 1) -> str:
        """返回账户地址"""
        assert addr_type in [0, 1], 'addr_type仅支持0'
        if addr_type == 0:
            return crypto_utils.get_evm_address_from_public_key(self.public_key)
        else:
            return crypto_utils.get_zx_address_from_public_key(self.public_key)
