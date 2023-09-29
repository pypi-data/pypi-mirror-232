#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# @FileName     :   test_auth_type_with_pk.py
# @Function     :   测试Public模式

import os

import allure
import pytest
import yaml

from chainmaker.user import User
from chainmaker.chain_client import ChainClient
from chainmaker.keys import AuthType
from tests.utils.cropto_config_utils import CURRENT_AUTH_TYPE


tests_path = os.path.join(os.path.abspath(os.path.dirname(__file__)))
contract_file = 'resources/rust-counter-2.0.0.wasm'

endorsers_yml = '''
endorsers: # 背书用户
  - user_sign_key_file_path: "./crypto-config/node1/admin/admin1/admin1.key"
    auth_type: public
  - user_sign_key_file_path: "./crypto-config/node2/admin/admin2/admin2.key"
    auth_type: public
  - user_sign_key_file_path: "./crypto-config/node3/admin/admin3/admin3.key"
    auth_type: public
  - user_sign_key_file_path: "./crypto-config/node4/admin/admin4/admin4.key"
    auth_type: public
'''


def create_endorsers(payload):
    """创建背书"""
    payload_bytes = payload.SerializeToString()
    users = yaml.safe_load(endorsers_yml).get("endorsers")
    print('背书用户数量', len(users))
    return [User.from_conf(**item).endorse(payload_bytes) for item in users]

@pytest.fixture()
def cc(request):
    sdk_config_path = os.path.join(request.config.rootdir, 'config', 'sdk_config_pk.yml')
    os.chdir(os.path.dirname(sdk_config_path))
    return ChainClient.from_conf(sdk_config_path)
    

@allure.feature('公钥身份模式')
@pytest.mark.skipif(CURRENT_AUTH_TYPE!=AuthType.Public, reason='仅支持pk模式')
class TestAuthTypePublic:

    @allure.story('获取链信息')
    def test_get_chain_info(self, cc):
        """测试公钥身份模式"""
        chain_info = cc.get_chain_info()
        print(chain_info)
        assert 4 == len(chain_info.node_list)

    @allure.story('更新链配置Core模块')
    def test_chain_config_update_core(self, cc):
        chain_config = cc.get_chain_config()
        tx_scheduler_timeout = 20
        tx_scheduler_validate_timeout = 20
        payload = cc.create_chain_config_core_update_payload(tx_scheduler_timeout, tx_scheduler_validate_timeout)
    
        endorsers = create_endorsers(payload)
        res = cc.send_request_with_sync_result(payload, endorsers=endorsers, with_sync_result=True)
    
        chain_config = cc.get_chain_config()
        assert chain_config.core.tx_scheduler_timeout == 20 and chain_config.core.tx_scheduler_validate_timeout == 20
    

