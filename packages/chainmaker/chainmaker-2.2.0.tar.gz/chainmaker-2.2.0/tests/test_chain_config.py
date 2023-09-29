#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# @FileName     :   test_chain_config.py
# @Function     :   测试链配置接口
"""
    Function        :    Input you funcion 
    Author          :    superhin
    Create time     :    2021/11/18
    Function List   :

"""
import time

import allure
import pytest
from google.protobuf import json_format

from chainmaker.keys import AuthType
from chainmaker.utils.result_utils import check_response


@pytest.fixture()
def node_org_id():
    return 'wx-org4.chainmaker.org'


@pytest.fixture()
def node_org_ca_file(node_org_id, crypto_config_path):
    return f'{crypto_config_path}/{node_org_id}/ca/ca.crt'


@pytest.fixture()
def node_id_file(node_org_id, crypto_config_path):
    return f'{crypto_config_path}/{node_org_id}/node/consensus1/consensus1.nodeid'


@pytest.fixture()
def node_id(node_id_file):
    with open(node_id_file, encoding='utf-8') as f:
        return f.read().strip()


@pytest.fixture()
def trust_root_crt(node_org_ca_file):
    with open(node_org_ca_file, encoding='utf-8') as f:
        return f.read().strip()


@pytest.mark.pvt
def test_get_chain_config(cc):
    """测试获取链配置"""
    res = cc.get_chain_config()
    print(json_format.MessageToJson(res))
    # assert len(res.consensus.nodes) == 4


def test_get_chain_config_by_block_height(cc):
    res = cc.get_chain_config_by_block_height(1)
    print(type(res), res)


def test_get_chain_config_sequence(cc):
    res = cc.get_chain_config_sequence()
    print(type(res), res)


def test_sign_chain_config_payload(cc):
    tx_scheduler_timeout = 10
    tx_scheduler_validate_timeout = 10
    payload = cc.create_chain_config_core_update_payload(tx_scheduler_timeout, tx_scheduler_validate_timeout)
    
    payload_bytes = payload.SerializeToString()
    signed_payload_bytes = cc.sign_chain_config_payload(payload_bytes)
    print(type(signed_payload_bytes), signed_payload_bytes)


def test_send_chain_config_update_request(cc, create_endorsers):
    tx_scheduler_timeout = 10
    tx_scheduler_validate_timeout = 10
    payload = cc.create_chain_config_core_update_payload(tx_scheduler_timeout, tx_scheduler_validate_timeout)
    endorsers = create_endorsers(payload)
    res = cc.send_chain_config_update_request(payload, endorsers)
    print(res)
    check_response(res)


@pytest.mark.parametrize('addr_type', [0, 1, 2], ids=['0-ChainMaker', '1-ZXL', '2-ETHEREUM'])
def test_chain_config_alter_addr_type(cc, addr_type):
    if cc.auth_type != AuthType.Public:
        pytest.skip('仅支持Public模式')
    # addr_type = 1  # 0-ChainMaker; 1-ZXL ; 2-ETHEREUM
    if cc.auth_type != AuthType.Public:
        pytest.skip("仅支持Public模式")  # todo 确认
    payload = cc.create_chain_config_alter_addr_type_payload(addr_type)
    print(payload)
    res = cc.send_manage_request(payload)
    print(res)
    
    check_response(res)
    
    assert addr_type == cc.get_chain_config().vm.addr_type


def test_chain_config_enable_or_disable_gas(cc):
    if cc.auth_type != AuthType.Public:
        pytest.skip('仅支持Public模式')
    chainconfig = cc.get_chain_config()
    origin_enable_gas = chainconfig.account_config.enable_gas
    print('原始enable_gas', origin_enable_gas)
    
    # enable gas
    payload = cc.create_chain_config_enable_or_disable_gas_payload()
    res = cc.send_manage_request(payload)
    check_response(res)
    
    chainconfig = cc.get_chain_config()
    assert chainconfig.account_config.enable_gas is not origin_enable_gas
    
    # disable gas
    payload = cc.create_chain_config_enable_or_disable_gas_payload()
    res = cc.send_manage_request(payload)
    check_response(res)
    chainconfig = cc.get_chain_config()
    assert chainconfig.account_config.enable_gas is origin_enable_gas


