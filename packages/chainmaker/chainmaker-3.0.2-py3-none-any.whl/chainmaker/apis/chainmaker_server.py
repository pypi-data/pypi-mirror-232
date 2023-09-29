#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# @FileName     :   chainmaker_server.py
# @Function     :   ChainMaker系统合约(链查询相关)接口
import json
import time
from typing import List
from typing import Union

import grpc

from chainmaker.apis.base_client import BaseClient
from chainmaker.exceptions import ERR_MSG_MAP, RpcConnectError, ContractFail
from chainmaker.keys import TxType, TxStage
from chainmaker.protos import (TxRequest, Transaction, GetConsensusStatusRequest,
                               GetPoolStatusRequest, TxPoolStatus,
                               GetTxIdsByTypeAndStageRequest, GetTxsInPoolByTxIdsRequest)
from chainmaker.protos.common.result_pb2 import Result
from chainmaker.protos.txpool.transaction_pool_pb2 import GetTxStatusRequest
from chainmaker.sdk_config import DefaultConfig
from chainmaker.utils.common import ensure_enum


class ChainMakerServerMixIn(BaseClient):
    """ChainMaker服务操作"""

    def get_chainmaker_server_version(self) -> str:
        """获取chainmaker服务版本号"""
        self._debug('begin to get chainmaker server version')
        tx_request = TxRequest()

        retry_limit = DefaultConfig.rpc_retry_limit
        retry_interval = DefaultConfig.rpc_retry_interval

        err_msg = ''
        for i in range(retry_limit):
            try:
                return self._get_client().GetChainMakerVersion(tx_request).version
            except grpc._channel._InactiveRpcError as ex:
                # todo 处理 DeadlineExceeded
                err_msg = ERR_MSG_MAP.get(ex.details(), ex.details())
                # self._logger.exception(ex)
                time.sleep(retry_interval // 1000)  # 毫秒
                self._logger.debug('[Sdk] %s, retry to send rpc request to %s' % (ex.details(), self.node.node_addr))
        else:
            raise RpcConnectError(
                '[Sdk] rpc service<%s enable_tls=%s> not available: %s' % (
                    self.node.node_addr, self.node.enable_tls, err_msg))


class ConsensusMixIn(BaseClient):
    """共识状态操作"""

    def get_consensus_validators(self) -> List[str]:
        """
        获取所有共识节点的身份标识
        :return: 共识节点身份标识
        :exception: 当查询的节点非共识节点时或共识节点内部查询中出现错误，返回error
        """
        self._debug("begin to GetConsensusValidators")
        req = GetConsensusStatusRequest(chain_id=self.chain_id)
        response = self._get_client().GetConsensusValidators(req)
        return response.nodes

    def get_consensus_height(self) -> int:
        """
        获取节点正在共识的区块高度
        :return:
        """
        self._debug("begin to GetConsensusHeight")
        req = GetConsensusStatusRequest(chain_id=self.chain_id)
        response = self._get_client().GetConsensusHeight(req)
        return response.value

    def get_consensus_state_json(self) -> dict:
        """
        获取共识节点的状态
        :return: 查询的共识节点状态
        """
        self._debug("begin to GetConsensusStateJSON")
        req = GetConsensusStatusRequest(chain_id=self.chain_id)
        response = self._get_client().GetConsensusStateJSON(req)
        return json.loads(response.value)


class TxPoolMixIn(BaseClient):
    """交易池状态操作"""

    def get_pool_status(self) -> TxPoolStatus:
        """
        获取交易池状态
        :return:
        """
        self._debug("begin to get txpool status")
        req = GetPoolStatusRequest(chain_id=self.chain_id)
        return self._get_client().GetPoolStatus(req)

    def get_tx_ids_by_type_and_stage(self, tx_type: Union[TxType, str, int] = None,
                                     tx_stage: Union[TxStage, str, int] = None) -> List[str]:
        """
        获取不同交易类型和阶段中的交易Id列表。
        :param tx_type: 交易类型 在pb的txpool包中进行了定义
        :param tx_stage: 交易阶段 在pb的txpool包中进行了定义
        :return: 交易Id列表
        """
        if tx_type is None:
            tx_type = TxType.ALL_TYPE
        if tx_stage is None:
            tx_stage = TxStage.ALL_STAGE
        tx_type, tx_stage = ensure_enum(tx_type, TxType), ensure_enum(tx_stage, TxStage)
        self._debug("begin to get tx_ids by type and stage: [tx_type:%s]/[tx_stage:%s]" % (tx_type, tx_stage))
        req = GetTxIdsByTypeAndStageRequest(chain_id=self.chain_id,
                                            tx_type=tx_type.value,
                                            tx_stage=tx_stage.value)
        res = self._get_client().GetTxIdsByTypeAndStage(req)
        return res.tx_ids

    def get_txs_in_pool_by_tx_ids(self, tx_ids: List[str]) -> (List[Transaction], List[str]):
        """
        根据txIds获取交易池中存在的txs，并返回交易池缺失的tx的txIds
        :param tx_ids: 交易Id列表
        :return: [交易池中存在的txs, 交易池缺失的tx的txIds]
        """
        self._debug("begin to get transactions in txpool by tx_ids: %s" % tx_ids)

        req = GetTxsInPoolByTxIdsRequest(chain_id=self.chain_id,
                                         tx_ids=tx_ids)
        res = self._get_client().GetTxsInPoolByTxIds(req)
        return res.txs, res.tx_ids

    def get_tx_status(self, tx_id: str):
        self._debug("begin to get transaction status in txpool: %s" % tx_id)
        req = GetTxStatusRequest(chain_id=self.chain_id, tx_id=tx_id)
        res = self._get_client().GetTxStatus(req)
        return res.tx_status


class CanonicalTxResultMixIn(BaseClient):
    """权威交易结果"""

    def sync_canonical_tx_result(self, tx_id: str) -> Result:
        """
         同步获取权威的公认的交易结果，即超过半数共识的交易
        :param tx_id:
        :return:
        """

    def _canonical_polling_tx_result(self, ctx, pool):
        pass

    def _canonical_get_tx_by_tx_id(self, tx_id):
        # params = {ParamKey.txId.name: tx_id}
        # payload = self._payload_builder.create_query_payload(SystemContractName.CHAIN_QUERY.name,
        #                                                      ChainQueryMethod.GET_TX_BY_TX_ID.name,
        #                                                      params)
        # tx_request = self._generate_tx_request(payload)
        for i in range(self.node_cnt):
            self._node_index = i
            try:
                return self.get_tx_by_tx_id(tx_id)
            except ContractFail:
                pass
