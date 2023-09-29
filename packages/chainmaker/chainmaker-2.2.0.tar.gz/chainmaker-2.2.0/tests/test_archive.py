#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# @FileName     :   test_archive.py
# @Function     :   测试归档接口
import hmac
import time

import allure
import pytest

from chainmaker.chain_client import ChainClient
from chainmaker.exceptions import ContractFail
from chainmaker.utils.common import uint64_to_bytes
from chainmaker.utils.file_utils import switch_dir
from chainmaker.utils.gm.sm3 import sm3_hmac, sm3_hash


@pytest.fixture()
def cc_admin(config_dir):
    with switch_dir(config_dir):
        cc = ChainClient.from_conf('sdk_config_with_admin.yml')
        yield cc
    cc.stop()


@allure.feature('归档')
@pytest.mark.skip('归档需要配置chainmaker.yml storage: unarchive_block_height及disable_block_file_db=true')
class TestArchive:
    """归档需要配置chainmaker.yml
    unarchive_block_height: 15
    disable_block_file_db: true
    """
    def test_get_archived_block_height(self, cc_admin):
        height = cc_admin.get_archived_block_height()
        print(height)
    
    def test_get_block_height(self, cc_admin):
        with pytest.raises(ContractFail) as err_msg:
            cc_admin.get_block_by_height(15)
            print(err_msg)
    
    def test_archive_block(self, cc_admin):
        block_height = cc_admin.get_current_block_height()
        print('当前区块高度', block_height)
        payload = cc_admin.create_archive_block_payload(16)
        print(payload)
        res = cc_admin.send_archive_block_request(payload)
        print(res)
    
    def test_restore_block(self, cc_admin):
        block_height = cc_admin.get_current_block_height()
        print('当前区块高度', block_height)
        full_block = cc_admin.get_full_block_by_height(15).SerializeToString()
        payload = cc_admin.create_restore_block_payload(full_block)
        res = cc_admin.send_restore_block_request(payload)
        print(res)
    
    def test_get_archived_full_block_by_height(self, cc_admin):
        block_with_rwset = cc_admin.get_archived_full_block_by_height(1)
        print(block_with_rwset)
    
    def test_get_archived_block_by_height(self, cc_admin):
        block_info = cc_admin.get_archived_block_by_height(1)
        print(block_info.block.txs[0].payload.tx_id)
        print(block_info.block.header.block_hash.hex())
    
    def test_get_archived_block_by_tx_id(self, cc_admin):
        tx_id = 'd15bc83ad9f74bc08d6510ca5a52fabe0854cfdae09e48b9ad525fdf481ac879'
        block_info = cc_admin.get_archived_block_by_tx_id(tx_id)
        print(block_info)
    
    def test_get_archived_block_by_hash(self, cc_admin):
        block_hash = '3f165abbb969741c9f209b23979a6d3fd15b3f90fb3d47a5b6454210bdf21e12'
        block_info = cc_admin.get_archived_block_by_hash(block_hash)
        print(block_info)
    
    def test_get_archived_tx_by_tx_id(self, cc_admin):
        tx_id = 'd15bc83ad9f74bc08d6510ca5a52fabe0854cfdae09e48b9ad525fdf481ac879'
        block_info = cc_admin.get_archived_tx_by_tx_id(tx_id)
        print(type(block_info))
    
    def test_send_tx(self, cc, send_tx):
        for i in range(10):
            send_tx(1, with_sync_result=True)
            time.sleep(1)
        print(cc.get_current_block_height())
