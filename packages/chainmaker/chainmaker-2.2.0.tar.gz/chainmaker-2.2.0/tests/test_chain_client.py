#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# @FileName     :   test_chain_client.py
# @Function     :   测试链客户端

import os

import pytest
import yaml

from chainmaker.apis.base_client import AuthType
from chainmaker.chain_client import ChainClient
from tests.utils.cropto_config_utils import CURRENT_AUTH_TYPE


def test_get_all_nodes_block_height(config_dir, sdk_config_path):
    os.chdir(config_dir)
    with open(sdk_config_path, encoding='utf-8') as f:
        data = yaml.safe_load(f)
    nodes_cnt = len(data['chain_client']['nodes'])
    
    clients = [ChainClient.from_conf(sdk_config_path, node_index=i) for i in range(nodes_cnt)]
    result = [client.get_current_block_height() for client in clients]
    print(result)
    assert len(set(result)) == 1


def test_get_chain_maker_server_version(cc):
    version = cc.get_chainmaker_server_version()
    assert isinstance(version, str)


def test_stop(cc):
    cc.get_chain_info()
    cc.stop()


def test_enable_disable_cert_hash(cc, send_tx):  # ✅
    """测试启用禁用证书哈希"""
    if cc.auth_type != AuthType.PermissionedWithCert or cc.enabled_alias is True:
        pytest.skip('仅支持CERT模式')
    cc.enable_cert_hash()
    assert cc.enabled_crt_hash is True

    res = send_tx()[0]
    res = cc.get_tx_by_tx_id(res.tx_id)

    signer = res.transaction.sender.signer
    assert 1 == signer.member_type, 'member_type应为1即CERT_HASH'
    assert cc.user.sign_cert_hash == signer.member_info
    
    cc.disable_cert_hash()
    assert cc.enabled_crt_hash is False
    
    res = send_tx()[0]
    res = cc.get_tx_by_tx_id(res.tx_id)
    signer = res.transaction.sender.signer
    assert 0 == signer.member_type, 'member_type应为0即CERT'
    assert cc.user.sign_cert_bytes == signer.member_info


@pytest.mark.skipif(CURRENT_AUTH_TYPE!=AuthType.PermissionedWithKey, reason='仅支持pwk模式')
def test_pwk_with_rsa(config_dir):
    sdk_config_file = os.path.join(config_dir, 'sdk_config_pwk.yml')
    os.chdir(config_dir)
    cc = ChainClient.from_conf(sdk_config_file)
    print(cc.get_chain_info())
    
    
    
