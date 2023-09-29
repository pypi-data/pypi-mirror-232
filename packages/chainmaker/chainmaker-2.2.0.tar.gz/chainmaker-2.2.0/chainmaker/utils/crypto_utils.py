#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# @FileName     :   crypto_utils.py
# @Function     :   读取证书、密钥文件、生成数字签名
import os
from datetime import datetime, timedelta
from typing import Union, List
from hashlib import sha256

import sha3
import asn1
from cryptography import x509  # pip install cryptography
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from cryptography.hazmat.primitives.asymmetric import padding

from chainmaker.utils.gm import sm3


def load_cert_file(cert_file_path: str) -> (x509.Certificate, bytes):
    """
    加载PEM证书文件
    :param cert_file_path: 证书文件路径
    :return: 证书对象及证书二进制内容
    """
    if cert_file_path is None:
        return None, None
    if not os.path.exists(cert_file_path):
        raise FileNotFoundError('证书文件路径 %s 不存在' % cert_file_path)
    
    with open(cert_file_path, "rb") as f:
        cert_bytes = f.read()
    cert = x509.load_pem_x509_certificate(cert_bytes)
    return cert, cert_bytes


def load_key_file(key_file_path: str) -> (Union[ec.EllipticCurvePrivateKey, rsa.RSAPrivateKey], bytes):
    """
    加载PEM私钥文件
    :param key_file_path: key文件路径
    :return:
    """
    if key_file_path is None:
        return None, None
    if not os.path.exists(key_file_path):
        raise FileNotFoundError('私钥文件路径 %s 不存在' % key_file_path)
    with open(key_file_path, "rb") as f:
        key_bytes = f.read()
    key = serialization.load_pem_private_key(key_bytes, password=None)
    return key, key_bytes


def load_public_key_file(key_file_path: str) -> Union[ec.EllipticCurvePublicKey, rsa.RSAPublicKey]:
    """加载PEM公钥文件"""
    with open(key_file_path, "rb") as f:
        key_bytes = f.read()
    return serialization.load_pem_public_key(key_bytes)


def sign_with_cert(key: ec.EllipticCurvePrivateKey, cert: x509.Certificate, msg: bytes):
    """使用证书签名+私钥签名"""
    # return key.sign(msg, padding=padding.PKCS1v15(), algorithm=hashes.SHA256())
    return key.sign(msg, ec.ECDSA(cert.signature_hash_algorithm))


def sign_with_key(key, msg: bytes):  # Fixme  EC 私钥签名
    """公钥模式使用RSA key签名"""
    return key.sign(msg, padding=padding.PKCS1v15(), algorithm=hashes.SHA256())


def sign_with_rsa_key(key: rsa.RSAPrivateKey, data: bytes, auth_type='SHA256'):
    """使用RSA私钥签名"""
    if auth_type == 'SHA256':
        return key.sign(data, padding=padding.PKCS1v15(), algorithm=hashes.SHA256())


def sign(key: Union[ec.EllipticCurvePrivateKey, rsa.RSAPrivateKey],
         cert: x509.Certificate, msg: bytes, auth_type=None, hash_type=None):
    """
    对信息进行签名
    :param key: 密钥对象
    :param cert: 证书对象
    :param msg: 待签名信息 payload_bytes
    :param auth_type:
    :return: 签名后的信息
    """
    if cert is not None:
        signature_hash_algorithm = cert.signature_hash_algorithm
    else:
        signature_hash_algorithm = hashes.SHA256()  # TODO 非SHA256
    
    if isinstance(key, ec.EllipticCurvePrivateKey):  # EC key
        return key.sign(msg, ec.ECDSA(signature_hash_algorithm))  # TODO 非SHA256
    elif isinstance(key, rsa.RSAPrivateKey):  # RSA key
        return key.sign(msg, padding=padding.PKCS1v15(), algorithm=signature_hash_algorithm)
    else:
        raise NotImplementedError('目前仅支持EC和RSA私钥')


def get_cert_hash(cert: x509.Certificate, hash_type='SHA256') -> bytes:
    """根据证书生成证书哈希"""
    if cert is None:
        return b''
    if hash_type == 'SHA256':
        return cert.fingerprint(hashes.SHA256())
    raise NotImplementedError('目前仅支持SHA256')