# 测试通过 ✅
@allure.feature('获取更新链配置')
class TestChainConfigCoreBlockUpdate:

    def test_chain_config_core_update(self, cc):
        tx_scheduler_timeout = 20
        tx_scheduler_validate_timeout = 20
        payload = cc.create_chain_config_core_update_payload(tx_scheduler_timeout, tx_scheduler_validate_timeout)
        print(json_format.MessageToJson(payload))
        
        res = cc.send_manage_request(payload, with_sync_result=True)
        check_response(res)
        
        chain_config = cc.get_chain_config()
        assert chain_config.core.tx_scheduler_timeout == 20 and chain_config.core.tx_scheduler_validate_timeout == 20
    
    def test_chain_config_core_update_tx_scheduler_timeout(self, cc, create_endorsers):
        chain_config = cc.get_chain_config()
        origin_tx_scheduler_validate_timeout = chain_config.core.tx_scheduler_validate_timeout
        tx_scheduler_timeout = 30
        payload = cc.create_chain_config_core_update_payload(tx_scheduler_timeout=tx_scheduler_timeout)
        
        endorsers = create_endorsers(payload)
        res = cc.send_request_with_sync_result(payload, endorsers=endorsers, with_sync_result=True)
        
        chain_config = cc.get_chain_config()
        assert chain_config.core.tx_scheduler_timeout == 30 and chain_config.core.tx_scheduler_validate_timeout == origin_tx_scheduler_validate_timeout
    
    def test_chain_config_block_update(self, cc, create_endorsers):
        tx_timestamp_verify = 'false'
        tx_timeout = 700
        block_tx_capacity = 110
        block_size = 20
        block_interval = 1100
        tx_parameter_size = 11
        
        payload = cc.create_chain_config_block_update_payload(tx_timestamp_verify, tx_timeout, block_tx_capacity,
                                                              block_size, block_interval, tx_parameter_size)
        endorsers = create_endorsers(payload)
        res = cc.send_request_with_sync_result(payload, endorsers=endorsers, with_sync_result=True)
        assert res.code == 0, res.contract_result
        chain_config = cc.get_chain_config()
        print(chain_config)
        assert chain_config.block.tx_timestamp_verify is False
        assert chain_config.block.tx_timeout == 700
        assert chain_config.block.block_tx_capacity == 110
        assert chain_config.block.block_size == 20
        assert chain_config.block.block_interval == 1100
        assert chain_config.block.tx_parameter_size == 11
    
    def test_chain_config_block_update_block_interval(self, cc, create_endorsers):
        block_interval = 1200
        
        payload = cc.create_chain_config_block_update_payload(block_interval=block_interval)
        endorsers = create_endorsers(payload)
        res = cc.send_request_with_sync_result(payload, endorsers=endorsers, with_sync_result=True)
        assert res.code == 0, res.contract_result
        chain_config = cc.get_chain_config()
        print(chain_config)
        assert chain_config.block.tx_timestamp_verify is False
        assert chain_config.block.tx_timeout == 700
        assert chain_config.block.block_tx_capacity == 110
        assert chain_config.block.block_size == 20
        assert chain_config.block.block_interval == 1200
    
    def test_create_chain_config_block_update_payload(self, cc):
        tx_timestamp_verify = 'true'
        tx_timeout = 600
        block_tx_capacity = 100
        block_size = 10
        block_interval = 2000
        
        payload = cc.create_chain_config_block_update_payload(tx_timestamp_verify, tx_timeout, block_tx_capacity,
                                                              block_size, block_interval)
        print(type(payload), payload)


