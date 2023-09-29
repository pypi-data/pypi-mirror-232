#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# @FileName     :   test_user_contract.py
# @Function     :   测试用户合约接口
"""
    Function        :    Input you funcion 
    Author          :    superhin
    Create time     :    2021/11/18
    Function List   :

"""
import os
import uuid

import allure
import pytest

from chainmaker.chain_client import RequestError, ChainClient
from chainmaker.user import User
from chainmaker.utils.evm_utils import calc_evm_contract_name, calc_evm_method_params
from chainmaker.utils.file_utils import switch_dir, load_yaml


@pytest.fixture()
def cc2(sdk_config_path, config_dir):
    with switch_dir(sdk_config_path):
        cc = ChainClient.from_conf(sdk_config_path)

    users_config = load_yaml(os.path.join(config_dir, './endorse_users_with_4clients.yml'))
    cc.endorse_users = [User.from_conf(**user_config) for user_config in users_config]
    yield cc
    cc.stop()
    


def contract_exists(cc, contract_name: str):
    """检查合约是否已安装"""
    try:
        cc.query_contract(contract_name, None)
    except RequestError as ex:
        if ex.err_code == 'INVALID_CONTRACT_PARAMETER_CONTRACT_NAME':
            return False
    return True


def issuer_asset(cc, contract_name, amount, addr):
    """发放"""
    params = {
        "amount": amount,
        "to": addr,
    }
    res = cc.invoke_contract(contract_name, "issue_amount", params, with_sync_result=True)
    return res
    # contract_result = res.contract_result
    #


def get_balance(cc, contract_name, addr):
    """获取余额"""
    params = {
        "owner": addr,
    }
    res = cc.query_contract(contract_name, "balance_of", params)
    balance = int(res.contract_result.result)
    return balance


def transfer(cc, contract_name, amount, addr):
    """转帐"""
    params = {
        "amount": amount,
        "to": addr,
    }
    res = cc.invoke_contract(contract_name, "transfer", params)
    return res


