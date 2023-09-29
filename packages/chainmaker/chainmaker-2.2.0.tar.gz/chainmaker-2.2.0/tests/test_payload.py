#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @FileName     :   def test_playload.py
# @Author       :   superhin
# @CreateTime   :   2022/4/28 11:32
# @Function     :
import pytest

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

@pytest.fixture()
def node_org_id():
    return 'wx-org4.chainmaker.org'

class TestPayload:
    @pytest.mark.payload
    def test_create_chain_config_core_update_payload(self, cc):
        tx_scheduler_timeout = 10
        tx_scheduler_validate_timeout = 10
        payload = cc.create_chain_config_core_update_payload(tx_scheduler_timeout, tx_scheduler_validate_timeout)
        print(type(payload), payload)
    
    @pytest.mark.payload
    def test_create_chain_config_trust_root_add_payload(self, cc, node_org_id, trust_root_crt):
        payload = cc.create_chain_config_trust_root_add_payload(node_org_id, [trust_root_crt])
        print(type(payload), payload)
    
    @pytest.mark.payload
    def test_create_chain_config_trust_root_update_payload(self, cc, node_org_id, trust_root_crt):
        payload = cc.create_chain_config_trust_root_update_payload(node_org_id, [trust_root_crt])
        print(type(payload), payload)
    
    @pytest.mark.payload
    def test_create_chain_config_trust_root_delete_payload(self, cc, node_org_id):
        payload = cc.create_chain_config_trust_root_delete_payload(node_org_id)
        print(type(payload), payload)
    
    @pytest.mark.payload
    def test_create_chain_config_consensus_node_id_add_payload(self, cc, node_org_id, node_id):
        """测试添加共识节点地址待签名payload生成"""
        node_ids = [node_id]
        payload = cc.create_chain_config_consensus_node_id_add_payload(node_org_id, node_ids)
        print(type(payload), payload)
    
    @pytest.mark.payload
    def test_create_chain_config_consensus_node_id_update_payload(self, cc, node_org_id, node_id):
        """测试更新共识节点地址待签名payload生成"""
        node_old_id = node_id
        node_new_id = node_id
        payload = cc.create_chain_config_consensus_node_id_update_payload(node_org_id, node_old_id, node_new_id)
        print(type(payload), payload)
    
    @pytest.mark.payload
    def test_create_chain_config_consensus_node_id_delete_payload(self, cc, node_org_id, node_id):
        """测试删除共识节点地址待签名payload生成"""
        payload = cc.create_chain_config_consensus_node_id_delete_payload(node_org_id, node_id)
        print(type(payload), payload)
    
    @pytest.mark.payload
    def test_create_chain_config_consensus_node_org_add_payload(self, cc, node_id, node_org_id):
        node_ids = [node_id]
        payload = cc.create_chain_config_consensus_node_org_add_payload(node_org_id, node_ids)
        print(type(payload), payload)
    
    @pytest.mark.payload
    def test_create_chain_config_consensus_node_org_update_payload(self, cc, node_id, node_org_id):
        node_ids = [node_id]
        payload = cc.create_chain_config_consensus_node_org_update_payload(node_org_id, node_ids)
        print(type(payload), payload)
    
    @pytest.mark.payload
    def test_create_chain_config_consensus_node_org_delete_payload(self, cc, node_org_id):
        payload = cc.create_chain_config_consensus_node_org_delete_payload(node_org_id)
        print(type(payload), payload)
    
    @pytest.mark.payload
    def test_create_chain_config_permission_add_payload(self, cc):
        print(cc.get_chain_config().resource_policies)
        permission_resource_name = 'CHAIN_CONFIG-TRUST_ROOT_DELETE'
        policy = cc.create_policy(rule='MAJORITY', role_list=['ADMIN', 'CLIENT'])
        print(policy)
        payload = cc.create_chain_config_permission_add_payload(permission_resource_name, policy)
        print(type(payload), payload)
    
    def test_chain_config_permission_add(self, cc, create_endorsers):
        print(cc.get_chain_config().resource_policies)
        permission_resource_name = 'CHAIN_CONFIG-TRUST_ROOT_DELETE'
        policy = cc.create_policy(rule='MAJORITY', role_list=['ADMIN'])
        payload = cc.create_chain_config_permission_add_payload(permission_resource_name, policy)
        endorsers = create_endorsers(payload)
        res = cc.send_request_with_sync_result(payload, endorsers=endorsers, with_sync_result=True)
        assert res.code == 0, res.contract_result
        print(cc.get_chain_config().resource_policies)
    
    @pytest.mark.payload
    def test_create_chain_config_permission_update_payload(self, cc):
        permission_resource_name = 'CHAIN_CONFIG-TRUST_ROOT_DELETE'
        policy = cc.create_policy(rule='MAJORITY', role_list=['ADMIN'])
        payload = cc.create_chain_config_permission_update_payload(permission_resource_name, policy)
        print(type(payload), payload)
    
    @pytest.mark.payload
    def test_create_chain_config_consensus_ext_add_payload(self, cc):
        print(cc.get_chain_config())
        params = {"org_id": "wx-org3"}
        payload = cc.create_chain_config_consensus_ext_add_payload(params)
        assert 'CHAIN_CONFIG' == payload.contract_name
        assert 'CONSENSUS_EXT_ADD' == payload.method
    
    @pytest.mark.payload
    def test_create_chain_config_consensus_ext_update_payload(self, cc):
        params = {"org_id": "wx-org4"}
        payload = cc.create_chain_config_consensus_ext_update_payload(params)
        assert 'CHAIN_CONFIG' == payload.contract_name
        assert 'CONSENSUS_EXT_UPDATE' == payload.method
    
    @pytest.mark.payload
    def test_create_chain_config_consensus_ext_delete_payload(self, cc):
        keys = ["org_id"]
        payload = cc.create_chain_config_consensus_ext_delete_payload(keys)
        assert 'CHAIN_CONFIG' == payload.contract_name
        assert 'CONSENSUS_EXT_DELETE' == payload.method
    
    @pytest.mark.payload
    def test_create_chain_config_permission_delete_payload(self, cc):
        permission_resource_name = 'CHAIN_CONFIG-TRUST_ROOT_DELETE'
        payload = cc.create_chain_config_permission_delete_payload(permission_resource_name)
        print(type(payload), payload)
    
    @pytest.mark.payload
    def test_create_chain_config_trust_member_add_payload(self, cc, node_org_id, node_id, trust_root_crt):
        trust_member_org_id = node_org_id
        trust_member_node_id = node_id
        trust_member_info = trust_root_crt
        trust_member_role = 'admin'
        payload = cc.create_chain_config_trust_member_add_payload(trust_member_org_id, trust_member_node_id,
                                                                  trust_member_info, trust_member_role)
        assert 'CHAIN_CONFIG' == payload.contract_name
        assert 'TRUST_MEMBER_ADD' == payload.method
    
    @pytest.mark.payload
    def test_create_chain_config_trust_member_delete_payload(self, cc, trust_root_crt):
        trust_member_info = trust_root_crt
        payload = cc.create_chain_config_trust_member_delete_payload(trust_member_info)
        assert 'CHAIN_CONFIG' == payload.contract_name
        assert 'TRUST_MEMBER_DELETE' == payload.method
    
    @pytest.mark.payload
    def test_create_archive_block_payload(self, cc):
        block_height = cc.get_current_block_height()
        
        payload = cc.create_archive_block_payload(block_height)
        print(payload)
    
    @pytest.mark.payload
    def test_create_archive_block_payload(self, cc):
        block_height = cc.get_current_block_height()
        full_block = cc.get_full_block_by_height(block_height).SerializeToString()
        payload = cc.create_restore_block_payload(full_block)
        print(payload)