# 测试通过 ✅
@allure.feature('获取更新链配置')
class TestChainConfigTrustRootManage:
    
    @allure.story('更新TrustRoot')
    def test_update_trust_root(self, cc, node_org_id, trust_root_crt):
        with allure.step('更新trust_root'):
            payload = cc.create_chain_config_trust_root_update_payload(node_org_id, [trust_root_crt])
            res = cc.send_manage_request(payload)
            assert res.code == 0, res.contract_result
    
    @allure.story('删除添加TrustRoot')
    def test_delete_add_trust_root(self, cc, config_dir, node_org_id, trust_root_crt, node_id):
        """测试删除添加trust_toot"""
        with allure.step('删除共识组织'):
            payload = cc.create_chain_config_consensus_node_org_delete_payload(node_org_id=node_org_id)
            res = cc.send_manage_request(payload, with_sync_result=True)
            # code==4 delete node org failed, param orgId[wx-org4.chainmaker.org] not found from nodes 不存在也视为成功
            assert res.code in [0, 4], f'删除共识组织失败 {res.contract_result}'
        
        with allure.step('删除trust_root'):
            payload = cc.create_chain_config_trust_root_delete_payload(node_org_id)
            res = cc.send_manage_request(payload, with_sync_result=True)
            print('删除trust_root响应', res)
            assert res.code in [0, 4], f'删除trust_root失败 {res.contract_result}'
            if res.code == 0:
                for i in range(10):
                    chain_config = cc.get_chain_config()
                    if node_org_id not in [item.org_id for item in chain_config.trust_roots]:
                        break
                    time.sleep(1)
        
        with allure.step('添加trust_root'):
            payload = cc.create_chain_config_trust_root_add_payload(node_org_id, [trust_root_crt])
            res = cc.send_manage_request(payload)
            assert res.code == 0, res.contract_result
            for i in range(10):
                chain_config = cc.get_chain_config()
                if node_org_id == chain_config.trust_roots[-1].org_id:
                    break
                time.sleep(1)
        
        with allure.step('添加共识组织'):
            payload = cc.create_chain_config_consensus_node_org_add_payload(node_org_id, [node_id])
            res = cc.send_manage_request(payload)
            assert res.code == 0, f'添加共识组织失败 {res.contract_result}'
            chain_config = cc.get_chain_config()
            assert node_org_id in [item.org_id for item in chain_config.trust_roots]


@allure.feature('获取更新链配置')
class TestChainConfigNodeIdManage:
    
    @allure.story('更新-删除-添加共识NodeId')
    def test_chain_config_consensus_node_id_update_delete_add(self, cc, config_dir, node_org_id, node_id):
        """测试删除添加node_id"""
        with allure.step('升级共识id'):
            payload = cc.create_chain_config_consensus_node_id_update_payload(node_org_id, node_id, node_id)
            res = cc.send_manage_request(payload)
            chain_config = cc.get_chain_config()
            print(chain_config.consensus.nodes)
            assert res.code in [0, 4], res.contract_result
            for node in chain_config.consensus.nodes:
                if node.org_id == node_org_id:
                    assert node_id in node.node_id
        
        with allure.step('删除共识id'):
            payload = cc.create_chain_config_consensus_node_id_delete_payload(node_org_id, node_id)
            res = cc.send_manage_request(payload, with_sync_result=True)
            print('删除共识id响应', res)
            assert res.code in [0, 4], res.contract_result
            
            chain_config = cc.get_chain_config()
            consensus_node_ids = []
            for node in chain_config.consensus.nodes:
                if node.org_id == node_org_id:
                    consensus_node_ids = node.node_id
            
            assert node_id not in consensus_node_ids
        
        with allure.step('添加共识id'):
            node_ids = [node_id]
            payload = cc.create_chain_config_consensus_node_id_add_payload(node_org_id, node_ids)
            res = cc.send_manage_request(payload)
            assert res.code == 0, res.contract_result
            chain_config = cc.get_chain_config()
            
            consensus_node_ids = []
            for node in chain_config.consensus.nodes:
                if node.org_id == node_org_id:
                    consensus_node_ids = node.node_id
            
            assert node_id in consensus_node_ids


@allure.feature('获取更新链配置')
class TestChainConfigNodeOrgManage:
    
    @allure.story('更新-删除-添加共识组织')
    def test_chain_config_consensus_node_org_update_delete_add(self, cc, config_dir, node_org_id, node_id):
        """测试共识组织删除-添加"""
        print('更新共识组织')
        node_ids = [node_id]
        payload = cc.create_chain_config_consensus_node_org_update_payload(node_org_id, node_ids)
        res = cc.send_manage_request(payload)
        assert res.code == 0, res.contract_result
        
        print('删除共识组织')
        payload = cc.create_chain_config_consensus_node_org_delete_payload(node_org_id)
        res = cc.send_manage_request(payload)
        assert res.code == 0, res.contract_result
        
        chain_config = cc.get_chain_config()
        assert node_org_id not in [node.org_id for node in chain_config.consensus.nodes]
        
        print('添加共识组织')
        node_ids = [node_id]
        payload = cc.create_chain_config_consensus_node_org_add_payload(node_org_id, node_ids)
        res = cc.send_manage_request(payload)
        assert res.code == 0, res.contract_result
        
        chain_config = cc.get_chain_config()
        assert node_org_id in [node.org_id for node in chain_config.consensus.nodes]