@allure.feature('用户合约')
class TestUserContract:
    @pytest.mark.payload
    def test_create_contract_create_payload_wasm(self, cc, testdata_dir):
        byte_code_path = os.path.join(testdata_dir, 'byte_codes',  'rust-asset-2.0.0.wasm')
        payload = cc.create_contract_create_payload('fact', '1.0', byte_code_path, 'WASMER', {})
        print(payload, type(payload))

    @pytest.mark.payload
    def test_create_contract_create_payload_evm(self, cc, testdata_dir):
        contract_name = calc_evm_contract_name('balance001')
        byte_code_path = os.path.join(testdata_dir, 'byte_codes', 'ledger_balance.bin')
        payload = cc.create_contract_create_payload(contract_name, '1.0', byte_code_path, 'EVM', None)
        print(payload, type(payload))

    @pytest.mark.payload
    def test_create_contract_upgrade_payload(self, cc, testdata_dir):
        byte_code_path = os.path.join(testdata_dir, 'byte_codes',  'rust-asset-2.0.0.wasm')
        payload = cc.create_contract_create_payload('fact', '2.0', byte_code_path,
                                                    'WASMER', {})
        print(payload, type(payload))

    @pytest.mark.payload
    def test_create_contract_freeze_payload(self, cc):
        payload = cc.create_contract_freeze_payload('fact')
        print(payload, type(payload))

    @pytest.mark.payload
    def test_create_contract_unfreeze_payload(self, cc):
        payload = cc.create_contract_unfreeze_payload('fact')
        print(payload, type(payload))

    @pytest.mark.payload
    def test_create_contract_revoke_payload(self, cc):
        payload = cc.create_contract_revoke_payload('fact')
        print(payload, type(payload))
    
    @allure.story('签名合约Payload')
    def test_sign_contract_manage_payload(self, cc, testdata_dir):  # fixme
        byte_code_path = os.path.join(testdata_dir, 'byte_codes', 'rust-asset-2.0.0.wasm')
        payload = cc.create_contract_create_payload('fact', '1.0', byte_code_path,
                                                    'WASMER', {})
        signed_payload = cc.sign_contract_manage_payload(payload.SerializeToString())
        print(signed_payload, type(signed_payload))
    
    @allure.story('发送合约管理请求')
    def test_send_contract_manage_request(self, cc, testdata_dir, create_endorsers):
        byte_code_path = os.path.join(testdata_dir, 'byte_codes', 'rust-asset-2.0.0.wasm')
        payload = cc.create_contract_create_payload('fact', '1.0', byte_code_path,
                                                    'WASMER', {})
        endorsers = create_endorsers(payload)
        res = cc.send_contract_manage_request(payload, endorsers)
        print(res, type(res))
    
    @allure.story('创建WSAM合约')
    def test_create_contract_wasm(self, cc, create_contract_fact):
        pass
    
    @allure.story('创建GASM合约')
    def test_create_contract_gasm(self, cc):  # fixme
        pass
    
    @allure.story('创建EVM合约')
    def test_create_contract_evm(self, cc, create_contract_balance001):
        pass
    
    @allure.story('创建Docker-Go合约')
    @pytest.mark.skip(reason="待实现")
    def test_create_contract_docker_go(self, cc):
        pass
    
    @allure.story('调用WASM合约')
    def test_invoke_contract_wasm(self, cc, create_contract_fact):
        # 调用WASM合约
        res = cc.invoke_contract('fact', 'save',
                        {"file_name": "name007", "file_hash": "ab3456df5799b87c77e7f88", "time": "6543234"},
                        with_sync_result=True)
        # 交易响应结构体转为字典格式
        assert res.code == 0, res.contract_result.message
    
    @allure.story('调用EVM合约')
    def test_invoke_contract_evm(self, cc, create_contract_balance001):
        # 调用EVM合约
        contract_name = 'balance001'
        method = 'updateBalance'
        params = [{"uint256": "10000"}, {"address": "0xa166c92f4c8118905ad984919dc683a7bdb295c1"}]
        contract_name = calc_evm_contract_name(contract_name)
        method, params = calc_evm_method_params(method, params)
        
        res = cc.invoke_contract(contract_name, method, params, with_sync_result=True)
        assert res.code == 0, res.contract_result.message
    
    @allure.story('检查合约是否存在')
    def test_check_contract_exists(self, cc, create_contract_fact):  # todo 改为get_contract_info
        contract_name = create_contract_fact
        assert contract_exists(cc, contract_name) is True
        random_contract_name = str(uuid.uuid4()).replace('-', '')
        assert contract_exists(cc, random_contract_name) is False
    
    @allure.story('查询WASM合约')
    def test_query_contract_wasm(self, cc, create_contract_fact):
        # 调用WASM合约
        res = cc.query_contract('fact', 'save',
                       {"file_name": "name007", "file_hash": "ab3456df5799b87c77e7f88", "time": "6543234"},
                       )
        # 交易响应结构体转为字典格式
        assert "SUCCESS" == res.message
    
    @allure.story('查询EVM合约')
    def test_query_contract_evm(self, cc, create_contract_balance001):
        # 调用EVM合约
        contract_name = 'balance001'
        method = 'updateBalance'
        params = [{"uint256": "10000"}, {"address": "0xa166c92f4c8118905ad984919dc683a7bdb295c1"}]
        
        contract_name = calc_evm_contract_name(contract_name)
        method, params = calc_evm_method_params(method, params)
        res = cc.query_contract(contract_name, method, params)
    
    @allure.story('获取交易体-不指定交易ID')
    def test_get_tx_request_without_tx_id(self, cc):
        res = cc.get_tx_request('fact', 'save',
                                {"file_name": "name007", "file_hash": "ab3456df5799b87c77e7f88", "time": "6543234"})
        print(res, type(res))
    
    @allure.story('获取交易体-指定交易ID')
    def test_get_tx_request_with_tx_id(self, cc):
        tx_request = cc.get_tx_request('fact', 'save',
                                       {"file_name": "name007", "file_hash": "ab3456df5799b87c77e7f88",
                                        "time": "6543234"},
                                       tx_id="9adc78daf14e4188a928b36cf201b28792651b7ed83a455dab93c921124db4f2")
        print(tx_request, type(tx_request))
    
    @allure.story('发送交易体')
    def test_send_tx_request(self, cc):
        tx_request = cc.get_tx_request('fact', 'save',
                                       {"file_name": "name007", "file_hash": "ab3456df5799b87c77e7f88",
                                        "time": "6543234"},
                                       tx_id="")
        res = cc.send_tx_request(tx_request, with_sync_result=True)
        print(res, type(res))
    
    @allure.story('查询-调用-冻结-解冻-升级-吊销asset存证合约')
    def test_contract_asset_lifecycle(self, cc, testdata_dir, create_contract_asset):
        """测试合约生命周期，创建-冻结-解冻-升级-吊销"""
        contract_name = create_contract_asset
        print('查询合约')
        res = cc.query_contract(contract_name, 'query_address')
        addr = res.contract_result.result
        
        print('调用合约')
        params = {
            "amount": "100000",
            "to": addr,
        }
        res = cc.invoke_contract(contract_name, "issue_amount", params, with_sync_result=True)
        assert 0 == res.contract_result.code, res.contract_result
        
        print("冻结合约")
        payload = cc.create_contract_freeze_payload(contract_name)
        res = cc.send_manage_request(payload)
        assert res.code == 0, res.contract_result.message
        
        print("解冻合约")
        payload = cc.create_contract_unfreeze_payload(contract_name)
        res = cc.send_manage_request(payload)
        assert res.code == 0, res.contract_result.message
        
        print("升级合约")
        params = {
            "issue_limit": "100000000",
            "total_supply": "100000000"
        }
        byte_code_path = os.path.join(testdata_dir, 'byte_codes', 'rust-asset-2.0.0.wasm')
        payload = cc.create_contract_upgrade_payload(contract_name, '2.0', byte_code_path, 'WASMER', params)
        res = cc.send_manage_request(payload)
        assert res.code == 0, res.contract_result.message
        
        print("吊销合约")
        payload = cc.create_contract_revoke_payload(contract_name)
        res = cc.send_manage_request(payload)
        assert res.code == 0, res.contract_result.message
    
    @allure.story('查询-调用-冻结-解冻-升级-吊销counter-go合约')
    def test_contract_counter_go_lifecycle(self, cc, testdata_dir, create_contract_counter_go):
        """测试创建counter-go合约"""
        contract_name = create_contract_counter_go
        print('调用合约')
        method = "increase"
        res = cc.invoke_contract(contract_name, method)
        assert res.code == 0, res.contract_result.message
        
        print('查询合约')
        method = 'query'
        res = cc.query_contract(contract_name, method)
        print('查询合约结果', res)
        
        print("冻结合约")
        payload = cc.create_contract_freeze_payload(contract_name)
        res = cc.send_manage_request(payload)
        assert res.code == 0, res.contract_result.message
        
        print("解冻合约")
        payload = cc.create_contract_unfreeze_payload(contract_name)
        res = cc.send_manage_request(payload)
        assert res.code == 0, res.contract_result.message
        
        print("升级合约")
        params = {}
        byte_code_path = os.path.join(testdata_dir, 'byte_codes',  'rust-counter-2.0.0.wasm')
        payload = cc.create_contract_upgrade_payload(contract_name, '2.0', byte_code_path, 'WASMER', params)
        res = cc.send_manage_request(payload)
        assert res.code == 0, res.contract_result.message
        
        print("吊销合约")
        payload = cc.create_contract_revoke_payload(contract_name)
        res = cc.send_manage_request(payload)
        assert res.code == 0, res.contract_result.message
    
    @pytest.mark.skip("fixme")
    def test_contract_asset(self, cc, cc2, create_contract_asset):  # fixme
        # 1. 创建合约
        contract_name = create_contract_asset
        
        # 2. 注册 client2 用户
        res = cc2.invoke_contract(contract_name, "register")
        addr = res.contract_result.result  # b'dc98ef0ec56cdef0360a3cee516b374a6d484937fcedc0f8e7fb48223efe7aa2'
        assert 64 == len(addr)
        
        # 3. 查询 钱包 对应地址
        res = cc.query_contract(contract_name, "query_address")
        addr1 = res.contract_result.result
        print(f"client1 address: {addr1}")
        
        res = cc2.query_contract(contract_name, "query_address")
        addr2 = res.contract_result.result
        print(f"client2 address: {addr2}")
        assert addr == addr2
        
        # 4. 发放金额 issue asset
        amount = "100000"
        res1 = issuer_asset(cc, contract_name, amount, addr1)
        assert 0 == res1.contract_result.code, res1.contract_result
        res2 = issuer_asset(cc, contract_name, amount, addr2)  # fixme cc2不能给自己发放金额
        assert 0 == res2.contract_result.code, res2.contract_result
        
        # 5. 分别查看余额
        balance1 = get_balance(cc, contract_name, addr1)
        assert int(amount) == balance1
        balance2 = get_balance(cc2, contract_name, addr2)
        assert int(amount) == balance2
        
        # 6. 转账
        transfer_amount = "100"
        res = transfer(cc, contract_name, transfer_amount, addr2)
        assert b"ok" == res.contract_result.result
        
        # 7. 再次分别查看余额
        balance1 = get_balance(cc, contract_name, addr1)
        assert int(amount) - int(transfer_amount) == balance1
        balance2 = get_balance(cc2, contract_name, addr2)
        assert int(amount) + int(transfer_amount) == balance2
    
    @allure.story('带Limit调用合约')
    def test_invoke_contract_with_limit(self, cc, create_contract_fact):
        if cc.auth_type != "Public":
            pytest.skip('仅支持Public模式')
        limit = 10
        res = cc.invoke_contract_with_limit('fact', 'save',
                                            {"file_name": "name007", "file_hash": "ab3456df5799b87c77e7f88",
                                             "time": "6543234"},
                                            with_sync_result=True, gas_limit=limit)
        
        assert res.code == 0, res.contract_result.message


@allure.feature('用户合约')
class TestCounterEvm:
    @allure.story('创建counter_evm合约')
    def test_create_counter_evm(self, create_counter_evm):
        pass

    @allure.story('调用counter_evm合约calc_json')
    def test_invoke_counter_evm(self, cc, create_counter_evm):
        contract_name = create_counter_evm
        method = 'calc_json'
        params = [{'string': 'sub'}, {'uint256': 100}, {'uint256': 4}, {'uint256': '25'}, {'uint256': '0'}]
        method, params = calc_evm_method_params(method, params)
        res = cc.invoke_contract(contract_name, method, params)
        print(res)
    
    @allure.story('查询counter_evm合约get_calc-params为空')
    def test_query_counter_evm(self, cc, create_counter_evm):
        contract_name = create_counter_evm
        method = 'get_calc'  # 查询EVM合约method, params不用转换
        params = None
        res = cc.query_contract(contract_name, method, params)
        # jsonschema.validate(json_format.MessageToDict(res), schemas.TxResponseSchema)

