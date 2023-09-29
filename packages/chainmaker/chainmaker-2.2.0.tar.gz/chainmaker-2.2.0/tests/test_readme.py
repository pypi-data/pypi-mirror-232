#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# @FileName     :   test_readme.py
# @Function     :   测试readme文档示例
import allure


@allure.story('测试以参数形式创建ChainClient')
def test_create_chain_client_with_args(crypto_config_path):
    from chainmaker.chain_client import ChainClient
    from chainmaker.node import Node
    from chainmaker.user import User
    from chainmaker.utils import file_utils
    
    user = User('wx-org1.chainmaker.org',
                sign_key_bytes=file_utils.read_file_bytes(f'{crypto_config_path}/wx-org1.chainmaker.org/user/client1/client1.tls.key'),
                sign_cert_bytes=file_utils.read_file_bytes(f'{crypto_config_path}/wx-org1.chainmaker.org/user/client1/client1.tls.crt'),
                tls_key_bytes=file_utils.read_file_bytes(f'{crypto_config_path}/wx-org1.chainmaker.org/user/client1/client1.sign.key'),
                tls_cert_bytes=file_utils.read_file_bytes(f'{crypto_config_path}/wx-org1.chainmaker.org/user/client1/client1.sign.crt')
                )
    
    node = Node(
        node_addr='127.0.0.1:12301',
        conn_cnt=1,
        enable_tls=True,
        trust_cas=[
            file_utils.read_file_bytes(f'{crypto_config_path}/wx-org1.chainmaker.org/ca/ca.crt'),
            file_utils.read_file_bytes(f'{crypto_config_path}/wx-org2.chainmaker.org/ca/ca.crt')
        ],
        tls_host_name='chainmaker.org'
    )
    
    cc = ChainClient(chain_id='chain1', user=user, nodes=[node])
    print(cc.get_chainmaker_server_version())


@allure.story('以配置文件形式创建ChainClient')
def test_create_chain_client_with_sdk_config(sdk_config_path):
    from chainmaker.chain_client import ChainClient
    from chainmaker.utils.file_utils import switch_dir

    sdk_config_file = sdk_config_path
    with switch_dir(sdk_config_file):
        cc = ChainClient.from_conf(sdk_config_path)
    print(cc.get_chainmaker_server_version())

@allure.story('创建合约')
def test_create_contract(crypto_config_path, sdk_config_path, testdata_dir):
    from google.protobuf import json_format
    from chainmaker.utils.file_utils import switch_dir
    from chainmaker.chain_client import ChainClient
    from chainmaker.utils.evm_utils import calc_evm_contract_name
    from chainmaker.keys import RuntimeType
    
    endorsers_config = [{'org_id': 'wx-org1.chainmaker.org',
                         'user_sign_crt_file_path': f'{crypto_config_path}/wx-org1.chainmaker.org/user/admin1/admin1.sign.crt',
                         'user_sign_key_file_path': f'{crypto_config_path}/wx-org1.chainmaker.org/user/admin1/admin1.sign.key'},
                        {'org_id': 'wx-org2.chainmaker.org',
                         'user_sign_crt_file_path': f'{crypto_config_path}/wx-org2.chainmaker.org/user/admin1/admin1.sign.crt',
                         'user_sign_key_file_path': f'{crypto_config_path}/wx-org2.chainmaker.org/user/admin1/admin1.sign.key'},
                        {'org_id': 'wx-org3.chainmaker.org',
                         'user_sign_crt_file_path': f'{crypto_config_path}/wx-org3.chainmaker.org/user/admin1/admin1.sign.crt',
                         'user_sign_key_file_path': f'{crypto_config_path}/wx-org3.chainmaker.org/user/admin1/admin1.sign.key'},
                        ]

    with switch_dir(sdk_config_path):
        cc = ChainClient.from_conf(sdk_config_path)
    
    def create_contract(contract_name: str, version: str, byte_code_path: str, runtime_type: RuntimeType,
                        params: dict = None,
                        with_sync_result=True) -> dict:
        """创建合约"""
        # 创建请求payload
        payload = cc.create_contract_create_payload(contract_name, version, byte_code_path, runtime_type, params)
        # 创建背书
        endorsers = cc.create_endorsers(payload, endorsers_config)
        # 携带背书发送请求
        res = cc.send_request_with_sync_result(payload, with_sync_result=with_sync_result, endorsers=endorsers)
        # 交易响应结构体转为字典格式
        return json_format.MessageToDict(res)
    
    # 创建WASM合约，本地合约文件./testdata/claim-wasm-demo/rust-fact-2.0.0.wasm应存在
    result1 = create_contract('fact', '1.0', f'{testdata_dir}/byte_codes/rust-fact-2.0.0.wasm', RuntimeType.WASMER, {})
    print(result1)
    
    # 创建EVM合约，本地合约文件./testdata/balance-evm-demo/ledger_balance.bin应存在
    
    contract_name = calc_evm_contract_name('balance001')
    result2 = create_contract(contract_name, '1.0', f'{testdata_dir}/byte_codes/ledger_balance.bin', RuntimeType.EVM)
    print(result2)

@allure.story('调用合约')
def test_invoke_contract(sdk_config_path):
    from google.protobuf import json_format
    from chainmaker.chain_client import ChainClient
    from chainmaker.utils.file_utils import switch_dir
    from chainmaker.utils.evm_utils import calc_evm_contract_name, calc_evm_method_params
    
    # 创建客户端
    sdk_config_file = sdk_config_path
    with switch_dir(sdk_config_file):
        cc = ChainClient.from_conf(sdk_config_file)
    
    # 调用WASM合约
    res1 = cc.invoke_contract('fact', 'save',
                              {"file_name": "name007", "file_hash": "ab3456df5799b87c77e7f88", "time": "6543234"},
                              with_sync_result=True)
    # 交易响应结构体转为字典格式
    print(json_format.MessageToDict(res1))
    
    # 调用EVM合约
    evm_contract_name = calc_evm_contract_name('balance001')
    evm_method, evm_params = calc_evm_method_params('updateBalance', [{"uint256": "10000"}, {
        "address": "0xa166c92f4c8118905ad984919dc683a7bdb295c1"}])
    res2 = cc.invoke_contract(evm_contract_name, evm_method, evm_params, with_sync_result=True)
    # 交易响应结构体转为字典格式
    print(json_format.MessageToDict(res2))
