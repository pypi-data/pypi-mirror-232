#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# @FileName     :   test_vm_contract.py
# @Function     :   测试虚拟机合约（用户合约）
import os
import time

import pytest
import allure


from chainmaker.exceptions import RequestError
from tests.utils.contract_utils import CounterRust


@pytest.fixture
def counter_rust(cc, random_contract_name, testdata_dir):
    return CounterRust(cc, random_contract_name, os.path.join(testdata_dir, 'byte_codes', 'counter-rust.wasm'))


@allure.feature('虚拟机合约')
class TestRustWasmer:
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story('异常用例-合约failure-交易出块前后查询结果变化')
    def test_rust_wasmer_failure(self, cc, counter_rust):
        with allure.step('创建合约'):
            counter_rust.create()
        
        with allure.step('查询合约'):
            contract = counter_rust.get_contract_info()
            print('contract', contract)
            
        with allure.step('调用合约'):
            block_height_before_invoke = cc.get_current_block_height()  # 执行合约前的区块高度
            invoke_result = counter_rust.calc_json('failure', '100', '2', '10', '50')
            block_height_after_invoke = cc.get_current_block_height()  # 执行合约后的区块高度
            assert 1 == block_height_after_invoke - block_height_before_invoke, '调用合约前后块高差应为1'
            
            invoke_result_code = invoke_result.code
            contract_result_msg = invoke_result.contract_result.message
            assert  4 == invoke_result_code, '交易执行结果状态'  # 4 为 'CONTRACT_FAIL'
            assert "test error" in contract_result_msg, '调用failure方法执行结果'
    
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story('执行fact合约业务流-存证合约-校验存证结果-交易出块前后查询结果变化')
    def test_rust_wasmer_call_self(self, cc, counter_rust):
        with allure.step('创建合约'):
            counter_rust.create()
            
        with allure.step('查询合约'):
            contract = counter_rust.get_contract_info()
            print('contract', contract)

        with allure.step('调用合约'):
            block_height_before_invoke = cc.get_current_block_height()  # 执行合约前的区块高度
            invoke_result = counter_rust.call_contract_self()
            block_height_after_invoke = cc.get_current_block_height()  # 执行合约后的区块高度
            assert 1 == block_height_after_invoke - block_height_before_invoke, '调用合约前后块高差应为1'
            
            invoke_reuslt_code = invoke_result.code
            contract_result_msg = invoke_result.contract_result.message
            assert 0 == invoke_reuslt_code, '执行成功'
            assert '' == contract_result_msg, '调用failure方法执行结果'

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story('wasmer合约升级')
    def test_rust_wasmer_upgrade(self, cc, counter_rust, testdata_dir):
        byte_code_path_upgrade = os.path.join(testdata_dir, 'byte_codes', 'counter-rust-upgrade.wasm')
        # 配置参数：合约调用参数定义：invoke_params
        upgrade_get_store_method = "upgrade_get_store"
        upgrade_set_store_method = "upgrade_set_store"
        
        # 調用參數
        key = 'upgrade_test_key'
        name = 'upgrade_test_name'
        value = 'upgrade_test_value_{}'.format(int(time.time()))
        set_store_params = {"key": key, "name": name, "value": value}
        get_store_params = {"key": key, "name": name}
        
        new_version = '1.1.0'
        
        # 期待结果
        exp_invoke_result_before_upgrade = "`upgrade_set_store` does not exist"
        
        with allure.step('创建合约'):
            counter_rust.create()
            
        with allure.step('查询合约'):
            contract = counter_rust.get_contract_info()
            print('contract', contract)
            
        with allure.step('合约升级前执行合约方法查询'):
            try:
                counter_rust.query(upgrade_get_store_method, get_store_params)
            except RequestError:
                print(f'升级前查询升级后的方法，返回失败')
        
        with allure.step('合约升级前执行合约方法调用'):
            invoke_result = counter_rust.invoke(upgrade_set_store_method, set_store_params)
            invoke_result_msg = invoke_result.contract_result.message
            assert exp_invoke_result_before_upgrade in invoke_result_msg, "升级前调用升级后存证合约失败"

        with allure.step('升级合约'):
            counter_rust.upgrade(byte_code_path_upgrade, new_version)
            
        with allure.step('查询合约'):
            contract = counter_rust.get_contract_info()
            print('contract', contract)

        with allure.step('合约升级后执行合约方法查询'):
            query_result = counter_rust.query(upgrade_get_store_method, get_store_params)
            print(f'校验合约结果 {query_result}')
            assert 'SUCCESS' == query_result.message, '查询结果message为SUCCESS'
    
        with allure.step('合约升级后执行合约方法调用'):
            block_height_before_invoke = cc.get_current_block_height()  # 执行合约前的区块高度
            counter_rust.invoke(upgrade_set_store_method, set_store_params)
            block_height_after_invoke = cc.get_current_block_height()  # 执行合约后的区块高度
            assert 1 == block_height_after_invoke - block_height_before_invoke, '调用合约前后块高差应为1'

        with allure.step('查询合约执行结果'):
            query_result = counter_rust.query(upgrade_get_store_method, get_store_params)
            print(f'校验合约结果 {query_result}')
            assert 'SUCCESS' == query_result.message,  '查询结果message为SUCCESS'
    
            query_value = query_result.contract_result.result.decode()
            print('query_value', query_value)
            assert value == query_value, '查询结果message为SUCCESS'

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story('异常用例-合约failure-交易出块前后查询结果变化')
    def test_rust_wasmer_call_memory(self, cc, counter_rust):
        allocate_size = 2048
        
        with allure.step('创建合约'):
            counter_rust.create()
    
        with allure.step('查询合约'):
            contract = counter_rust.get_contract_info()
            print('contract', contract)

        with allure.step('调用合约'):
            block_height_before_invoke = cc.get_current_block_height()  # 执行合约前的区块高度
            counter_rust.call_memory(allocate_size)
            block_height_after_invoke = cc.get_current_block_height()  # 执行合约后的区块高度
            assert 1 == block_height_after_invoke - block_height_before_invoke, '调用合约前后块高差应为1'
            
