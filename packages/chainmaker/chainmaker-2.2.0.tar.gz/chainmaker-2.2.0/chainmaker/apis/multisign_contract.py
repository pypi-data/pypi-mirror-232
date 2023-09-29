#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# @FileName     :   multisign_contract.py
# @Function     :   ChainMaker 多签接口
from typing import Union

from chainmaker.user import User
from chainmaker.apis.base_client import BaseClient
from chainmaker.keys import SystemContractNames, MultiSignMethods, ParamKeys, VoteStatus
from chainmaker.protos.common.request_pb2 import Payload, EndorsementEntry
from chainmaker.protos.common.result_pb2 import TxResponse
from chainmaker.protos.syscontract.multi_sign_pb2 import MultiSignVoteInfo, MultiSignInfo
from chainmaker.utils import result_utils


class MultiSignContractMixin(BaseClient):
    def multi_sign_contract_req(self, payload: Payload, timeout: int = None, with_sync_result: bool = False) -> TxResponse:
        """
        发起多签请求
        :param payload: 待签名payload
        :param timeout: 请求超时时间
        :param with_sync_result: 是否同步获取交易结果
        :return: 交易响应或交易信息
        """
        return self.send_request_with_sync_result(payload, timeout=timeout, with_sync_result=with_sync_result)
    
    def multi_sign_contract_vote(self, multi_sign_req_payload, endorser: User, is_agree: bool = True,
                                 timeout: int = None, with_sync_result: bool = False) -> TxResponse:
        """
        对请求payload发起多签投票
        :param multi_sign_req_payload: 待签名payload
        :param endorser: 投票用户对象
        :param is_agree: 是否同意，true为同意，false则反对
        :param timeout: 请求超时时间
        :param with_sync_result: 是否同步获取交易结果
        :return: 交易响应或交易信息
        """
        vote_status = VoteStatus.AGREE if is_agree is True else VoteStatus.REJECT
        payload_bytes = multi_sign_req_payload.SerializeToString()
        vote_info = self._create_vote_info(vote_status=vote_status, endorsement=endorser.endorse(payload_bytes))
        
        params = {
            ParamKeys.VOTE_INFO: vote_info.SerializeToString(),
            ParamKeys.TX_ID: multi_sign_req_payload.tx_id
        }
        payload = self._create_multi_sign_vote_payload(params)
        return self.send_request_with_sync_result(payload, timeout=timeout, with_sync_result=with_sync_result)
    
    def multi_sign_contract_vote_tx_id(self, tx_id, endorser: User, is_agree: bool,
                                       timeout: int = None, with_sync_result: bool = False) -> TxResponse:
        """
        对交易ID发起多签投票
        :param tx_id: 交易ID
        :param endorser: 投票用户对象
        :param is_agree: 是否同意，true为同意，false则反对
        :param timeout: 请求超时时间
        :param with_sync_result: 是否同步获取交易结果
        :return: 交易响应或交易信息
        """
        tx = self.get_tx_by_tx_id(tx_id)
        payload = tx.transaction.payload
        payload_bytes = payload.SerializeToString()
        vote_status = VoteStatus.AGREE if is_agree is True else VoteStatus.REJECT
        vote_info = self._create_vote_info(vote_status=vote_status, endorsement=endorser.endorse(payload_bytes))
        params = {
            ParamKeys.VOTE_INFO: vote_info.SerializeToString(),
            ParamKeys.TX_ID: tx_id
        }
        
        payload = self._create_multi_sign_vote_payload(params)
        return self.send_request_with_sync_result(payload, timeout=timeout, with_sync_result=with_sync_result)
    
    def multi_sign_contract_query(self, tx_id: str) -> MultiSignInfo:
        """
        根据交易ID查询多签状态
        :param tx_id: 交易ID
        :return: 多签信息
        """
        params = {
            ParamKeys.TX_ID: tx_id
        }
        payload = self._create_multi_sign_query_payload(params)
        response = self.send_request_with_sync_result(payload)
        assert result_utils.result_is_ok(response), f'响应失败: {response}'
        multi_sign_info = MultiSignInfo()
        multi_sign_info.ParseFromString(response.contract_result.result)
        return multi_sign_info
    
    def create_multi_sign_req_payload(self, params: Union[list, dict]) -> Payload:
        """
        根据发起多签请求所需的参数构建payload
        :param params: 发起多签请求所需的参数
        :return: 待签名Payload
        """
        return self.payload_builder.create_invoke_payload(SystemContractNames.MULTI_SIGN, MultiSignMethods.REQ,
                                                          params)
    
    def _create_multi_sign_vote_payload(self, params: Union[list, dict]) -> Payload:
        """
        生成多签投票待签名Payload
        :param params: 发起投票请求所需参数
        :return: 待签名Payload
        """
        return self.payload_builder.create_invoke_payload(SystemContractNames.MULTI_SIGN, MultiSignMethods.VOTE,
                                                          params)
    
    def _create_multi_sign_query_payload(self, params: Union[list, dict]) -> Payload:
        """
        生成查询多签状态待签名Payload
        :param params: 查询多签状态请求所需参数
        :return: 待签名Payload
        """
        return self.payload_builder.create_query_payload(SystemContractNames.MULTI_SIGN, MultiSignMethods.QUERY,
                                                         params)
    
    @staticmethod
    def _create_vote_info(vote_status: str, endorsement: EndorsementEntry) -> MultiSignVoteInfo:
        """
        创建多签投票信息结构体
        :param vote_status: AGREE或REJECT
        :param endorsement: 背书项
        :return: 多签投票信息结构体
        """
        return MultiSignVoteInfo(
            vote=vote_status,
            endorsement=endorsement
        )
