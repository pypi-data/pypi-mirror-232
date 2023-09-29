#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# @FileName     :   test_cert_manage.py
# @Function     :   测试证书管理接口

import os

import allure
from cryptography.hazmat.primitives import serialization

from chainmaker.utils.result_utils import result_is_ok
from chainmaker.utils.crypto_utils import create_crl_bytes, load_crl_file
from google.protobuf import json_format


@allure.feature('证书管理')
class TestCertManage:
    @allure.story('获取证书哈希')
    def test_get_cert_hash(self, cc):
        assert cc.get_cert_hash()
        assert cc.user.sign_cert_hash

    @allure.story('切换用户并获取证书哈希')
    def test_get_cert_hash_with_node4(self, cc, users):
        cc.user = users.get('client4')
        assert cc.get_cert_hash()

    @allure.story('查询证书')
    def test_query_cert(self, cc):
        cert_hashes = [cc.get_cert_hash().hex()]
        print(cert_hashes)
        res = cc.query_cert(cert_hashes)
        assert hasattr(res.cert_infos[0], 'cert')
        print(json_format.MessageToJson(res))

    @allure.story('删除证书')
    def test_del_cert(self, cc):
        cert_hashes = [cc.get_cert_hash().hex()]
        method = "CERTS_DELETE"
        params = {
            "cert_hashes": ",".join(cert_hashes)
        }
        payload = cc._create_cert_manage_payload(method, params)
        res = cc.send_manage_request(payload, with_sync_result=True)
        print(res)

    @allure.story('添加证书')
    def test_add_cert(self, cc):  # 重复添加不会报错
        res = cc.add_cert(with_sync_result=True)
        print(res)

    @allure.story('冻结解冻证书')
    def test_freeze_unfreeze_cert(self, cc, cc2, config_dir):
        """测试冻结-解冻证书"""
        cert_file = os.path.join(config_dir, 'crypto-config', 'wx-org2.chainmaker.org', 'user', 'client1',
                                 'client1.sign.crt')
        with open(cert_file) as f:
            cert = f.read()
        certs = [cert]
        payload = cc.create_cert_freeze_payload(certs)
        result = cc.send_manage_request(payload)
        message = result.contract_result.message
        if "the certHashKey is exist certHashKey" in message:
            print("证书已冻结")
        else:
            assert result.contract_result.message == 'OK', result.contract_result
        
        # 解冻证书
        payload = cc.create_cert_unfreeze_payload(certs)
        result = cc.send_manage_request(payload)
        print(result.contract_result)
        assert result.contract_result.message == 'OK', result.contract_result
        # with pytest.raises(RequestError):
        #     cc2.get_chain_config()

    @allure.story('吊销证书')
    def test_revoke_cert(self, cc, config_dir):
        """测试吊销证书"""
        os.chdir(config_dir)
        
        ca_crt_file = 'crypto-config/wx-org2.chainmaker.org/ca/ca.crt'
        ca_key_file = 'crypto-config/wx-org2.chainmaker.org/ca/ca.key'
        crt_path = 'crypto-config/wx-org2.chainmaker.org/user/client1/client1.tls.crt'
        
        cert_crl = create_crl_bytes(crt_path, ca_key_file, ca_crt_file)
        payload = cc.create_cert_revoke_payload(cert_crl)
        
        res = cc.send_manage_request(payload)
        assert result_is_ok(res)

    @allure.story('生成和加载吊销证书列表文件')
    def test_create_and_load_crl(self, config_dir, tmpdir):
        """测试创建吊销证书列表及加载吊销证书列表"""
        os.chdir(config_dir)
        
        ca_crt_file = './crypto-config/wx-org2.chainmaker.org/ca/ca.crt'
        ca_key_file = './crypto-config/wx-org2.chainmaker.org/ca/ca.key'
        crt_path = './crypto-config/wx-org2.chainmaker.org/user/client1/client1.tls.crt'
        crl_file = os.path.join(tmpdir, './client1.crl')
        data = create_crl_bytes(crt_path, ca_key_file, ca_crt_file)
        
        with open(crl_file, 'wb') as f:
            f.write(data)
        
        # 测试加载证书吊销列表
        crl = load_crl_file(crl_file)
        public_bytes = crl.public_bytes(encoding=serialization.Encoding.PEM)
        assert public_bytes == data


@allure.feature('证书压缩')
class TestCertHash:
    @allure.story('启用禁用证书哈希')
    def test_enable_disable_cert_hash(self, cc, send_tx):
        cc.enable_cert_hash()
        response = send_tx(1, with_sync_result=True)[0]
        assert result_is_ok(response)
        transaction_info = cc.get_tx_by_tx_id(response.tx_id)
        assert 1 == transaction_info.transaction.sender.signer.member_type, 'member_type应为CERT_HASH'
        
        cc.disable_cert_hash()
        response = send_tx(1, with_sync_result=True)[0]
        assert result_is_ok(response)
        transaction_info = cc.get_tx_by_tx_id(response.tx_id)
        assert 0 == transaction_info.transaction.sender.signer.member_type, 'member_type应为CERT'
        
