#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# @FileName     :   test_multisign_contract.py
# @Function     :   测试多签接口

import os

import allure

from chainmaker.utils import file_utils


@allure.feature('线上多签')
class TestMultiSign:

    @allure.story('多签请求')
    def test_multi_sign_contract_req(self, cc, testdata_dir, create_endorsers, create_contract_name):
        
        byte_code_path = os.path.join(testdata_dir, 'byte_codes', 'rust-counter-2.0.0.wasm')
        byte_code = file_utils.load_byte_code(byte_code_path)

        params = {'SYS_CONTRACT_NAME': 'CONTRACT_MANAGE',
                  'SYS_METHOD': 'INIT_CONTRACT',
                  'CONTRACT_NAME': create_contract_name,
                  'CONTRACT_VERSION': '1.0',
                  'CONTRACT_BYTECODE': byte_code,
                  'CONTRACT_RUNTIME_TYPE': 'WASMER'
                  }
        # params = [{"key": "SYS_CONTRACT_NAME", "value": "CONTRACT_MANAGE", "IsFile": False},
        #           {"key": "SYS_METHOD", "value": "INIT_CONTRACT", "IsFile": False},
        #           {"key": "CONTRACT_NAME", "value": create_contract_name, "IsFile": False},
        #           {"key": "CONTRACT_VERSION", "value": "1.0", "IsFile": False},
        #           {"key": "CONTRACT_BYTECODE", "value": "./testdata/claim-wasm-demo/rust-fact-2.0.0.wasm",
        #            "IsFile": True},
        #           {"key": "CONTRACT_RUNTIME_TYPE", "value": "WASMER", "IsFile": False},
        #           ]
        payload = cc.create_multi_sign_req_payload(params)
        res = cc.multi_sign_contract_req(payload)
        print(res)
        assert 'OK' == res.message

    @allure.story('多签投票(payload）')
    def test_multi_sign_contract_vote(self, cc, users, testdata_dir, create_contract_name):

        byte_code_path = os.path.join(testdata_dir, 'byte_codes', 'rust-counter-2.0.0.wasm')
        byte_code = file_utils.load_byte_code(byte_code_path)

        params = {'SYS_CONTRACT_NAME': 'CONTRACT_MANAGE',
                  'SYS_METHOD': 'INIT_CONTRACT',
                  'CONTRACT_NAME': create_contract_name,
                  'CONTRACT_VERSION': '1.0',
                  'CONTRACT_BYTECODE': byte_code,
                  'CONTRACT_RUNTIME_TYPE': 'WASMER'
                  }
        multi_sign_req_payload = cc.create_multi_sign_req_payload(params)
        res = cc.multi_sign_contract_req(multi_sign_req_payload, with_sync_result=True)
        print(res.tx_id)
        assert res.code == 0, res.contract_result.message

        # admin1投票
        user = users.get('admin1')
        res = cc.multi_sign_contract_vote(multi_sign_req_payload, endorser=user, is_agree=True, with_sync_result=True)
        assert res.code == 0, res.contract_result.message
        
        # admin2投票
        user = users.get('admin2')
        res = cc.multi_sign_contract_vote(multi_sign_req_payload, endorser=user, is_agree=True, with_sync_result=True)
        assert res.code == 0, res.contract_result.message

        # admin3投票
        user = users.get('admin3')
        res = cc.multi_sign_contract_vote(multi_sign_req_payload, endorser=user, is_agree=True, with_sync_result=True)
        assert res.code == 0, res.contract_result.message

    @allure.story('多签请求(tx_id)')
    def test_multi_sign_contract_vote_tx_id(self, cc, users, multi_sign_tx_id):
        user = users.get('admin1')
        # multi_sign_tx_id = 'a6124e0783e041ab869caf257a9bce7b10704fed695a49d8b28ca6fdba95fdf3'
        print(multi_sign_tx_id)
        res = cc.multi_sign_contract_vote_tx_id(tx_id=multi_sign_tx_id, endorser=user, is_agree=False)
        assert res.contract_result.code == 0, res.contract_result.message

    @allure.story('多签查询(tx_id)')
    def test_multi_sign_contract_query(self, cc, create_endorsers, multi_sign_tx_id):
        multi_sign_tx_id = 'a6124e0783e041ab869caf257a9bce7b10704fed695a49d8b28ca6fdba95fdf3'
        print(multi_sign_tx_id)
        multi_sign_info = cc.multi_sign_contract_query(multi_sign_tx_id)
        print(multi_sign_info.status)
        # assert res.contract_result.code == 0, res.contract_result.message
