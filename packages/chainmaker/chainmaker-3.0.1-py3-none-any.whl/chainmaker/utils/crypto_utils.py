#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# @FileName     :   crypto_utils.py
# @Function     :   读取证书、密钥文件、生成数字签名
import os
import warnings
from datetime import datetime, timedelta
from pathlib import Path
from typing import Union, List

import asn1
from cryptography import x509  # pip install cryptography
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from cryptography.hazmat.primitives.asymmetric import padding

from chainmaker.keys import HashType, Certificate, PrivateKey, PublicKey
from chainmaker.utils import sm2, file_utils

HASH_ALGO_MAP = {'SHA256': hashes.SHA256(), 'SHA3_256': hashes.SHA3_256(), 'SM3': hashes.SM3()}


def load_pem_cert(cert_bytes_or_file_path: Union[Path, str, bytes]) -> Union[Certificate, None]:
    """加载PEM格式证书-支持国密"""
    if not cert_bytes_or_file_path:
        return None
    cert_bytes = cert_bytes_or_file_path
    if isinstance(cert_bytes_or_file_path, (Path, str)):
        cert_bytes = file_utils.read_file_bytes(cert_bytes_or_file_path)
    return x509.load_pem_x509_certificate(cert_bytes)


def load_pem_private_key(key_bytes_or_file_path: Union[Path, str, bytes], password=None) -> Union[PrivateKey, None]:
    if not key_bytes_or_file_path:
        return None
    key_bytes = key_bytes_or_file_path
    if isinstance(key_bytes_or_file_path, (Path, str)):
        key_bytes = file_utils.read_file_bytes(key_bytes_or_file_path)
    try:
        return serialization.load_pem_private_key(key_bytes, password=password)
    except Exception as ex:
        print(ex)
        return sm2.Sm2PrivateKey.from_pem(key_bytes)


def load_pem_public_key(key_bytes_or_file_path: Union[Path, str, bytes]) -> PublicKey:
    """加载PEM公钥文件"""
    warnings.warn('will be removed for not used', DeprecationWarning)
    key_bytes = key_bytes_or_file_path
    if isinstance(key_bytes_or_file_path, (Path, str)):
        key_bytes = file_utils.read_file_bytes(key_bytes_or_file_path)
    return serialization.load_pem_public_key(key_bytes)


# def load_public_key_file(key_file_path: str) -> Sm2PublicKey:
#     """加载PEM公钥文件"""
#     warnings.warn('请使用crypto_utils.load_pem_public_key', DeprecationWarning)
#     return load_pem_public_key(key_file_path)
#
#
# def load_cert_file(cert_file_path: str) -> (Certificate, bytes):
#     """
#     加载PEM证书文件
#     :param cert_file_path: 证书文件路径
#     :return: 证书对象及证书二进制内容
#     """
#     warnings.warn('请使用crypto_utils.load_pem_cert', DeprecationWarning)
#     if cert_file_path is None:
#         return None, None
#     if not os.path.exists(cert_file_path):
#         raise FileNotFoundError('证书文件路径 %s 不存在' % cert_file_path)
#
#     with open(cert_file_path, "rb") as f:
#         cert_bytes = f.read()
#     cert_or_cert_bytes = x509.load_pem_x509_certificate(cert_bytes)
#     return cert_or_cert_bytes, cert_bytes
#
#
# def load_key_file(key_file_path: str) -> (Sm2PrivateKey, bytes):
#     """
#     加载PEM私钥文件
#     :param key_file_path: key文件路径
#     :return:
#     """
#     warnings.warn('请使用crypto_utils.load_pem_key', DeprecationWarning)
#     if key_file_path is None:
#         return None, None
#     if not os.path.exists(key_file_path):
#         raise FileNotFoundError('私钥文件路径 %s 不存在' % key_file_path)
#     with open(key_file_path, "rb") as f:
#         key_bytes = f.read()
#     key = serialization.load_pem_private_key(key_bytes, password=None)
#     return key, key_bytes


def sign_with_cert(key: PrivateKey, cert: Certificate, msg: bytes):
    """使用证书签名+私钥签名"""
    # return key._sign(msg_digest, padding=padding.PKCS1v15(), algorithm=hashes.SHA256())
    warnings.warn('will be removed for not used', DeprecationWarning)
    return key.sign(msg, ec.ECDSA(cert.signature_hash_algorithm))