@allure.feature('获取更新链配置')
class TestChainConfigPermissionManage:
    """测试链配置-权限管理"""
    
    @allure.story('创建策略')
    def test_create_policy(self, cc):
        policy = cc.create_policy(rule='MAJORITY', role_list=['ADMIN'])
        print(type(policy), policy)
    
    @allure.story('链配置更新权限')
    def test_chain_config_permission_update(self, cc, create_endorsers):
        print(cc.get_chain_config().resource_policies)
        permission_resource_name = 'CHAIN_CONFIG-TRUST_ROOT_ADD'
        policy = cc.create_policy(rule='MAJORITY', role_list=['ADMIN'])
        payload = cc.create_chain_config_permission_update_payload(permission_resource_name, policy)
        endorsers = create_endorsers(payload)
        res = cc.send_request_with_sync_result(payload, endorsers=endorsers, with_sync_result=True)
        
        assert res.code == 0, res.contract_result
        print(cc.get_chain_config().resource_policies)
    
    @allure.story('链配置删除权限')
    def test_chain_config_permission_delete(self, cc, create_endorsers):
        permission_resource_name = 'CHAIN_CONFIG-TRUST_ROOT_DELETE'
        payload = cc.create_chain_config_permission_delete_payload(permission_resource_name)
        print(type(payload), payload)
        endorsers = create_endorsers(payload)
        res = cc.send_request_with_sync_result(payload, endorsers=endorsers, with_sync_result=True)
        assert res.code == 0, res.contract_result
        print(cc.get_chain_config().resource_policies)


@allure.feature('获取更新链配置')
class TestChainConfigConsensusExtManage:
    
    @allure.story('链配置添加共识Ext')
    def test_chain_config_consensus_ext_add(self, cc, create_endorsers):
        print(cc.get_chain_config())
        params = {"org_id": "wx-org3"}
        payload = cc.create_chain_config_consensus_ext_add_payload(params)
        endorsers = create_endorsers(payload)
        res = cc.send_request_with_sync_result(payload, endorsers=endorsers, with_sync_result=True)
        assert res.code == 0, res.contract_result
        print(cc.get_chain_config().consensus.ext_config)
    
    @allure.story('链配置更新共识Ext')
    def test_chain_config_consensus_ext_update(self, cc, create_endorsers):
        params = {"org_id": "wx-org4"}
        payload = cc.create_chain_config_consensus_ext_update_payload(params)
        endorsers = create_endorsers(payload)
        res = cc.send_request_with_sync_result(payload, endorsers=endorsers, with_sync_result=True)
        assert res.code == 0, res.contract_result
        print(cc.get_chain_config().consensus.ext_config)
    
    @allure.story('链配置删除共识Ext')
    def test_chain_config_consensus_ext_delete(self, cc, create_endorsers):
        keys = ["org_id"]
        payload = cc.create_chain_config_consensus_ext_delete_payload(keys)
        print(type(payload), payload)
        endorsers = create_endorsers(payload)
        res = cc.send_request_with_sync_result(payload, endorsers=endorsers, with_sync_result=True)
        assert res.code == 0, res.contract_result
        print(cc.get_chain_config().consensus.ext_config)


@allure.feature('获取更新链配置')
class TestChainConfigTrustMember:
    
    @allure.story("链配置添加删除TrustMember第三方伙伴")
    def test_chain_config_add_delete_trust_member(self, cc, node_org_id, node_id, trust_root_crt):
        trust_member_org_id = node_org_id
        trust_member_node_id = node_id
        trust_member_info = trust_root_crt
        trust_member_role = 'admin'
        payload = cc.create_chain_config_trust_member_add_payload(trust_member_org_id, trust_member_node_id,
                                                                  trust_member_info, trust_member_role)
        
        res = cc.send_manage_request(payload)
        check_response(res)
        chain_config = cc.get_chain_config()
        trust_member = chain_config.trust_members[0]
        assert trust_member_org_id == trust_member.org_id
        assert trust_member_node_id == trust_member.node_id
        assert trust_member_info == trust_member.member_info
        assert trust_member_role == trust_member.role
        
        payload = cc.create_chain_config_trust_member_delete_payload(trust_member_info)
        res = cc.send_manage_request(payload)
        check_response(res)
        
        chain_config = cc.get_chain_config()
        trust_member_infos = [trust_member.member_info for trust_member in chain_config.trust_members]
        assert trust_member not in trust_member_infos
