#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# @FileName     :   test_pubkey_manage.py
# @Function     :   测试公钥管理接口

import os

import allure
import pytest
from google.protobuf.json_format import MessageToDict

from chainmaker.keys import AuthType
from chainmaker.user import User
from tests.utils.cropto_config_utils import CURRENT_AUTH_TYPE


@pytest.mark.skipif(CURRENT_AUTH_TYPE != AuthType.PermissionedWithKey, reason='仅支持PermissionWithKey')
@allure.feature('PermissionWithKey')
class TestPermissionWithKey:
    def test_permission_with_key(self, cc):
        """测试公钥身份模式"""
        print(cc.get_chain_info())

    def test_create_contract_wasm(self, cc, create_contract_name):
        # 创建payload
        params = {
            "issue_limit": "100000000",
            "total_supply": "100000000"
        }
        payload = cc.create_contract_create_payload(create_contract_name, '1.0', byte_code_path,
                                                    'WASMER', params)
        # 携带背书发送请求
        res = cc.send_manage_request(payload, with_sync_result=True)
        assert res.code == 0, res.contract_result.message


@pytest.mark.skipif(CURRENT_AUTH_TYPE != AuthType.PermissionedWithKey, reason='仅支持PermissionWithKey')
@allure.feature('公钥管理')
class TestPubkeyMagage:
    @pytest.mark.payload
    def test_create_pubkey_add_payload(self, cc):
        pubkey = 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCoVX1MfVkxocdu+LUxqj8AL3whXjeH2cGtYkLZXKS7/bXPsZK79wEZewHptAOHoY4z' \
                 'VZ+yucVe1Cu2d7bwOPWG8L8A5YUJ4vSVwzzQpZBo6lWWZb39IyauDUq3U4g40yATTauA1xgF1kfArYRkOR/+X+X5b8PAyFwP7aVIztXa' \
                 'k6YD1VONpzYwGC3rMSFUCnyRD3xLroy002xmdoVEgebPDB1zuETFRMCGZfBx8+Vt22CxBMcp2y4JymoFpzk+0aB94bzc/Y5ZTarWmJRz' \
                 'jZQZ0ftrtzVcl5dBFe9He3LNr/fQCxgyV4O+EhhM1y3+3lhkhXWJNeShasKE7Ik2PKzj leon_liuyi@msn.com'
        org_id = 'wx-org5.chainmaker.org'
        role = 'client'
        payload = cc.create_pubkey_add_payload(pubkey, org_id, role)
        print(type(payload), payload)

    @pytest.mark.payload
    def test_create_pubkey_del_payload(self, cc):
        pubkey = 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCoVX1MfVkxocdu+LUxqj8AL3whXjeH2cGtYkLZXKS7/bXPsZK79wEZewHptAOHoY4z' \
                 'VZ+yucVe1Cu2d7bwOPWG8L8A5YUJ4vSVwzzQpZBo6lWWZb39IyauDUq3U4g40yATTauA1xgF1kfArYRkOR/+X+X5b8PAyFwP7aVIztXa' \
                 'k6YD1VONpzYwGC3rMSFUCnyRD3xLroy002xmdoVEgebPDB1zuETFRMCGZfBx8+Vt22CxBMcp2y4JymoFpzk+0aB94bzc/Y5ZTarWmJRz' \
                 'jZQZ0ftrtzVcl5dBFe9He3LNr/fQCxgyV4O+EhhM1y3+3lhkhXWJNeShasKE7Ik2PKzj leon_liuyi@msn.com'
        org_id = 'wx-org5.chainmaker.org'
        payload = cc.create_pubkey_delete_payload(pubkey, org_id)
        print(type(payload), payload)
        
    @pytest.mark.payload
    def test_create_pubkey_query_payload(self, cc):
        pubkey = 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCoVX1MfVkxocdu+LUxqj8AL3whXjeH2cGtYkLZXKS7/bXPsZK79wEZewHptAOHoY4z' \
                 'VZ+yucVe1Cu2d7bwOPWG8L8A5YUJ4vSVwzzQpZBo6lWWZb39IyauDUq3U4g40yATTauA1xgF1kfArYRkOR/+X+X5b8PAyFwP7aVIztXa' \
                 'k6YD1VONpzYwGC3rMSFUCnyRD3xLroy002xmdoVEgebPDB1zuETFRMCGZfBx8+Vt22CxBMcp2y4JymoFpzk+0aB94bzc/Y5ZTarWmJRz' \
                 'jZQZ0ftrtzVcl5dBFe9He3LNr/fQCxgyV4O+EhhM1y3+3lhkhXWJNeShasKE7Ik2PKzj leon_liuyi@msn.com'
        payload = cc.create_pubkey_query_payload(pubkey)
        print(type(payload), payload)

    def test_send_pubkey_manage_request(self, cc):
        pass

    @allure.story('添加公钥')
    def test_add_pubkey(self, cc, crypto_config_path):
        pubkey_file_path = os.path.join(crypto_config_path, 'wx-org3.chainmaker.org', 'user', 'client1', 'client1.pem')
        pubkey = open(pubkey_file_path).read()
        org_id = 'wx-org1.chainmaker.org'
        role = 'client'
        payload = cc.create_pubkey_add_payload(pubkey, org_id, role)
        res = cc.send_manage_request(payload)
        assert res.code == 0, res.contract_result.message

    @allure.story('查询公钥')
    def test_query_pubkey(self, cc, crypto_config_path):
        pubkey_file_path = os.path.join(crypto_config_path, 'wx-org3.chainmaker.org', 'user', 'client1', 'client1.pem')
        pubkey = open(pubkey_file_path).read()
        payload = cc.create_pubkey_query_payload(pubkey)
        res = cc.send_request_with_sync_result(payload)
        # res = cc.send_manage_request(payload)
        assert hasattr(res, 'contract_result'), '公钥不存在'
        print(MessageToDict(res))

    @allure.story('删除公钥')
    def test_del_pubkey(self, cc, crypto_config_path):
        pubkey_file_path = os.path.join(crypto_config_path, 'wx-org3.chainmaker.org', 'user', 'client1', 'client1.pem')
        pubkey = open(pubkey_file_path).read()
        org_id = 'wx-org1.chainmaker.org'
        payload = cc.create_pubkey_delete_payload(pubkey, org_id)
        res = cc.send_manage_request(payload)
        assert res.code == 0, res.contract_result.message

    @allure.story('添加公钥-使用其他节点')
    def test_add_pubkey_with_node4(self, cc, config_dir, crypto_config_path):
        os.chdir(config_dir)
        cc.user = User.from_conf(
            org_id= "wx-org4.chainmaker.org",
            user_sign_key_file_path="./crypto-config/wx-org4.chainmaker.org/admin/admin.key",
            crypto=dict(hash='SHA256'),
            auth_type='permissionedWithKey',
        )
        pubkey_file_path = os.path.join(crypto_config_path, 'wx-org4.chainmaker.org', 'user', 'admin1', 'admin1.pem')
        pubkey = open(pubkey_file_path).read()
        org_id = 'wx-org4.chainmaker.org'
        role = 'client'
        payload = cc.create_pubkey_add_payload(pubkey, org_id, role)
        res = cc.send_manage_request(payload)
        print(res)