def sign_with_key(key: PrivateKey, msg: bytes,
                  auth_type=HashType.SHA256):  # Fixme  EC 私钥签名
    """公钥模式使用 key签名"""
    warnings.warn('will be removed for not used', DeprecationWarning)
    if auth_type != HashType.SHA256:
        raise NotImplementedError('暂时只支持SHA256')
    if isinstance(key, rsa.RSAPrivateKey):
        return key.sign(msg, padding=padding.PKCS1v15(), algorithm=hashes.SHA256())
    else:
        return key.sign(msg, signature_algorithm=ec.ECDSA(hashes.SHA256()))


def _sign_with_private_key(key: PrivateKey, hash_algo: hashes.HashAlgorithm, msg: bytes) -> bytes:
    """使用私钥签名消息"""
    if isinstance(key, ec.EllipticCurvePrivateKey):  # EC key
        return key.sign(msg, ec.ECDSA(hash_algo))
    elif isinstance(key, rsa.RSAPrivateKey):  # RSA key
        return key.sign(msg, padding=padding.PKCS1v15(), algorithm=hash_algo)
    elif isinstance(key, sm2.Sm2PrivateKey):
        return key.sign_with_sm3(msg).asn1_dump()
    else:
        # todo SM3
        raise NotImplementedError('目前仅支持EC和RSA私钥')


def sign(key: PrivateKey, cert: Certificate, msg: bytes, hash_type: HashType = None) -> bytes:
    """
    对信息进行签名
    :param key: 密钥对象
    :param cert: 证书对象， 可以为None
    :param msg: 待签名信息 payload_bytes
    :param hash_type: 哈希类型
    :return: 签名后的信息
    """
    if cert is not None:
        hash_algo = cert.signature_hash_algorithm
    else:
        hash_algo = HASH_ALGO_MAP.get(hash_type.name, hashes.SHA256())

    return _sign_with_private_key(key, hash_algo, msg)


def get_cert_hash_bytes(cert: Certificate) -> bytes:
    """根据证书生成证书哈希"""
    if cert is None:
        return b''
    hash_algo = cert.signature_hash_algorithm
    return cert.fingerprint(hash_algo)


def create_crl_bytes(cert_bytes_or_file_path: Union[Path, str, bytes, list],
                     ca_key_bytes_or_file_path: Union[Path, str, bytes],
                     ca_crt_bytes_or_file_path: Union[Path, str, bytes],
                     revocation_date_timestamp=1711206185) -> bytes:
    """
    创建吊销证书列表文件二进制数据
    :param revocation_date_timestamp:
    :param cert_bytes_or_file_path: 原客户端证书文件 eg ./crypto-config/wx-org2.chainmaker.org/user_full_name/client1/client1.tls.crt'
    :param ca_key_bytes_or_file_path: 同组织根证书私钥文件 eg. ./crypto-config/wx-org2.chainmaker.org/ca/ca.key
    :param ca_crt_bytes_or_file_path: 同组织跟证书文件 eg. ./crypto-config/wx-org2.chainmaker.org/ca/ca.crt
    :return: 生成的crl文件二进制内容
    """
    now = datetime.now()
    next_update_duration = dict(hours=4)  # todo arg

    ca_crt = load_pem_cert(ca_crt_bytes_or_file_path)
    ca_key = load_pem_private_key(ca_key_bytes_or_file_path)

    certs = cert_bytes_or_file_path if isinstance(cert_bytes_or_file_path, list) else [cert_bytes_or_file_path]

    revoked_certs = []
    for cert_bytes in certs:
        revoked_crt = load_pem_cert(cert_bytes)

        revoked_cert = x509.RevokedCertificateBuilder(
            revoked_crt.serial_number,
            datetime.fromtimestamp(revocation_date_timestamp),
        ).build()
        revoked_certs.append(revoked_cert)

    builder = x509.CertificateRevocationListBuilder(
        issuer_name=ca_crt.issuer,
        last_update=now,
        next_update=now + timedelta(**next_update_duration),
        revoked_certificates=revoked_certs,
    )

    ski_ext = ca_crt.extensions.get_extension_for_class(x509.SubjectKeyIdentifier)
    identifier = x509.AuthorityKeyIdentifier.from_issuer_subject_key_identifier(ski_ext.value)
    builder = builder.add_extension(identifier, critical=False)

    crl = builder.sign(private_key=ca_key, algorithm=hashes.SHA256())

    public_bytes = crl.public_bytes(encoding=serialization.Encoding.PEM)
    return public_bytes


def load_crl_file(crl_file: Union[Path, str]) -> x509.CertificateRevocationList:
    """
    读取crl文件，生成CertificateRevocationList对象
    :param crl_file: 吊销证书crl文件
    :return: CertificateRevocationList对象
    """
    with open(crl_file, 'rb') as f:
        data = f.read()
    return x509.load_pem_x509_crl(data)