def create_crl_bytes(crt_file: str, ca_key_file: str, ca_crt_file: str) -> bytes:
    """
    创建吊销证书列表文件二进制数据
    :param crt_file: 原客户端证书文件 eg ./crypto-config/wx-org2.chainmaker.org/user/client1/client1.tls.crt'
    :param ca_key_file: 同组织根证书私钥文件 eg. ./crypto-config/wx-org2.chainmaker.org/ca/ca.key
    :param ca_crt_file: 同组织跟证书文件 eg. ./crypto-config/wx-org2.chainmaker.org/ca/ca.crt
    :return: 生成的crl文件二进制内容
    """
    revocation_date_timestamp = 1711206185
    now = datetime.now()
    next_update_duration = dict(hours=4)
    
    ca_crt, _ = load_cert_file(ca_crt_file)
    ca_key, _ = load_key_file(ca_key_file)
    revoked_crt, _ = load_cert_file(crt_file)
    
    revoked_cert = x509.RevokedCertificateBuilder(
        revoked_crt.serial_number,
        datetime.fromtimestamp(revocation_date_timestamp),
    ).build()
    
    builder = x509.CertificateRevocationListBuilder(
        issuer_name=ca_crt.issuer,
        last_update=now,
        next_update=now + timedelta(**next_update_duration),
        revoked_certificates=[revoked_cert],
    )
    
    ski_ext = ca_crt.extensions.get_extension_for_class(x509.SubjectKeyIdentifier)
    identifier = x509.AuthorityKeyIdentifier.from_issuer_subject_key_identifier(ski_ext.value)
    builder = builder.add_extension(identifier, critical=False)
    
    crl = builder.sign(private_key=ca_key, algorithm=hashes.SHA256())
    
    public_bytes = crl.public_bytes(encoding=serialization.Encoding.PEM)
    return public_bytes


def load_crl_file(crl_file) -> x509.CertificateRevocationList:
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
    key, _ = load_key_file(private_key_file)
    public_key_bytes = key.public_key().public_bytes(serialization.Encoding.PEM,
                                                     serialization.PublicFormat.PKCS1)
    return public_key_bytes


def get_address_from_private_key_file(private_key_file: str, addr_type=1):
    """根据私钥文件生成地址 # 0-ChainMaker; 1-ZXL"""
    private_key, _ = load_key_file(private_key_file)
    pk = private_key.public_key()
    if addr_type == 0:
        return get_evm_address_from_public_key(pk)
    elif addr_type == 1:
        return get_zx_address_from_public_key(pk)
    raise NotImplementedError('addr_type仅支持 0-ChainMaker; 1-ZXL')
    

def asn1_load(data: bytes)->list:
    """加载asn1序列化内容构造签名对象"""
    result = []
    dec = asn1.Decoder()
    dec.start(data)
    dec.enter()
    line = dec.read()
    while line is not None:
        tag, value = line
        result.append(value)
        line = dec.read()
    return result


def ans1_dump(*args: List[int])->bytes:
    enc = asn1.Encoder()
    enc.start()
    enc.enter(asn1.Numbers.Sequence)
    for number in args:
        enc.write(number)
    enc.leave()
    res = enc.output()
    return res


def get_evm_address_from_public_key(pk: Union[ec.EllipticCurvePublicKey, rsa.RSAPublicKey]):
    """根据公钥生成地址"""
    pk_der_bytes = pk.public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)
    ski = sha256(pk_der_bytes[24:]).hexdigest()
    hex = sha3.keccak_256()
    hex.update(bytes.fromhex(ski))
    return '0x' + hex.hexdigest()[24:]


def get_zx_address_from_public_key(pk: Union[rsa.RSAPublicKey, ec.EllipticCurvePublicKey]):
    """根据公钥生成至信链地址"""
    pk_numbers = pk.public_numbers()
    if isinstance(pk, rsa.RSAPublicKey):
        n = pk_numbers.n
        e = pk_numbers.e
        pk_der_bytes = ans1_dump(n, e)
    elif isinstance(pk, ec.EllipticCurvePublicKey):
        x = pk_numbers.x
        y = pk_numbers.y
        ret = '04%32x%32x' % (x, y)
        pk_der_bytes = bytes.fromhex(ret)  # todo pk.key_size
    else:
        raise NotImplementedError('仅支持rsa及ec公钥')
    digest = sm3.sm3_hash(pk_der_bytes)
    return 'ZX%s' % digest[:40]


if __name__ == '__main__':
    r = get_address_from_private_key_file('/Users/superhin/Projects/chainmaker-go/build/crypto-config/node1/admin/admin1/admin1.key')
    print(r)
