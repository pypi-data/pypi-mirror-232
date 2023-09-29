#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# @FileName     :   node.py
# @Function     :   ChainMaker客户端连接节点
from typing import Union, List

from chainmaker.utils import crypto_utils


class Node(object):
    def __init__(self, node_addr: str, conn_cnt: int = 1, enable_tls: bool = False,
                 trust_cas: Union[bytes, List[bytes]] = None, tls_host_name=None):
        """
        客户端连接节点
        :param node_addr: 节点RPC地址，eg 127.0.0.1:12301
        :param conn_cnt: 创建连接数量，默认为1
        :param enable_tls: 是否启用tls
        :param trust_cas: trust_root_paths ca证书二进制内容列表，或ca证书二进制列表连接成的byte字符串
        :param tls_host_name: tls服务器名称
        """
        self.addr = node_addr
        self.conn_cnt = conn_cnt or 1
        self.enable_tls = enable_tls
        self.tls_host_name = tls_host_name
        
        if isinstance(trust_cas, list):
            self.trusted_cas = b''.join(trust_cas)
        elif isinstance(trust_cas, bytes):
            self.trusted_cas = trust_cas
        else:
            raise TypeError('trust_cas仅支持bytes和List[bytes]格式')
    
    def __repr__(self):
        return f'<Node {self.addr}>'
    
    def __eq__(self, other):
        if hasattr(other, 'addr'):
            return self.addr == other.addr
        return False
    
    @classmethod
    def from_conf(cls, node_addr, conn_cnt=None, enable_tls=False, trust_root_paths=None, tls_host_name=None):
        trusted_cas = crypto_utils.merge_cert_pems(trust_root_paths) if trust_root_paths else b''
        return cls(node_addr, conn_cnt, enable_tls, trusted_cas, tls_host_name)