def merge_cert_pems(ca_paths: list) -> bytes:
    """
    连接多个证书内容
    :param ca_paths: ca证书文件路径列表
    :return: 连接后的bytes数据
    """
    ca_certs = []
    for ca_path in ca_paths:
        for file in os.listdir(ca_path):
            if file.endswith(".crt"):
                with open(os.path.join(ca_path, file), 'rb') as f:
                    ca_cert = f.read()
                    ca_certs.append(ca_cert)
    return b''.join(ca_certs)


def get_public_key_bytes(private_key_file: str) -> bytes:
    """
    从Public模式私钥中获取公钥二进制数据
    :param private_key_file: 私钥文件路径，eg. "./testdata/crypto-config/node1/admin/admin1/admin1.key"
    :return:
    """
    warnings.warn('will be removed for not used', DeprecationWarning)
    key = load_pem_private_key(private_key_file)
    public_key_bytes = key.public_key().public_bytes(serialization.Encoding.PEM,
                                                     serialization.PublicFormat.PKCS1)
    return public_key_bytes


# def get_address_from_private_key_file(private_key_file: str, addr_type=1):
#     """根据私钥文件生成地址 # 0-ChainMaker; 1-ZXL"""
#     warnings.warn('即将废弃,请使用chainmaker.utils.address_utils.get_address_from_private_key_pem', DeprecationWarning)
#     private_key, _ = load_key_file(private_key_file)
#     pk = private_key.public_key()
#     if addr_type == 0:
#         return get_evm_address_from_public_key(pk)
#     elif addr_type == 1:
#         return get_zx_address_from_public_key(pk)
#     raise NotImplementedError('addr_type仅支持 0-ChainMaker; 1-ZXL')


def asn1_load(data: bytes) -> list:
    """加载asn1序列化内容构造签名对象"""
    warnings.warn('will be removed by use pyasn1', DeprecationWarning)
    result = []
    dec = asn1.Decoder()
    dec.start(data)
    dec.enter()
    line = dec.read()
    while line is not None:
        tag, value = line
        if tag.typ == asn1.Types.Primitive:
            result.append(value)
        elif tag.typ == asn1.Types.Constructed:
            result.append(asn1_load)
        line = dec.read()
    return result


def ans1_dump(*args: List[int]) -> bytes:
    warnings.warn('will be removed by use pyasn1', DeprecationWarning)
    enc = asn1.Encoder()
    enc.start()
    enc.enter(asn1.Numbers.Sequence)
    for number in args:
        enc.write(number)
    enc.leave()
    res = enc.output()
    return res

# def _calc_address_from_ski(ski: str) -> str:
#     """
#     通过ski计算地址
#     :param ski: 16进制SubjectKeyIdentifier值
#     :return: 40位地址
#     """
#     addr = sha3.keccak_256()
#     addr.switch_branch(bytes.fromhex(ski))
#     addr = addr.hexdigest()[24:]
#     return addr


# def get_evm_address_from_public_key(pk: Sm2PublicKey, hash_type: HashType = HashType.SHA256):
#     """
#     根据公钥生成以太坊-EVM地址
#     :param pk: 公钥对象
#     :return: 42位地址
#     """
#     warnings.warn('即将废弃,请使用chainmaker.utils.address_utils.get_ethereum_address_from_public_key', DeprecationWarning)
#     pk_der_bytes = pk.public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)
#     if hash_type == HashType.SHA256:
#         ski = sha256(pk_der_bytes[24:]).hexdigest()
#         return '0x%s' % _calc_address_from_ski(ski)
#     raise NotImplementedError('目前仅支持SHA256')
#
#
# def get_zx_address_from_public_key(pk: Sm2PublicKey):
#     """
#     根据公钥生成至信链地址
#     :param pk: 公钥对象
#     :return: 42位地址
#     """
#     warnings.warn('即将废弃,请使用chainmaker.utils.address_utils.get_zxl_address_from_public_key', DeprecationWarning)
#     pk_numbers = pk.public_numbers()
#     if isinstance(pk, rsa.RSAPublicKey):
#         n = pk_numbers.n
#         e = pk_numbers.e
#         pk_der_bytes = ans1_dump(n, e)
#     elif isinstance(pk, ec.EllipticCurvePublicKey):
#         x = pk_numbers.x
#         y = pk_numbers.y
#         ret = '04%32x%32x' % (x, y)
#         pk_der_bytes = bytes.fromhex(ret)  # todo pk.key_size
#     else:
#         raise NotImplementedError('仅支持rsa及ec公钥')
#
#     digest = sm3.sm3_hash(pk_der_bytes)
#
#     return 'ZX%s' % digest[:40]
