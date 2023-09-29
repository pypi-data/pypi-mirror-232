#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# @FileName     :   test_gas_manage.py
# @Function     :   测试Gas计费管理
import os
import allure
import pytest

from chainmaker.user import User
from chainmaker.keys import AuthType, RechargeGasItem
from chainmaker.chain_client import ChainClient
from chainmaker.utils.crypto_utils import get_address_from_private_key_file, get_zx_address_from_public_key, get_evm_address_from_public_key

from tests.utils.cropto_config_utils import CURRENT_AUTH_TYPE


@pytest.mark.skipif(CURRENT_AUTH_TYPE != AuthType.Public, reason='Gas计费管理仅支持public模式')
@allure.feature('Gas管理')
class TestCaseManage:
 
    def test_pk_to_address(self):
        pass
    
    def test_cert_to_address(self, crypto_config_path):
        client1_sign_key_file = os.path.join(crypto_config_path, "node1/admin/admin1/admin1.key")
        address = get_address_from_private_key_file(client1_sign_key_file)
        
        print('address', address)
        
        assert len(address) == 42
        assert address == 'ZX7b415d8172b7f7e8049d992a6b578b9d9e3a9190'
    
    def test_hex_to_address(self):
        pass
    
    def test_set_gas_admin(self, cc):  # ✅
        address = cc.user.get_address()
        payload = cc.create_set_gas_admin_payload(address)
        res = cc.send_manage_request(payload, with_sync_result=True)
        assert res.contract_result.message == 'OK', res.contract_result
    
    def test_get_gas_admin(self, cc):  # ✅
        address = cc.get_gas_admin()
        assert address == cc.user.get_address()
    
    def test_get_gas_balance(self, cc):  # ✅
        address = 'ZX573795fa766f226574573a6467fd506def0797bb'
        balance = cc.get_gas_balance(address)
        print(balance)
    
    def test_recharge_balance(self, cc):
        """测试充值"""
        address = cc.user.get_address()
        origin_balance = cc.get_gas_balance(address)
        payload = cc.create_recharge_gas_payload([RechargeGasItem(address,1000)])
        res = cc.send_manage_request(payload, with_sync_result=True)
        assert res.contract_result.message == 'OK', res.contract_result
        current_balance = cc.get_gas_balance(address)
        assert 1000 == current_balance - origin_balance
    
    def test_refund_gas_payload(self, cc):
        """测试退款"""
        address = 'ZX7b415d8172b7f7e8049d992a6b578b9d9e3a9190'
        origin_balance = cc.get_gas_balance(address)
        payload = cc.create_refund_gas_payload(address, 500)
        res = cc.send_manage_request(payload,  with_sync_result=True)
        assert res.contract_result.message == 'OK', res.contract_result
        current_balance = cc.get_gas_balance(address)
        assert 500 == origin_balance - current_balance
    
    def test_freeze_gas_account(self, cc):
        """测试冻结账户"""
        address = 'ZX7b415d8172b7f7e8049d992a6b578b9d9e3a9190'
        payload = cc.create_frozen_gas_account_payload(address)
        res = cc.send_manage_request(payload,  with_sync_result=True)
        assert res.contract_result.message == 'OK', res.contract_result
    
    def test_unfreeze_gas_account(self, cc):
        """测试解冻账户"""
        address = 'ZX7b415d8172b7f7e8049d992a6b578b9d9e3a9190'
        payload = cc.create_unfrozen_gas_account_payload(address)
        res = cc.send_manage_request(payload, with_sync_result=True)
        assert res.contract_result.message == 'OK', res.contract_result
    
    def test_get_gas_account_status(self, cc):
        address = 'ZX7b415d8172b7f7e8049d992a6b578b9d9e3a9190'
        res = cc.get_gas_account_status(address)
        print(res)
    
    def test_attach_gas_limit(self, cc):  # Fixme
        address = 'ZX7b415d8172b7f7e8049d992a6b578b9d9e3a9190'
        payload = cc.create_recharge_gas_payload(address, 1000)
        cc.attach_gas_limit(gas_limit=100)
        res = cc.send_manage_request(payload, with_sync_result=True)
        assert res.contract_result.message == 'OK', res.contract_result
