#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# @FileName     :   setup.py
# @Function     :   安装配置

from setuptools import find_packages, setup

__version__ = '3.0.2'

INSTALL_REQUIRES = [
    "protobuf==4.22.1",
    "grpcio",
    "pyyaml",
    "cryptography",
    "pysha3",
    "pymysql",
    "eth-abi>2.6",
    "pyasn1",
    "requests",
]

TEST_REQUIRES = [
    'pytest>=3.3.1',
    'pytest-timeout'
]

setup(
    name='chainmaker',
    version=__version__,
    description='ChainMaker Python SDK',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author='THL chainmaker developers',
    author_email='operation@chainmaker.org',
    license='Apache License',
    url='https://git.chainmaker.org.cn/chainmaker/chainmaker-sdk-python.git',
    include_package_data=True,
    packages=find_packages(include=['chainmaker']),
    zip_safe=True,
    install_requires=INSTALL_REQUIRES,
    tests_require=TEST_REQUIRES,
    keywords=["chainmaker", "blockchain", "chainmaker-sdk-python", "chainmaker-sdk"],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Software Development :: User Interfaces',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ]
)
