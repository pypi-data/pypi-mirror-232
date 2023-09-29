#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# @FileName     :   test_system_contract.py
# @Function     :   测试系统合约接口
"""
    Function        :    Input you funcion 
    Author          :    superhin
    Create time     :    2021/11/18
    Function List   :

"""
import base64

import allure
import pytest
from google.protobuf import json_format

from chainmaker import exceptions
from chainmaker.protos.common import transaction_pb2
from chainmaker.utils.result_utils import check_response


def base64_to_block_hash(block_hash_base64: str):
    """base64形式的block_hash转hex形式的block_hash"""
    return base64.b64decode(block_hash_base64).hex()


def test_block_hash_base64_to_hex():
    block_hash_base64 = '55ueu9Z7Tb0eyusAOYdHcPWrYdTFJuCKOtDlIjsId6U='
    excepted_block_hash = 'e79b9ebbd67b4dbd1ecaeb0039874770f5ab61d4c526e08a3ad0e5223b0877a5'
    assert excepted_block_hash == base64_to_block_hash(block_hash_base64)


@allure.feature('查询链信息')
class TestQueryChain:
    
    @pytest.mark.pvt
    @allure.story('查询链信息')
    def test_get_chain_info(self, cc):
        """测试获取链信息"""
        res = cc.get_chain_info()
        print(res)
        assert res.block_height >= 0
    
    @allure.story('根据交易ID查询交易信息')
    def test_get_tx_by_tx_id(self, cc, last_block_tx_id):
        """测试通过交易id 获取交易信息 """
        tx_id = last_block_tx_id
        res = cc.get_tx_by_tx_id(tx_id)
        assert tx_id == res.transaction.payload.tx_id
        assert isinstance(res, transaction_pb2.TransactionInfo)
        print(json_format.MessageToJson(res))
    
    @allure.story('根据交易ID查询带读写集交易信息')
    def test_get_tx_with_rwset_by_tx_id(self, cc, last_block_tx_id):  # Fixme 和 get_tx_by_tx_id结果一样
        tx_id = last_block_tx_id
        res = cc.get_tx_with_rwset_by_tx_id(tx_id)
        assert tx_id == res.transaction.payload.tx_id
        assert res.rw_set is not None
        print(json_format.MessageToJson(res))
    
    @allure.story('根据高度查询区块信息')
    def test_get_block_by_height(self, cc):
        """测试通过高度获取区块信息"""
        block_height = cc.get_current_block_height()
        res = cc.get_block_by_height(block_height, with_rw_set=False)
        print(json_format.MessageToJson(res))
        assert block_height == res.block.header.block_height
    
    @allure.story('根据高度查询区块信息')
    def test_get_block_by_height_zero(self, cc):
        """测试通过高度获取区块信息"""
        block_height = 0
        res = cc.get_block_by_height(block_height, with_rw_set=False)
        print(json_format.MessageToJson(res))
        print('res.block.header.block_height', res.block.header.block_height)
        assert block_height == res.block.header.block_height
    
    @allure.story('根据高度查询带读写集区块信息')
    def test_get_block_by_height_with_rw_set(self, cc):
        """测试通过高度获取区块信息"""
        block_height = cc.get_current_block_height()
        res = cc.get_block_by_height(block_height, with_rw_set=True)
        print(type(res), res)
    
    @allure.story('根据哈希查询区块信息')
    def test_get_block_by_hash(self, cc, last_block_hash):
        block_hash = last_block_hash
        res = cc.get_block_by_hash(block_hash, with_rw_set=False)
        print(type(res), res)
    
    @allure.story('根据交易ID查询区块信息')
    def test_get_block_by_tx_id(self, cc, last_block_tx_id):
        """测试通过区块哈希获取区块信息"""
        tx_id = last_block_tx_id
        res = cc.get_block_by_tx_id(tx_id, with_rw_set=False)
        print(type(res), res)
    
    @allure.story('根据高度查询带读写集区块信息')
    def test_get_block_by_tx_id_with_rw_set(self, cc, last_block_tx_id):
        """测试通过交易id获取区块信息"""
        tx_id = last_block_tx_id
        res = cc.get_block_by_tx_id(tx_id, with_rw_set=True)
        print(type(res), res)
    
    @allure.story('获取最新配置区块信息')
    def test_get_last_config_block(self, cc):
        res = cc.get_last_config_block(with_rw_set=False)
        print(type(res), res)
    
    @allure.story('获取最新带读写集配置区块信息')
    def test_get_last_config_block_with_rw_set(self, cc):
        res = cc.get_last_config_block(with_rw_set=True)
        print(type(res), res)
    
    @allure.story('获取最新区块信息')
    def test_get_last_block(self, cc):
        res = cc.get_last_block()
        print(type(res), res)
    
    @allure.story('获取最新带读写集区块信息')
    def test_get_last_block_with_rw_set(self, cc):
        res = cc.get_last_block(with_rw_set=True)
        print(type(res), res)
    
    @allure.story('获取节点加入的链列表')
    def test_get_node_chain_list(self, cc):
        res = cc.get_node_chain_list()
        print(json_format.MessageToJson(res))
        assert 'chain1' in res.chain_id_list
    
    @allure.story('根据高度获取完整区块信息')
    def test_get_full_block_by_height(self, cc):
        block_height = cc.get_current_block_height()
        res = cc.get_full_block_by_height(block_height)
        print(json_format.MessageToJson(res))
    
    @allure.story('根据交易ID获取区块高度')
    def test_get_block_height_by_tx_id(self, cc, last_block_tx_id):
        """测试根据交易id获取区块高度"""
        tx_id = last_block_tx_id
        res = cc.get_block_height_by_tx_id(tx_id)
        print(type(res), res)
    
    @allure.story('根据哈希获取区块高度')
    def test_get_block_height_by_hash(self, cc, last_block_hash):
        """测试根据交易id获取区块高度"""
        block_hash = last_block_hash
        res = cc.get_block_height_by_hash(block_hash)
        print(type(res), res)
    
    @allure.story('获取归档区块高度')
    def test_get_archived_block_height(self, cc):
        """测试获取归档块高"""
        res = cc.get_archived_block_height()
        print(type(res), res)
    
    @allure.story('获取区块高度-使用交易ID')
    def test_get_block_height_with_tx_id(self, cc, last_block_tx_id):
        tx_id = last_block_tx_id
        res = cc.get_block_height(tx_id)
        print(type(res), res)
    
    @allure.story('获取区块高度-使用区块哈希')
    def test_get_block_height_with_hash(self, cc, last_block_hash):  # fixme
        hash = last_block_hash
        res = cc.get_block_height(block_hash=hash)
        print(type(res), res)
    
    @allure.story('获取当前区块高度')
    def test_get_current_block_height(self, cc):
        res = cc.get_current_block_height()
        print(type(res), res)
    
    @allure.story('根据高度获取区块头信息')
    def test_get_block_header_by_height(self, cc):
        block_height = cc.get_current_block_height()
        res = cc.get_block_header_by_height(block_height)
        print(json_format.MessageToJson(res))
        assert block_height == res.block_height
    
    def test_get_merkle_path_by_tx_id(self, cc, last_block_tx_id):
        tx_id = last_block_tx_id
        print('交易ID', tx_id)
        res = cc.get_merkle_path_by_tx_id(tx_id)
        print(res)


