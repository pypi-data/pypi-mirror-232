#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# @FileName     :   gas_manage.py
# @Function     :   ChainMaker Gas计费管理接口
from typing import Union, List

from chainmaker.apis.base_client import BaseClient
from chainmaker.keys import SystemContractNames, AccountManagerMethods, ParamKeys, RechargeGasItem
from chainmaker.protos.common.request_pb2 import Payload
from chainmaker.protos.common.result_pb2 import TxResponse, Result
from chainmaker.protos.syscontract.account_manager_pb2 import RechargeGas, RechargeGasReq




class GasManageMixIn(BaseClient):
    """Gas计费管理"""
    
    def get_gas_admin(self) -> str:
        """
        查询Gas管理员地址
        :return: Gas管理员账户地址
        """
        self.logger.debug("[SDK] begin to get gas admin")
        
        payload = self.payload_builder.create_query_payload(SystemContractNames.ACCOUNT_MANAGER, AccountManagerMethods.GET_ADMIN,
                                                            params=[])
        res = self.send_request_with_sync_result(payload)
        return res.contract_result.result.decode()
    
    def get_gas_balance(self, address: str) -> int:
        """
        获取Gas账户余额
        :param str address: 账户地址
        :return:
        """
        self.logger.debug("[SDK] begin to get gas gas balance, [address:%s]", address)
        
        params = {ParamKeys.address_key: address}
        payload = self.payload_builder.create_query_payload(SystemContractNames.ACCOUNT_MANAGER,
                                                            AccountManagerMethods.GET_BALANCE, params)
        res = self.send_request_with_sync_result(payload)
        balance = int(res.contract_result.result.decode())
        return balance
    
    def get_gas_account_status(self, address: str) -> bool:
        """
        查询Gas账户状态
        :param str address: 账户地址
        :return: 正常是返回True, 冻结返回False
        """
        self.logger.debug("[SDK] begin to get gas account status, [address:%s]", address)
        
        params = {ParamKeys.address_key: address}
        payload = self.payload_builder.create_query_payload(SystemContractNames.ACCOUNT_MANAGER,
                                                            AccountManagerMethods.ACCOUNT_STATUS, params)
        res = self.send_request_with_sync_result(payload)
        return b'0' == res.contract_result.result
    
    def create_set_gas_admin_payload(self, address: str) -> Payload:
        """
        创建设置Gas管理员Payload
        :param address: 管理员账户地址
        :return: Payload
        """
        self.logger.debug("[SDK] begin to create [SetGasAdmin] to be signed payload, [address:%s]", address)
        
        params = {ParamKeys.address_key: address}
        return self.payload_builder.create_invoke_payload(SystemContractNames.ACCOUNT_MANAGER, AccountManagerMethods.SET_ADMIN,
                                                          params)
    
    def create_recharge_gas_payload(self, recharge_gas_list: List[RechargeGasItem]) -> Payload:
        """
        创建Gas充值Payload
        :param recharge_gas_list: 充值列表
        :return: Payload
        """
        self.logger.debug("[SDK] begin to create [RechargeGas] to be signed payload, [recharge_gas_list:%s]", recharge_gas_list)
        
        batch_recharge_gas = [RechargeGas(address=item.address, gas_amount=item.amount) for item in recharge_gas_list]
        recharge_gas_req = RechargeGasReq(batch_recharge_gas=batch_recharge_gas).SerializeToString()
        
        params = {ParamKeys.batch_recharge: recharge_gas_req}  # Fixme
        
        return self.payload_builder.create_invoke_payload(SystemContractNames.ACCOUNT_MANAGER, AccountManagerMethods.RECHARGE_GAS,
                                                          params)
    
    def create_refund_gas_payload(self, address: str, amount: int) -> Payload:
        """
        创建Gas退款Payload
        :param address: 账户地址
        :param amount: 退款额度
        :return: Payload
        """
        self.logger.debug("[SDK] begin to create [RefundGas] to be signed payload, [address:%s]/[amount:%s]", address,
                          amount)
        
        if amount <= 0:
            raise ValueError('amount must > 0')
        
        params = {ParamKeys.address_key: address, ParamKeys.charge_gas_amount: amount}
        
        return self.payload_builder.create_invoke_payload(SystemContractNames.ACCOUNT_MANAGER, AccountManagerMethods.REFUND_GAS,
                                                          params)
    
    def create_frozen_gas_account_payload(self, address: str) -> Payload:
        """
        创建冻结账户Payload
        :param address: 账户地址
        :return: Payload
        """
        self.logger.debug("[SDK] begin to create [FrozenGasAccount] to be signed payload, [address:%s]", address)
        
        params = {ParamKeys.address_key: address}
        return self.payload_builder.create_invoke_payload(SystemContractNames.ACCOUNT_MANAGER,
                                                          AccountManagerMethods.FROZEN_ACCOUNT, params)
    
    def create_unfrozen_gas_account_payload(self, address: str) -> Payload:
        """
        创建解冻账户Payload
        :param address: 账户地址
        :return: Payload
        """
        self.logger.debug("[SDK] begin to create [UnFrozenGasAccount] to be signed payload, [address:%s]", address)
        
        params = {ParamKeys.address_key: address}
        return self.payload_builder.create_invoke_payload(SystemContractNames.ACCOUNT_MANAGER,
                                                          AccountManagerMethods.UNFROZEN_ACCOUNT, params)
    
    def send_gas_manage_request(self, payload: Payload, endorsers: list, timeout: int = None,
                                with_sync_result: bool = True) -> Union[TxResponse, Result]:
        """
        发送Gas管理请求
        :param payload: Payload
        :param endorsers: 背书列表
        :param timeout: 超时时间
        :param with_sync_result: 是否同步轮询结果
        :return: 响应信息
        """
        return self.send_request_with_sync_result(payload, endorsers, timeout, with_sync_result)
    
    @staticmethod
    def attach_gas_limit(payload: Payload, gas_limit: int) -> Payload:
        """
        设置Gas转账限制
        :param payload: Payload
        :param gas_limit: Gas交易限制
        :return: Payload
        """
        payload.limit.gas_limit = gas_limit
        return payload
