#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# @FileName     :   user.py
# @Function     :   ChainMaker客户端User对象
from typing import Optional, Union

from cryptography import x509
from cryptography.exceptions import UnsupportedAlgorithm
from cryptography.hazmat._oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa

from chainmaker.exceptions import ChainClientException
from chainmaker.keys import AddrType, AuthType, Defaults, HashType
from chainmaker.protos.accesscontrol import member_pb2
from chainmaker.protos.accesscontrol.member_pb2 import Member, MemberType
from chainmaker.protos.common.request_pb2 import EndorsementEntry, Payload
from chainmaker.utils import crypto_utils, file_utils
from chainmaker.utils.crypto_utils import load_pem_private_key, load_pem_x509_certificate


class User(object):
    """客户端用户"""

    def __init__(self, org_id: str = None,
                 sign_key_bytes: bytes = None,
                 sign_cert_bytes: bytes = None,
                 tls_key_bytes: bytes = None,
                 tls_cert_bytes: bytes = None,
                 auth_type: AuthType = None,
                 hash_type: HashType = None,
                 alias: str = None,
                 key_pwd: str = None,
                 sign_key_pwd: str = None,
                 enc_key_bytes: bytes = None,
                 enc_cert_bytes: bytes = None,
                 enc_key_pwd: str = None,
                 enable_normal_key: bool = None
                 ):
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

        self.alias = alias
        self.enc_key_bytes = enc_key_bytes
        self.enc_cert_bytes = enc_cert_bytes

        self.enable_normal_key = enable_normal_key  # v2.3.0 新增 todo 怎么用

        self.sign_key = load_pem_private_key(self.sign_key_bytes, password=sign_key_pwd)
        self.sign_cert = load_pem_x509_certificate(self.sign_cert_bytes)
        self.tls_key = load_pem_private_key(self.tls_key_bytes, password=key_pwd)
        self.tls_cert = load_pem_x509_certificate(self.tls_cert_bytes)
        self.enc_key = load_pem_private_key(self.enc_key_bytes, password=enc_key_pwd)
        self.enc_cert = load_pem_x509_certificate(self.enc_cert_bytes)

        self.sign_cert_hash = b''
        self.enabled_alias = Defaults.ENABLED_ALIAS
        self.enabled_crt_hash = Defaults.ENABLED_CRT_HASH

        # 额外属性，可以用于给该属性赋值以标识用户
        self.addr_type = None
        self._hash_type = hash_type

    def __repr__(self):
        return f'<User {self.member_id}>'

    def __eq__(self, other):
        if hasattr(other, 'member_id'):
            return self.member_id == other.member_id
        return False

    @classmethod
    def from_conf(cls, org_id: str = "",
                  user_sign_key_file_path: str = None,
                  user_sign_crt_file_path: str = None,
                  user_sign_key_pwd: str = None,
                  user_key_file_path: str = None,
                  user_crt_file_path: str = None,
                  user_key_pwd: str = None,
                  user_enc_key_file_path: str = None,
                  user_enc_crt_file_path: str = None,
                  user_enc_key_pwd: str = None,
                  crypto: dict = None,
                  auth_type: Union[AuthType, str] = None,
                  alias: str = None,
                  enable_normal_key: bool = None,
                  ):

        sign_key_bytes = file_utils.read_file_bytes(user_sign_key_file_path)
        sign_cert_bytes = file_utils.read_file_bytes(user_sign_crt_file_path) if user_sign_crt_file_path else None
        tls_key_bytes = file_utils.read_file_bytes(user_key_file_path) if user_key_file_path else None
        tls_cert_bytes = file_utils.read_file_bytes(user_crt_file_path) if user_crt_file_path else None

        enc_key_bytes = file_utils.read_file_bytes(user_enc_key_file_path) if user_enc_key_file_path else None
        enc_cert_bytes = file_utils.read_file_bytes(user_enc_crt_file_path) if user_enc_crt_file_path else None

        user = cls(org_id=org_id,
                   sign_key_bytes=sign_key_bytes,
                   sign_cert_bytes=sign_cert_bytes,
                   tls_key_bytes=tls_key_bytes,
                   tls_cert_bytes=tls_cert_bytes,
                   enc_key_bytes=enc_key_bytes,
                   enc_cert_bytes=enc_cert_bytes,
                   sign_key_pwd=user_sign_key_pwd,
                   key_pwd=user_key_pwd,
                   enc_key_pwd=user_enc_key_pwd,
                   enable_normal_key=enable_normal_key,
                   )

        if isinstance(crypto, dict):
            user._hash_type = crypto.get('hash')

        if isinstance(auth_type, str) and auth_type.lower() == 'public':
            user.auth_type = AuthType.Public
        elif isinstance(auth_type, str) and auth_type.lower() == 'permissionedwithkey':
            user.auth_type = AuthType.PermissionedWithKey
        else:
            user.auth_type = Defaults.AUTH_TYPE

        if isinstance(alias, str):  # 证书别名
            user.alias = alias

        return user

    def sign(self, payload: Payload) -> bytes:
        """
        v2.3.0 新增
        :param payload:
        :return:
        """
        return self._sign(payload.SerializeToString())

    def _sign(self, payload_bytes: bytes) -> bytes:
        """
        v2.3.0 新增
        :param payload_bytes:
        :return:
        """
        signature = crypto_utils.sign(self.sign_key, self.sign_cert, payload_bytes,
                                      auth_type=self.auth_type, hash_type=self.hash_type)
        return signature

    # 生成背书
    def endorse(self, payload_bytes: bytes) -> EndorsementEntry:
        """
        生成背书
        :param payload_bytes: payload.SerializeToString() 序列化后的payload bytes数据
        :return:
        """
        signature = self._sign(payload_bytes)

        # 构造sender
        if self.auth_type == AuthType.PermissionedWithCert:
            # 使用别名
            if self.enabled_alias is True and isinstance(self.alias, str) and len(self.alias) > 0:
                member_type, member_info = member_pb2.MemberType.ALIAS, self.alias.encode()

            elif self.enabled_crt_hash is True and isinstance(self.cert_hash, bytes) and len(
                    self.cert_hash) > 0:
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
            signature=signature,
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
    
    def get_address(self, addr_type: Union[int, AddrType, str] = 2) -> str:
        """
        返回账户地址
        v2.3.0 修改
        :param addr_type: 地址类型 0-长安链 1-至信链 2-以太坊
        :return: 40位长安链地址 或 42位至信链地址(ZX开头) 或 42位以太坊地址(0x开头)
        """
        if addr_type == AddrType.ETHEREUM:
            return crypto_utils.get_evm_address_from_public_key(self.public_key)
        if addr_type == AddrType.ZXL:
            return crypto_utils.get_zxl_address_from_public_key(self.public_key, hash_type=HashType.SM3)
        return crypto_utils.get_chainmaker_address_from_public_key(self.public_key, self.hash_type)

    @property
    def address(self) -> str:
        """用户账户地址
        v2.3.0 新增
        """
        if self.addr_type is None:
            raise ChainClientException('user.addr_type not set')
        return self.get_address(self.addr_type)

    @property
    def uid(self) -> str:
        """
        用户Id, 即ski(subject key identifier)
        v2.3.0 新增
        :return: hex字符串
        """
        if self.certificate:
            return crypto_utils.get_ski_from_cert(self.certificate)
        return crypto_utils.get_ski_from_public_key(self.public_key)

    @property
    def member_id(self) -> str:
        """从用户签名证书或公钥中获取用户通用名称
        v2.3.0 新增
        """
        if self.certificate:
            subject = self.certificate.subject
            return subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
        return self.public_bytes.decode()

    @property
    def hash_type(self) -> HashType:
        """哈希类型"""
        if self._hash_type is None and self.certificate:
            try:
                hash_type = self.certificate.signature_hash_algorithm
            except UnsupportedAlgorithm as ex:
                if '1.2.156.10197.1.501' in str(ex):
                    hash_type = hashes.SM3()
                else:
                    raise
            self._hash_type = hash_type.__class__.__name__
        return self._hash_type

    @property
    def role(self) -> Optional[str]:
        """从用户(签名)证书中获取用户角色
        v2.3.0 新增
        """
        if self.certificate:
            subject = self.certificate.subject
            return subject.get_attributes_for_oid(NameOID.ORGANIZATIONAL_UNIT_NAME)[0].value.upper()

    @property
    def member_info(self) -> bytes:
        """
        用户证书或公钥二进制信息
        v2.3.0 新增
        :return:
        """
        if self.member_type == MemberType.ALIAS:  # 证书别名模式
            return self.alias.encode()
        if self.member_type == MemberType.CERT_HASH:  # 证书哈希(短证书)模式
            return self.cert_hash
        if self.member_type == MemberType.CERT:  # 证书模式
            return self.sign_cert_bytes
        else:  # 公钥模式
            return self.public_bytes

    @property
    def member_type(self) -> MemberType:
        """
        v2.3.0 新增
        :return:
        """
        if self.auth_type == AuthType.PermissionedWithCert:
            if self.enabled_alias is True and isinstance(self.alias, str) and len(self.alias) > 0:
                return MemberType.ALIAS
            if self.enabled_crt_hash is True and len(self.cert_hash) > 0:
                return MemberType.CERT_HASH
            return MemberType.CERT
        else:
            return MemberType.PUBLIC_KEY

    @property
    def member(self) -> Member:
        """签名者
        v2.3.0 新增
        """
        signer = Member(org_id=self.org_id, member_info=self.member_info, member_type=self.member_type.value)
        return signer


class Signer(User):
    """客户端签名用户"""