@allure.feature('系统合约')
class TestSystemContract:
    def test_invoke_system_contract_with_user_contract(self, cc, create_contract_fact):
        contract_name = "fact"
        method = "save"
        params = {"file_name": "name007", "file_hash": "ab3456df5799b87c77e7f88", "time": "6543234"}
        res = cc.invoke_system_contract(contract_name, method, tx_id="", params=params, timeout=60,
                                        with_sync_result=True)
        print(res)
    
    @pytest.mark.skip('由于不支持背书无法调用大部分系统合约')
    def test_invoke_system_contract_with_system_contract(self, cc):
        pass
    
    def test_query_system_contract_with_user_contract(self, cc, create_contract_fact):
        contract_name = "fact"
        method = "save"
        params = {"file_name": "name007", "file_hash": "ab3456df5799b87c77e7f88", "time": "6543234"}
        res = cc.query_system_contract(contract_name, method, params)
        print(res)
    
    def test_query_system_contract_with_system_contract(self, cc, create_contract_fact):
        contract_name = "CHAIN_CONFIG"
        method = "GET_CHAIN_CONFIG"
        params = None
        res = cc.query_system_contract(contract_name, method, params)
        print(json_format.MessageToJson(res))


@allure.feature('合约查询')
class TestQueryContract:
    def test_create_native_contract_access_payload(self, cc, create_frozen_contract):
        contract_name = create_frozen_contract
        access_contract_list = [contract_name]
        payload = cc.create_native_contract_access_grant_payload(access_contract_list)
        print(payload)
    
    def test_grand_access_native_contract_with_user_contract(self, cc, create_frozen_contract):
        contract_name = create_frozen_contract
        access_contract_list = [contract_name]
        payload = cc.create_native_contract_access_grant_payload(access_contract_list)
        res = cc.send_manage_request(payload)
        print('响应: ', res)
        
        check_response(res)
        contract = cc.get_contract_info(contract_name)
        print(contract.status)
        assert 0 == contract.status  # 0:NORMAL 1:FROZEN 2: REVOKED
    
    def test_create_native_contract_revoke_payload(self, cc, create_frozen_contract):
        contract_name = create_frozen_contract
        access_contract_list = [contract_name]
        payload = cc.create_native_contract_access_revoke_payload(access_contract_list)
        print(payload)
    
    def test_revoke_access_native_contract_with_user_contract(self, cc, create_contract_counter_go):
        contract_name = create_contract_counter_go
        access_contract_list = [contract_name]
        payload = cc.create_native_contract_access_revoke_payload(access_contract_list)
        res = cc.send_manage_request(payload)
        print('响应: ', res)
        check_response(res)
        contract = cc.get_contract_info(contract_name)
        print(contract.status)
        assert 1 == contract.status  # TODO 确认 为什么不是2
    
    @allure.story("禁用启用系统合约")
    def test_revoke_grant_access_native_contract(self, cc):
        contract_name = 'CROSS_TRANSACTION'
        print('合约状态: ', cc.get_contract_info(contract_name).status)
        with allure.step("吊销合约访问"):
            payload = cc.create_native_contract_access_revoke_payload([contract_name])
            res = cc.send_manage_request(payload)  # "contract status invalid, contract[CROSS_TRANSACTION] expect status:NORMAL,actual status:FROZEN"
            check_response(res)
            assert 1 == cc.get_contract_info(contract_name).status  # TODO 确认 为什么不是2
            disabled_contract_list = cc.get_disabled_native_contract_list()
            print('禁用合约列表: ', disabled_contract_list)
            assert contract_name in disabled_contract_list
        
        with allure.step("启用合约访问"):
            payload = cc.create_native_contract_access_grant_payload([contract_name])
            res = cc.send_manage_request(payload)
            check_response(res)
            assert 0 == cc.get_contract_info(contract_name).status
            
            disabled_contract_list = cc.get_disabled_native_contract_list()
            print('禁用合约列表: ', disabled_contract_list)
            assert contract_name not in disabled_contract_list
    
    @allure.story('获取合约信息-用户合约')
    def test_get_contract_info_with_user_contract(self, cc, create_contract_fact):
        contract_name = 'fact'
        contract = cc.get_contract_info(contract_name)
        print(json_format.MessageToJson(contract))
        assert contract_name == contract.name, contract
    
    @allure.story('获取合约信息-不存在的用户合约')
    def test_get_contract_info_with_not_exist_user_contract(self, cc):
        contract_name = 'abcdefg'
        try:
            contract = cc.get_contract_info(contract_name)
        except exceptions.ContractFail as ex:
            assert 'contract not exist' in ex.err_msg
    
    @allure.story('获取合约信息-系统合约')
    def test_get_contract_info_with_system_contract(self, cc):
        contract_name = 'ACCOUNT_MANAGER'
        contract = cc.get_contract_info(contract_name)
        assert 'ACCOUNT_MANAGER' == contract.name, contract
    
    @allure.story('获取合约列表')
    def test_get_contract_list(self, cc, create_contract_fact):
        contracts = cc.get_contract_list()
        print('合约数', len(contracts))
        contract_names = [contract.name for contract in contracts]
        print('contract_names', contract_names)
        assert 'fact' in contract_names
    
    def test_get_disabled_native_contract_list(self, cc, create_contract_counter_go):
        contract_name = create_contract_counter_go
        access_contract_list = [contract_name]
        payload = cc.create_native_contract_access_revoke_payload(access_contract_list)
        print(json_format.MessageToJson(payload))
        res = cc.send_manage_request(payload)
        check_response(res)
        
        res = cc.get_disabled_native_contract_list()
        print(res)
        assert contract_name in res
