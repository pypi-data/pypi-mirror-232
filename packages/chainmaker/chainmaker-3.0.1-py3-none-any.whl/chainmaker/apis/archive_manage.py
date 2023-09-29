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
from chainmaker.keys import (ArchiveDB, ParamKey, SystemContractName, ArchiveManageMethod)
from chainmaker.protos import (BlockInfo, Payload, TxResponse, BlockWithRWSet)
from chainmaker.utils.common import uint64_to_bytes


class ArchiveMixIn(BaseClient):
    # 10-00 创建数据归档区块待签名Payload
    def create_archive_block_payload(self, target_block_height: int) -> Payload:
        """
        创建数据归档区块待签名Payload
        :param target_block_height: 归档目标区块高度
        :return: 待签名Payload
        """
        self._debug('create [ARCHIVE_MANAGE-ARCHIVE_BLOCK] to be signed payload')
        params = {ParamKey.BLOCK_HEIGHT.name: uint64_to_bytes(target_block_height)}
        return self._payload_builder.create_archive_payload(SystemContractName.ARCHIVE_MANAGE.name,
                                                            ArchiveManageMethod.ARCHIVE_BLOCK.name, params)

    # 10-01 创建归档数据恢复待签名Payload
    def create_restore_block_payload(self, full_block: bytes) -> Payload:
        """
        创建归档数据恢复待签名Payload
        :param full_block: 完整区块数据（对应结构：store.BlockWithRWSet）
        :return: 待签名Payload
        """
        self._debug('create [ARCHIVE_MANAGE-RESTORE_BLOCK] to be signed payload')
        params = {ParamKey.FULL_BLOCK.name: full_block}
        return self._payload_builder.create_archive_payload(SystemContractName.ARCHIVE_MANAGE.name,
                                                            ArchiveManageMethod.RESTORE_BLOCK.name, params)

    def sign_archive_payload(self, payload_bytes: bytes) -> Payload:
        """
        签名归档请求
        :param payload_bytes: Payload二进制数据
        :return: 签名后的Payload
        """
        return self.user.sign(payload_bytes)

    def send_archive_block_request(self, payload: Payload, timeout: int = None) -> TxResponse:
        """
        发送归档请求
        :param payload: 归档待签名Payload
        :param timeout: 超时时间
        :return: 交易响应TxResponse
        :raise: 已归档抛出InternalError
        """
        return self.send_request(payload, timeout=timeout)

    def send_restore_block_request(self, payload, timeout: int = None) -> TxResponse:
        """
        发送恢复归档区块请求
        :param payload: 归档请求待签名Payload
        :param timeout: RPC请求超时事件
        :return: 交易响应信息
        """
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
        archive_type = archive_type or self._archive_config.type or 'mysql'
        if archive_type.lower() == "mysql":
            return self.get_archived_block_from_mysql(block_height)
        raise NotImplementedError('[Sdk] 目前仅支持MySQL数据库')

    def get_archived_block_from_mysql(self, block_height: int):
        dest = self._archive_config.dest or ''
        try:
            db_user, db_pwd, db_host, db_port = dest.split(":")
        except ValueError:
            raise ValueError('[Sdk] archive["dest"]格式错误, 应为<db_user>:<db_pwd>:<db_host>:<db_port>格式')

        db_name = '%s_%s' % (ArchiveDB.MysqlDBNamePrefix, self.chain_id)
        table_sn = int(block_height / ArchiveDB.RowsPerBlockInfoTable.value) + 1
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


class ArchiveWithEndorsers(BaseClient):
    def archive_block(self, target_block_height: int, timeout: int = None) -> TxResponse:
        """
        归档区块
        :param target_block_height: 目标区块高度
        :param timeout: RPC请求超时时间
        :return: 请求响应
        """
        payload = self.create_archive_block_payload(target_block_height)
        return self.send_archive_block_request(payload, timeout=timeout)

    # 10-01 恢复区块
    def restore_block(self, full_block: bytes, timeout: int = None) -> TxResponse:
        """
        恢复区块
        :param full_block: 完整区块数据
        :param timeout: RPC请求超时时间
        :return: 请求响应
        """
        payload = self.create_restore_block_payload(full_block)
        return self.send_archive_block_request(payload, timeout=timeout)

