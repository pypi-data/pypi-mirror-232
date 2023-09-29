#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# @FileName     :   archive.py
# @Function     :   ChainMaker 归档接口

import pymysql

from chainmaker.apis.base_client import BaseClient
from chainmaker.keys import ArchiveDB
from chainmaker.keys import ParamKeys
from chainmaker.keys import SystemContractNames, ArchiveManageMethods
from chainmaker.protos.common.block_pb2 import BlockInfo
from chainmaker.protos.common.request_pb2 import Payload
from chainmaker.protos.common.result_pb2 import TxResponse
from chainmaker.protos.store.store_pb2 import BlockWithRWSet
from chainmaker.utils.common import uint64_to_bytes


class ArchiveMixIn(BaseClient):
    
    def create_archive_block_payload(self, target_block_height: int) -> Payload:
        """
        构造数据归档区块Payload
        :param target_block_height: 归档目标区块高度
        :return: 待签名Payload
        """
        self.logger.debug('[SDK] create [ArchiveBlock] to be signed payload')
        params = {ParamKeys.BLOCK_HEIGHT: uint64_to_bytes(target_block_height)}
        return self.payload_builder.create_archive_payload(SystemContractNames.ARCHIVE_MANAGE,
                                                           ArchiveManageMethods.ARCHIVE_BLOCK, params)
    
    def create_restore_block_payload(self, full_block: bytes) -> Payload:
        """
        构造归档数据恢复Payload
        :param full_block: 完整区块数据（对应结构：store.BlockWithRWSet）
        :return: 待签名Payload
        """
        self.logger.debug('[SDK] create [RestoreBlock] to be signed payload')
        params = {ParamKeys.FULL_BLOCK: full_block}
        return self.payload_builder.create_archive_payload(SystemContractNames.ARCHIVE_MANAGE,
                                                           ArchiveManageMethods.RESTORE_BLOCK, params)
    
    def sign_archive_payload(self, payload: Payload) -> Payload:  # do nothing
        return payload
    
    def send_archive_block_request(self, payload: Payload, timeout: int = None)->TxResponse:
        """
        发送归档请求
        :param payload: 归档待签名Payload
        :param timeout: 超时时间
        :return: 交易响应TxResponse
        :raise: 已归档抛出InternalError
        """
        return self.send_request(payload, timeout=timeout)
    
    def send_restore_block_request(self, payload, timeout: int = None):
        return self.send_request(payload, timeout=timeout)
    
    def get_archived_full_block_by_height(self, block_height: int) -> BlockWithRWSet:
        """
        根据区块高度，查询已归档的完整区块（包含合约event info）
        :param block_height: 区块高度
        :return: 区块详情 BlockInfo
        :raises RequestError: 请求失败
        """
        full_block = self.get_from_archive_store(block_height)
        return full_block
    
    def get_archived_block_by_height(self, block_height: int, with_rwset: bool = False) -> BlockInfo:
        """
        根据区块高度，查询已归档的区块
        :param block_height: 区块高度
        :param with_rwset: 是否包含读写集
        :return: 区块详情 BlockInfo
        :raises RequestError: 请求失败
        """
        full_block = self.get_from_archive_store(block_height)
        block_info = BlockInfo(
            block=full_block.block,
        )
        if with_rwset:
            block_info.rwset_list = full_block.TxRWSets
        
        return block_info
    
    def get_archived_block_by_hash(self, block_hash: str, with_rwset: bool = False) -> BlockInfo:
        """
        根据区块hash查询已归档的区块
        :param block_hash: 区块hash
        :param with_rwset: 是否包含读写集
        :return: 区块详情 BlockInfo
        :raises RequestError: 请求失败
        """
        block_height = self.get_block_height_by_hash(block_hash)
        return self.get_archived_block_by_height(block_height, with_rwset)
    
    def get_archived_block_by_tx_id(self, tx_id: str, with_rwset: bool = False) -> BlockInfo:
        """
        根据交易id查询已归档的区块
        :param tx_id: 交易ID
        :param with_rwset: 是否包含读写集
        :return: 区块详情 BlockInfo
        :raises RequestError: 请求失败
        """
        block_height = self.get_block_height_by_tx_id(tx_id)
        return self.get_archived_block_by_height(block_height, with_rwset)
    
    def get_archived_tx_by_tx_id(self, tx_id: str):
        """
        根据交易id查询已归档的交易
        :param tx_id: 交易id
        :return: 交易详情
        :raises RequestError: 请求失败
        """
        block_info = self.get_archived_block_by_tx_id(tx_id)
        for tx in block_info.block.txs:
            if tx.payload.tx_id == tx_id:
                return tx
    
    def get_from_archive_store(self, block_height: int, archive_type: str = None):
        archive_type = archive_type or self.archive_config.type or 'mysql'
        if archive_type.lower() == "mysql":
            return self.get_archived_block_from_mysql(block_height)
        raise NotImplementedError('目前仅支持MySQL数据库')
    
    def get_archived_block_from_mysql(self, block_height: int):
        dest = self.archive_config.dest or ''
        try:
            db_user, db_pwd, db_host, db_port = dest.split(":")
        except ValueError:
            raise ValueError('archive["dest"]格式错误, 应为<db_user>:<db_pwd>:<db_host>:<db_port>格式')
        
        db_name = '%s_%s' % (ArchiveDB.MysqlDBNamePrefix, self.chain_id)
        table_sn = int(block_height / ArchiveDB.RowsPerBlockInfoTable) + 1
        table_name = "%s_%s" % (ArchiveDB.MysqlTableNamePrefix, table_sn)
        query_sql = ArchiveDB.QUERY_FULL_BLOCK_BY_HEIGHT_SQL % (table_name, block_height)
        
        with pymysql.Connection(host=db_host, port=int(db_port), user=db_user, password=db_pwd, db=db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(query_sql)
            block_with_rwset_bytes, hmac = cursor.fetchone()
        
        # TODO 校验 hmac
        block_with_rwset = BlockWithRWSet()
        block_with_rwset.ParseFromString(block_with_rwset_bytes)
        
        return block_with_rwset
