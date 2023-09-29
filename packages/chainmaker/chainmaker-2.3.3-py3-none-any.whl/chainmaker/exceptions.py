#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# @FileName     :   exceptions.py
# @Function     :   已知异常

# InactiveRpcError = grpc._channel._InactiveRpcError


ERR_MSG_MAP = {
    'Empty update': 'Empty trust_root_paths',
    'failed to connect to all addresses': 'Failed to connect address, please check server, port and trust_root_paths'
}


class OnChainFailedError(Exception):
    """
    failed to put data or tx on chain
    """
    pass


class InvalidParametersError(Exception):
    """
    failed to put data or tx on chain
    """
    pass


class RequestError(Exception):
    """
    We failed to decode ABI output.

    Most likely ABI mismatch.
    """
    
    def __init__(self, err_code, err_msg, *args):
        self.err_code = err_code
        self.err_msg = err_msg
        super().__init__(f'TxStatusCode: {self.err_code} message: {self.err_msg}', *args)


class RpcConnectError(Exception):
    """
    Failed to connect to the rpc server
    """


class Timeout(RequestError):
    pass


class InvalidParameter(RequestError):
    pass


class NoPermission(RequestError):
    pass


class ContractFail(RequestError):
    pass


class InternalError(RequestError):
    pass


class InvalidContractTransactionType(RequestError):
    pass


class InvalidContractParameterContractName(RequestError):
    pass


class InvalidContractParameterMethod(RequestError):
    pass


class InvalidContractParameterInitMethod(RequestError):
    pass


class InvalidContractParameterUpgradeMethod(RequestError):
    pass


class InvalidContractParameterByteCode(RequestError):
    pass


class InvalidContractParameterRuntimeType(RequestError):
    pass


class InvalidContractParameterVersion(RequestError):
    pass


class GetFromTxContextFailed(RequestError):
    pass


class PutIntoTxContextFailed(RequestError):
    pass


class ContractVersionExistFailed(RequestError):
    pass


class ContractVersionNotExistFailed(RequestError):
    pass


class ContractByteCodeNotExistFailed(RequestError):
    pass


class MarshalSenderFailed(RequestError):
    pass


class InvokeInitMethodFailed(RequestError):
    pass


class InvokeUpgradeMethodFailed(RequestError):
    pass


class CreateRuntimeInstanceFailed(RequestError):
    pass


class UnmarshalCreatorFailed(RequestError):
    pass


class UnmarshalSenderFailed(RequestError):
    pass


class GetSenderPkFailed(RequestError):
    pass


class GetCreatorPkFailed(RequestError):
    pass


class GetCreatorFailed(RequestError):
    pass


class GetCreateCertFailed(RequestError):
    pass


class GetSenderCertFailed(RequestError):
    pass


class ContractFreezeFailed(RequestError):
    pass


class ContractTooDeepFailed(RequestError):
    pass


class ContractRevokeFailed(RequestError):
    pass


class ContractInvokeMethodFailed(RequestError):
    pass


class GasBalanceNotEnoughFailed(RequestError):
    pass


TX_RESPONSE_ERROR_MAP = {
    1: Timeout,
    2: InvalidParameter,
    3: NoPermission,
    4: ContractFail,
    5: InternalError,
    
    10: InvalidContractTransactionType,
    11: InvalidContractParameterContractName,
    12: InvalidContractParameterMethod,
    13: InvalidContractParameterInitMethod,
    14: InvalidContractParameterUpgradeMethod,
    15: InvalidContractParameterByteCode,
    16: InvalidContractParameterRuntimeType,
    17: InvalidContractParameterVersion,
    
    20: GetFromTxContextFailed,
    21: PutIntoTxContextFailed,
    22: ContractVersionExistFailed,
    23: ContractVersionNotExistFailed,
    24: ContractByteCodeNotExistFailed,
    25: MarshalSenderFailed,
    26: InvokeInitMethodFailed,
    27: InvokeUpgradeMethodFailed,
    28: CreateRuntimeInstanceFailed,
    29: UnmarshalCreatorFailed,
    30: UnmarshalSenderFailed,
    31: GetSenderPkFailed,
    32: GetCreatorPkFailed,
    33: GetCreatorFailed,
    34: GetCreateCertFailed,
    35: GetSenderCertFailed,
    36: ContractFreezeFailed,
    37: ContractTooDeepFailed,
    38: ContractRevokeFailed,
    39: ContractInvokeMethodFailed,
    
    42: GasBalanceNotEnoughFailed
    
}


class ChainClientException(Exception):
    """客户端异常"""
