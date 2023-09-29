#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# @FileName     :   test_subscribe.py
# @Function     :   测试订阅接口
"""
    Function        :    Input you funcion 
    Author          :    superhin
    Create time     :    2021/11/24
    Function List   :

"""
import re
import threading

import allure


@allure.feature('订阅')
class TestSubscribe:
    def test_subscribe_current_block(self, cc):
        start_block = 0
        end_block = cc.get_current_block_height()
        res = cc.subscribe_block(start_block, end_block, with_rw_set=False, only_header=False)
        print(type(res))
        count = 0
        for block_info in res:
            count += 1
            print('订阅到区块', block_info.block.header.block_height)
        assert end_block - start_block + 1 == count

    def test_subscribe_block_while_putting_block(self, cc, send_tx):
        current_height = cc.get_current_block_height()
        print('当前高度', current_height)
        start_block = current_height - 3
        end_block = current_height + 13

        t = threading.Thread(target=send_tx, args=(15,))
        print('启动线程，发送交易')
        t.start()
        # send_tx(5)
     
        res = cc.subscribe_block(start_block, end_block, with_rw_set=False, only_header=False)
        count = 0
        for block_info in res:
            count += 1
            print(count, '订阅到区块', block_info.block.header.block_height)
        t.join()
        assert end_block - start_block + 1 == count
        
    def test_subscribe_block_only_header(self, cc):
        start_block = 0
        end_block = cc.get_current_block_height()
        res = cc.subscribe_block(start_block, end_block, with_rw_set=False, only_header=True)
        count = 0
        for block_header in res:
            count += 1
            print(count, '订阅到区块头', block_header.block_height)
        assert end_block - start_block + 1 == count
    
    def test_subscribe_block_with_rwset(self, cc):
        start_block = 0
        end_block = cc.get_current_block_height()
        res = cc.subscribe_block(start_block, end_block, with_rw_set=True, only_header=False)
        count = 0
        for block_with_rwset in res:
            count += 1
            assert 'BlockWithRWSet' == block_with_rwset.__class__.__name__
            assert len(block_with_rwset.txRWSets) > 0, '读写集字段中应包含内容'
        assert end_block - start_block + 1 == count

    def test_subscribe_tx(self, cc, send_tx):
        start_block = 0
        end_block = cc.get_current_block_height()
        contract_name = 'fact'
        
        res = cc.subscribe_tx(start_block, end_block, contract_name, tx_ids=[])
        count = 0
        for transaction in res:
            count += 1
            # print(transaction)
            assert 'fact' == transaction.result.contract_result.contract_event[0].contract_name, transaction.result
        print('count', count)
    
    def test_subscribe_contract_event(self, cc, send_tx):
        start_block = 0
        end_block = cc.get_current_block_height()
        topic = 'topic_vx'
        contract_name = 'fact'
        res = cc.subscribe_contract_event(start_block, end_block, topic, contract_name)
        count = 0
        for contract_event_info_list in res:
            # print(type(contract_event_info_list))
            count += 1
            assert topic == contract_event_info_list.contract_events[0].topic
            assert contract_name == contract_event_info_list.contract_events[0].contract_name
        print('count', count)
        
    def test_subscribe(self, cc, capsys):
        start_block = 0
        end_block = cc.get_current_block_height()
    
        payload = cc.create_subscribe_block_payload(start_block, end_block)
    
        cc.subscribe(payload)
        out, err = capsys.readouterr()
        count = len(re.findall('receive data', out.strip()))
    
        assert end_block - start_block + 1 == count

