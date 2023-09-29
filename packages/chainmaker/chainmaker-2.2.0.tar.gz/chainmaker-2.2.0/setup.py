#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# @FileName     :   setup.py
# @Function     :   安装配置

from setuptools import setup

setup(
    name='chainmaker',
    version='2.2.0',
    packages=['chainmaker',
              'chainmaker.utils',
              'chainmaker.utils.gm',
              'chainmaker.apis',
              'chainmaker.protos',
              'chainmaker.protos.accesscontrol',
              'chainmaker.protos.api',
              'chainmaker.protos.common',
              'chainmaker.protos.config',
              'chainmaker.protos.consensus',
              'chainmaker.protos.discovery',
              'chainmaker.protos.net',
              'chainmaker.protos.store',
              'chainmaker.protos.sync',
              'chainmaker.protos.syscontract',
              'chainmaker.protos.txpool',
              ],
    url='https://git.chainmaker.org.cn/chainmaker/chainmaker-sdk-python.git',
    license='Apache License',
    author='THL chainmaker developers',
    author_email='operation@chainmaker.org',
    description='ChainMaker Python SDK',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    install_requires=["protobuf", "grpcio", "pyyaml", "cryptography", "pysha3", "pymysql", "eth-abi<=2.6", "asn1"],
    keywords=["chainmaker", "blockchain", "chainmaker-sdk-python", "chainmaker-sdk"],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Software Development :: User Interfaces',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ]
)
