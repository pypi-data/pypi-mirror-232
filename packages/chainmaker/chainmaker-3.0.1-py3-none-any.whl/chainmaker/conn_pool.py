#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# @FileName     :   conn_pool.py
# @Function     :   ChainMaker 链接池
import logging
import random
from typing import List

# noinspection PyPackageRequirements
import grpc

from chainmaker.keys import Defaults, RPCClientConfig
from chainmaker.node import Node
from chainmaker.protos.api.rpc_node_pb2_grpc import RpcNodeStub

logger = logging.getLogger(__name__)

DEFAULT_RPC_CLIENT_CONFIG = RPCClientConfig(Defaults.GRPC_MAX_SEND_MESSAGE_LENGTH,
                                            Defaults.GRPC_MAX_RECEIVE_MESSAGE_LENGTH)


class ConnectionPool:
    def __init__(self, user, nodes: List[Node], rpc_client_config=None):
        self.user = user
        self.nodes = nodes
        self.rpc_client_config = rpc_client_config or DEFAULT_RPC_CLIENT_CONFIG
        self.node_cnt = len(nodes)
        self.pool = self.init_channels()  # 结构为二位列表 [[channel1, channel2],[channel3, channel4]]
        self._node = None  # 当前连接节点

    def init_channels(self):
        return [[self.get_channel(node) for _ in range(node.conn_cnt)] for node in self.nodes]

    def get_channel(self, node: Node) -> grpc.Channel:
        """
        根据节点获取连接
        :param node: 连接节点
        :return: Node桩
        """
        max_send_message_size = (self.rpc_client_config.max_send_message_size
                                 or Defaults.GRPC_MAX_SEND_MESSAGE_LENGTH)
        max_receive_message_size = (self.rpc_client_config.max_receive_message_size
                                    or Defaults.GRPC_MAX_RECEIVE_MESSAGE_LENGTH)
        opts = [
            ('grpc.max_send_message_length', max_send_message_size * 1024 * 1024),
            ('grpc.max_receive_message_length', max_receive_message_size * 1024 * 1024)]

        if node.enable_tls:
            # 创建 双向tls 的 secure channel
            # credential = grpc.metadata_call_credentials()
            credential = grpc.ssl_channel_credentials(root_certificates=node.trusted_cas,
                                                      private_key=self.user.tls_key_bytes,
                                                      certificate_chain=self.user.tls_cert_bytes)

            # 如果启用了tls_host_name, 则以tls_host_name来验证tls连接。
            if node.tls_host_name:
                opts.append(('grpc.ssl_target_name_override', node.tls_host_name))
            channel = grpc.secure_channel(node.addr, credential, options=opts)
        else:
            # 创建 insecure channel
            channel = grpc.insecure_channel(node.addr, options=opts)
        return channel

    def get_random_channel(self) -> (Node, grpc.Channel):
        node_index = random.randint(0, len(self.nodes)-1)
        return self.nodes[node_index], random.choice(self.pool[node_index])

    def get_node_random_channel(self, node_index: int)->(Node, grpc.Channel):
        if not 0 < node_index < len(self.pool):
            raise ValueError('node_index 应大于0并小于节点长度')
        return self.nodes[node_index], random.choice(self.pool[node_index])

    @property
    def node(self) -> Node:
        """当前连接节点"""
        return self._node

    def get_client(self, node_index: int = None) -> RpcNodeStub:
        """
        根据策略或去连接
        :param node_index: 节点索引
        :return:
        """
        if node_index is None:
            self._node, channel = self.get_random_channel()
        else:
            self._node, channel = self.get_node_random_channel(node_index)
        return RpcNodeStub(channel)

    def close(self):
        [channel.close() for channels in self.pool for channel in channels]
