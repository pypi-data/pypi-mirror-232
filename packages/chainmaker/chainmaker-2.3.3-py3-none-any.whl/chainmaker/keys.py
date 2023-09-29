#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# @FileName     :   keys.py
# @Function     :   默认参数及常量
from typing import List, Union


# v2.2.1 修改-兼容Python3.6不支持namedtuple defaults参数
class RechargeGasItem:
    def __init__(self, address: str, amount: int):
        self.address = address
        self.amount = amount


# v2.3.0 修改
class UserConfig:
    org_id: str = None
    user_key_file_path: str = None
    user_crt_file_path: str = None
    user_key_pwd: str = None  # v2.3.0 增加
    user_sign_key_file_path: str = None
    user_sign_crt_file_path: str = None
    user_sign_key_pwd: str = None  # v2.3.0 增加
    user_enc_key_file_path: str = None  # v2.3.0 增加
    user_enc_crt_file_path: str = None  # v2.3.0 增加
    user_enc_key_pwd: str = None  # v2.3.0 增加
    crypto: dict = None
    auth_type: str = None
    alias: str = None
    enable_normal_key: bool = None  # v2.3.0 增加


# v2.3.2 新增
class ArchiveType:
    mysql = "mysql"
    archivecenter = "archivecenter"


class HashType:
    SHA256 = 'SHA256'
    # SHA3 = 'SHA3'
    SHA3_256 = 'SHA3_256'
    SM3 = 'SM3'


# v2.2.1 修改-兼容Python3.6不支持namedtuple defaults参数
class ArchiveConfig:
    def __init__(self, type: Union[ArchiveType, str], dest: str = None, secret_key: str = None):
        self.type = type
        self.dest = dest
        self.secret_key = secret_key


# v2.2.1 修改-兼容Python3.6不支持namedtuple defaults参数
class RPCClientConfig:
    def __init__(self, max_receive_message_size: str = None, max_send_message_size: str = None,
                 send_tx_timeout: int = None, get_tx_timeout: int = None, **kwargs):
        self.max_receive_message_size = max_receive_message_size
        self.max_send_message_size = max_send_message_size
        self.send_tx_timeout = send_tx_timeout  # v2.3.0 增加
        self.get_tx_timeout = get_tx_timeout  # v2.3.0 增加


# v2.2.1 修改-兼容Python3.6不支持namedtuple defaults参数
class PKCS11Config:
    def __init__(self, enabled: bool = None, library: str = None,
                 label: str = None,
                 password: str = None,
                 session_cache_size: int = None,
                 hash: HashType = None, **kwargs):
        self.enabled = enabled
        self.library = library
        self.label = label
        self.password = password
        self.session_cache_size = session_cache_size
        self.hash = hash


# v2.2.1 修改-兼容Python3.6不支持namedtuple defaults参数
class ArchiveCenterConfigTLSConfig:

    def __init__(self, server_name: str, priv_key_file: str, cert_file: str, trust_ca_list: List[str], **kwargs):
        self.server_name = server_name
        self.priv_key_file = priv_key_file
        self.cert_file = cert_file
        self.trust_ca_list = trust_ca_list


# v2.3.2 增加
class ArchiveCenterConfig:
    def __init__(self, chain_genesis_hash: str,
                 archive_center_http_url: str = None,
                 request_second_limit: int = None,
                 rpc_address: str = None,
                 tls_enable: bool = None,
                 tls: dict = None, **kwargs):
        self.chain_genesis_hash = chain_genesis_hash
        self.archive_center_http_url = archive_center_http_url
        self.request_second_limit = request_second_limit
        self.rpc_address = rpc_address
        self.tls_enable = tls_enable
        self.tls = ArchiveCenterConfigTLSConfig(**tls) if isinstance(tls, dict) else None


class AuthType:
    PermissionedWithCert = 'PermissionedWithCert'
    PermissionedWithKey = 'PermissionedWithKey'
    Public = 'Public'


class Defaults:
    SEQ = 0
    TX_ID = ''
    ENDORSE_USERS = []
    PARAMS = None
    LIMIT = None
    NODE_INDEX = 0
    AUTH_TYPE = AuthType.PermissionedWithCert
    HASH_TYPE = HashType.SHA256

    ENABLED_ALIAS = False
    ENABLED_CRT_HASH = False

    REQUEST_TIMEOUT = 3  # 秒
    SUBSCRIBE_TIMEOUT = 60  # 秒
    WITH_SYNC_RESULT = False  # 必须默认为False, 否则像get_chain_info这种也会轮询交易
    WITH_RWSET = False

    TX_CHECK_INTERVAL = 0.5  # 秒
    TX_CHECK_TIMEOUT = 30
    RETRY_LIMIT = 4
    RETRY_INTERVAL = 0.5  # 毫秒

    GRPC_MAX_SEND_MESSAGE_LENGTH = 16
    GRPC_MAX_RECEIVE_MESSAGE_LENGTH = 16

    RPC_GET_TX_TIMEOUT = 60  # v2.3.0 新增 查询请求超时时间
    RPC_SEND_TX_TIMEOUT = 60  # v2.3.0 新增 INVOKE请求超时时间



class Rule:
    ALL = 'ALL'
    ANY = 'ANY'
    MAJORITY = 'MAJORITY'
    SELF = 'SELF'
    FORBIDDEN = 'FORBIDDEN'


class Role:
    consensus = 'consensus'
    common = 'common'
    admin = 'admin'
    client = 'client'
    light = 'light'


class RuntimeType:
    WASMER = 'WASMER'
    WXVM = 'WXVM'
    GASM = 'GASM'
    EVM = 'EVM'
    DOCKER_GO = 'DOCKER_GO'
    DOCKER_JAVA = 'DOCKER_JAVA'


class ContractStatus:
    NORMAL = 0
    FROZEN = 1
    REVOKED = 2


class AddrType:
    CHAINMAKER = 0
    ZXL = 1
    ETHEREUM = 2


class ChainConfigMethods:
    GET_CHAIN_CONFIG = "GET_CHAIN_CONFIG"
    GET_CHAIN_CONFIG_AT = "GET_CHAIN_CONFIG_AT"
    CORE_UPDATE = "CORE_UPDATE"
    BLOCK_UPDATE = "BLOCK_UPDATE"
    TRUST_ROOT_ADD = "TRUST_ROOT_ADD"
    TRUST_ROOT_UPDATE = "TRUST_ROOT_UPDATE"
    TRUST_ROOT_DELETE = "TRUST_ROOT_DELETE"
    NODE_ADDR_ADD = "NODE_ADDR_ADD"
    NODE_ADDR_UPDATE = "NODE_ADDR_UPDATE"
    NODE_ADDR_DELETE = "NODE_ADDR_DELETE"
    NODE_ORG_ADD = "NODE_ORG_ADD"
    NODE_ORG_UPDATE = "NODE_ORG_UPDATE"
    NODE_ORG_DELETE = "NODE_ORG_DELETE"
    CONSENSUS_EXT_ADD = "CONSENSUS_EXT_ADD"
    CONSENSUS_EXT_UPDATE = "CONSENSUS_EXT_UPDATE"
    CONSENSUS_EXT_DELETE = "CONSENSUS_EXT_DELETE"
    PERMISSION_ADD = "PERMISSION_ADD"
    PERMISSION_UPDATE = "PERMISSION_UPDATE"
    PERMISSION_DELETE = "PERMISSION_DELETE"
    NODE_ID_ADD = "NODE_ID_ADD"
    NODE_ID_UPDATE = "NODE_ID_UPDATE"
    NODE_ID_DELETE = "NODE_ID_DELETE"
    TRUST_MEMBER_ADD = "TRUST_MEMBER_ADD"
    TRUST_MEMBER_UPDATE = "TRUST_MEMBER_UPDATE"
    TRUST_MEMBER_DELETE = "TRUST_MEMBER_DELETE"
    ALTER_ADDR_TYPE = "ALTER_ADDR_TYPE"
    ENABLE_OR_DISABLE_GAS = "ENABLE_OR_DISABLE_GAS"
    # v2.3.2 new
    SET_INVOKE_BASE_GAS = 'SET_INVOKE_BASE_GAS'  # set invoke base gas
    SET_ACCOUNT_MANAGER_ADMIN = 'SET_ACCOUNT_MANAGER_ADMIN'  # set account manager admin
    PERMISSION_LIST = 'PERMISSION_LIST'  # list permissions
    UPDATE_VERSION = 'UPDATE_VERSION'  # switch_branch version
    MULTI_SIGN_ENABLE_MANUAL_RUN = 'MULTI_SIGN_ENABLE_MANUAL_RUN'  # update `enable_manual_run` flag of multi sign
    ENABLE_ONLY_CREATOR_UPGRADE = 'ENABLE_ONLY_CREATOR_UPGRADE'   # TODO 新增接口
    DISABLE_ONLY_CREATOR_UPGRADE = 'DISABLE_ONLY_CREATOR_UPGRADE'   # ODO 新增接口
    SET_INVOKE_GAS_PRICE = 'SET_INVOKE_GAS_PRICE'
    SET_INSTALL_BASE_GAS = 'SET_INSTALL_BASE_GAS'
    SET_INSTALL_GAS_PRICE = 'SET_INSTALL_GAS_PRICE'


class ChainQueryMethods:
    GET_BLOCK_BY_TX_ID = "GET_BLOCK_BY_TX_ID"
    GET_TX_BY_TX_ID = "GET_TX_BY_TX_ID"
    GET_BLOCK_BY_HEIGHT = "GET_BLOCK_BY_HEIGHT"
    GET_CHAIN_INFO = "GET_CHAIN_INFO"
    GET_LAST_CONFIG_BLOCK = "GET_LAST_CONFIG_BLOCK"
    GET_BLOCK_BY_HASH = "GET_BLOCK_BY_HASH"
    GET_NODE_CHAIN_LIST = "GET_NODE_CHAIN_LIST"
    GET_GOVERNANCE_CONTRACT = "GET_GOVERNANCE_CONTRACT"
    GET_BLOCK_WITH_TXRWSETS_BY_HEIGHT = "GET_BLOCK_WITH_TXRWSETS_BY_HEIGHT"
    GET_BLOCK_WITH_TXRWSETS_BY_HASH = "GET_BLOCK_WITH_TXRWSETS_BY_HASH"
    GET_LAST_BLOCK = "GET_LAST_BLOCK"
    GET_FULL_BLOCK_BY_HEIGHT = "GET_FULL_BLOCK_BY_HEIGHT"
    GET_BLOCK_HEIGHT_BY_TX_ID = "GET_BLOCK_HEIGHT_BY_TX_ID"
    GET_BLOCK_HEIGHT_BY_HASH = "GET_BLOCK_HEIGHT_BY_HASH"
    GET_BLOCK_HEADER_BY_HEIGHT = "GET_BLOCK_HEADER_BY_HEIGHT"
    GET_ARCHIVED_BLOCK_HEIGHT = "GET_ARCHIVED_BLOCK_HEIGHT"
    GET_ALL_CONTRACTS = "GET_ALL_CONTRACTS"
    GET_MERKLE_PATH_BY_TX_ID = "GET_MERKLE_PATH_BY_TX_ID"
    # v2.3.2 new
    GET_ARCHIVE_STATUS = "GET_ARCHIVE_STATUS"


class CertManageMethods:
    CERT_ADD = "CERT_ADD"
    CERTS_DELETE = "CERTS_DELETE"
    CERTS_QUERY = "CERTS_QUERY"
    CERTS_FREEZE = "CERTS_FREEZE"
    CERTS_UNFREEZE = "CERTS_UNFREEZE"
    CERTS_REVOKE = "CERTS_REVOKE"
    CERT_ALIAS_ADD = "CERT_ALIAS_ADD"
    CERT_ALIAS_UPDATE = "CERT_ALIAS_UPDATE"
    CERTS_ALIAS_DELETE = "CERTS_ALIAS_DELETE"
    CERTS_ALIAS_QUERY = "CERTS_ALIAS_QUERY"


class GovernanceMethods:
    pass


class MultiSignMethods:
    REQ = "REQ"
    VOTE = "VOTE"
    QUERY = "QUERY"
    TRIG = "TRIG"


class ContractManageMethods:
    INIT_CONTRACT = "INIT_CONTRACT"
    UPGRADE_CONTRACT = "UPGRADE_CONTRACT"
    FREEZE_CONTRACT = "FREEZE_CONTRACT"
    UNFREEZE_CONTRACT = "UNFREEZE_CONTRACT"
    REVOKE_CONTRACT = "REVOKE_CONTRACT"
    GRANT_CONTRACT_ACCESS = "GRANT_CONTRACT_ACCESS"
    REVOKE_CONTRACT_ACCESS = "REVOKE_CONTRACT_ACCESS"
    VERIFY_CONTRACT_ACCESS = "VERIFY_CONTRACT_ACCESS"
    INIT_NEW_NATIVE_CONTRACT = "INIT_NEW_NATIVE_CONTRACT"

    # ContractQuery
    GET_CONTRACT_INFO = "GET_CONTRACT_INFO"
    GET_CONTRACT_BYTECODE = "GET_CONTRACT_BYTECODE"
    GET_CONTRACT_LIST = "GET_CONTRACT_LIST"
    GET_DISABLED_CONTRACT_LIST = "GET_DISABLED_CONTRACT_LIST"


class PrivateComputeMethods:
    GET_CONTRACT = "GET_CONTRACT"
    GET_DATA = "GET_DATA"
    SAVE_CA_CERT = "SAVE_CA_CERT"
    SAVE_DIR = "SAVE_DIR"
    SAVE_DATA = "SAVE_DATA"
    SAVE_ENCLAVE_REPORT = "SAVE_ENCLAVE_REPORT"
    GET_ENCLAVE_PROOF = "GET_ENCLAVE_PROOF"
    GET_CA_CERT = "GET_CA_CERT"
    GET_DIR = "GET_DIR"
    CHECK_CALLER_CERT_AUTH = "CHECK_CALLER_CERT_AUTH"
    GET_ENCLAVE_VERIFICATION_PUB_KEY = "GET_ENCLAVE_VERIFICATION_PUB_KEY"
    GET_ENCLAVE_REPORT = "GET_ENCLAVE_REPORT"
    GET_ENCLAVE_CHALLENGE = "GET_ENCLAVE_CHALLENGE"
    GET_ENCLAVE_SIGNATURE = "GET_ENCLAVE_SIGNATURE"
    SAVE_REMOTE_ATTESTATION = "SAVE_REMOTE_ATTESTATION"


class DposErc20Methods:
    GET_OWNER = "GET_OWNER"
    GET_DECIMALS = "GET_DECIMALS"
    TRANSFER = "TRANSFER"
    TRANSFER_FROM = "TRANSFER_FROM"
    GET_BALANCEOF = "GET_BALANCEOF"
    APPROVE = "APPROVE"
    GET_ALLOWANCE = "GET_ALLOWANCE"
    BURN = "BURN"
    MINT = "MINT"
    TRANSFER_OWNERSHIP = "TRANSFER_OWNERSHIP"
    GET_TOTAL_SUPPLY = "GET_TOTAL_SUPPLY"


class DposStakeMethods:
    GET_ALL_CANDIDATES = "GET_ALL_CANDIDATES"
    GET_VALIDATOR_BY_ADDRESS = "GET_VALIDATOR_BY_ADDRESS"
    DELEGATE = "DELEGATE"
    GET_DELEGATIONS_BY_ADDRESS = "GET_DELEGATIONS_BY_ADDRESS"
    GET_USER_DELEGATION_BY_VALIDATOR = "GET_USER_DELEGATION_BY_VALIDATOR"
    UNDELEGATE = "UNDELEGATE"
    READ_EPOCH_BY_ID = "READ_EPOCH_BY_ID"
    READ_LATEST_EPOCH = "READ_LATEST_EPOCH"
    SET_NODE_ID = "SET_NODE_ID"
    GET_NODE_ID = "GET_NODE_ID"
    UPDATE_MIN_SELF_DELEGATION = "UPDATE_MIN_SELF_DELEGATION"
    READ_MIN_SELF_DELEGATION = "READ_MIN_SELF_DELEGATION"
    UPDATE_EPOCH_VALIDATOR_NUMBER = "UPDATE_EPOCH_VALIDATOR_NUMBER"
    READ_EPOCH_VALIDATOR_NUMBER = "READ_EPOCH_VALIDATOR_NUMBER"
    UPDATE_EPOCH_BLOCK_NUMBER = "UPDATE_EPOCH_BLOCK_NUMBER"
    READ_EPOCH_BLOCK_NUMBER = "READ_EPOCH_BLOCK_NUMBER"
    READ_COMPLETE_UNBOUNDING_EPOCH_NUMBER = "READ_COMPLETE_UNBOUNDING_EPOCH_NUMBER"
    READ_SYSTEM_CONTRACT_ADDR = "READ_SYSTEM_CONTRACT_ADDR"


class SubscribeManageMethods:
    SUBSCRIBE_BLOCK = "SUBSCRIBE_BLOCK"
    SUBSCRIBE_TX = "SUBSCRIBE_TX"
    SUBSCRIBE_CONTRACT_EVENT = "SUBSCRIBE_CONTRACT_EVENT"


class ArchiveManageMethods:
    ARCHIVE_BLOCK = "ARCHIVE_BLOCK"
    RESTORE_BLOCK = "RESTORE_BLOCK"


class CrossTransactionMethods:
    COMMIT = "COMMIT"
    ROLLBACK = "ROLLBACK"
    READ_STATE = "READ_STATE"
    SAVE_PROOF = "SAVE_PROOF"
    READ_PROOF = "READ_PROOF"
    ARBITRATE = "ARBITRATE"


class PubkeyManageMethods:
    PUBKEY_ADD = "PUBKEY_ADD"
    PUBKEY_DELETE = "PUBKEY_DELETE"
    PUBKEY_QUERY = "PUBKEY_QUERY"


class AccountManagerMethods:
    SET_ADMIN = "SET_ADMIN"
    GET_ADMIN = "GET_ADMIN"
    RECHARGE_GAS = "RECHARGE_GAS"
    GET_BALANCE = "GET_BALANCE"
    CHARGE_GAS = "CHARGE_GAS"
    FROZEN_ACCOUNT = "FROZEN_ACCOUNT"
    UNFROZEN_ACCOUNT = "UNFROZEN_ACCOUNT"
    ACCOUNT_STATUS = "ACCOUNT_STATUS"
    REFUND_GAS = "REFUND_GAS"
    REFUND_GAS_VM = "REFUND_GAS_VM"
    # new TODO 新增接口
    CHARGE_GAS_FOR_MULTI_ACCOUNT = "CHARGE_GAS_FOR_MULTI_ACCOUNT"

# v2.3.2 新增
class TransactionManagerMethods:
    ADD_BLACKLIST_TX_IDS = 'ADD_BLACKLIST_TX_IDS'
    DELETE_BLACKLIST_TX_IDS = 'DELETE_BLACKLIST_TX_IDS'
    GET_BLACKLIST_TX_IDS = 'GET_BLACKLIST_TX_IDS'


class TMethods:
    P = "P"
    G = "G"
    N = "N"
    D = "D"


class SystemContractNames:
    CHAIN_CONFIG = 'CHAIN_CONFIG'
    CHAIN_QUERY = 'CHAIN_QUERY'
    CERT_MANAGE = 'CERT_MANAGE'
    GOVERNANCE = 'GOVERNANCE'
    MULTI_SIGN = 'MULTI_SIGN'
    CONTRACT_MANAGE = 'CONTRACT_MANAGE'
    PRIVATE_COMPUTE = 'PRIVATE_COMPUTE'
    DPOS_ERC20 = 'DPOS_ERC20'
    DPOS_STAKE = 'DPOS_STAKE'
    SUBSCRIBE_MANAGE = 'SUBSCRIBE_MANAGE'
    ARCHIVE_MANAGE = 'ARCHIVE_MANAGE'
    CROSS_TRANSACTION = 'CROSS_TRANSACTION'
    PUBKEY_MANAGE = 'PUBKEY_MANAGE'
    ACCOUNT_MANAGER = 'ACCOUNT_MANAGER'
    TRANSACTION_MANAGER = 'TRANSACTION_MANAGER' # v2.3.2新增
    T = 'T'


class ParamKeys:
    block_height = 'block_height'
    org_id = 'org_id'
    root = 'root'
    node_id = 'node_id'
    new_node_id = 'new_node_id'
    node_ids = 'node_ids'
    member_info = 'member_info'
    role = 'role'
    tx_scheduler_timeout = 'tx_scheduler_timeout'
    tx_scheduler_validate_timeout = 'tx_scheduler_validate_timeout'
    tx_timestamp_verify = 'tx_timestamp_verify'
    tx_timeout = 'tx_timeout'
    block_tx_capacity = 'block_tx_capacity'
    block_size = 'block_size'
    block_interval = 'block_interval'
    tx_parameter_size = 'tx_parameter_size'
    addr_type = 'addr_type'
    block_version = 'block_version'

    NATIVE_CONTRACT_NAME = 'NATIVE_CONTRACT_NAME'
    CONTRACT_NAME = 'CONTRACT_NAME'
    txId = 'txId'
    blockHeight = 'blockHeight'
    blockHash = 'blockHash'
    withRWSet = 'withRWSet'
    START_BLOCK = 'START_BLOCK'
    END_BLOCK = 'END_BLOCK'
    WITH_RWSET = 'WITH_RWSET'
    ONLY_HEADER = 'ONLY_HEADER'
    TX_IDS = 'TX_IDS'
    TOPIC = 'TOPIC'
    VOTE_INFO = 'VOTE_INFO'
    TX_ID = 'TX_ID'
    SYS_CONTRACT_NAME = 'SYS_CONTRACT_NAME'
    SYS_METHOD = 'SYS_METHOD'
    CONTRACT_VERSION = 'CONTRACT_VERSION'
    CONTRACT_BYTECODE = 'CONTRACT_BYTECODE'
    CONTRACT_RUNTIME_TYPE = 'CONTRACT_RUNTIME_TYPE'
    BLOCK_HEIGHT = 'BLOCK_HEIGHT'
    FULL_BLOCK = 'FULL_BLOCK'

    batch_recharge = 'batch_recharge'
    address_key = 'address_key'
    charge_gas_amount = 'charge_gas_amount'

    # dpos erc20
    to = 'to'
    _from = 'from'
    value = 'value'
    address = 'address'
    min_self_delegation = 'min_self_delegation'
    epoch_validator_number = 'epoch_validator_number'
    epoch_block_number = 'epoch_block_number'
    owner = 'owner'

    # 隐私计算
    contract_name = 'contract_name'
    code_hash = 'code_hash'
    key = 'key'
    order_id = 'order_id'
    private_dir = 'private_dir'
    enclave_id = 'enclave_id'
    payload = 'payload'
    order_ids = 'order_ids'
    sign_pairs = 'sign_pairs'
    report = 'report'
    ca_cert = 'ca_cert'
    version = 'version'
    code_header = 'code_header'
    is_deploy = 'is_deploy'
    rw_set = 'rw_set'
    events = 'events'
    report_hash = 'report_hash'
    result = 'result'
    sign = 'sign'
    proof = 'proof'

    enable_optimize_charge_gas = 'enable_optimize_charge_gas'  # v2.2.2 新增

    multi_sign_enable_manual_run = 'multi_sign_enable_manual_run'  # v2.3.1 新增

    set_invoke_base_gas = 'set_invoke_base_gas'  # v2.3.2 新增
    set_install_base_gas = 'set_install_base_gas'  # v2.3.2 新增
    set_invoke_gas_price = 'set_invoke_gas_price'  # v2.3.2 新增
    set_install_gas_price = 'set_install_gas_price'  # v2.3.2 新增


class VoteStatus:
    AGREE = 'AGREE'
    REJECT = 'REJECT'


class ArchiveDB:
    MysqlDBNamePrefix = "cm_archived_chain"
    MysqlTableNamePrefix = "t_block_info"
    RowsPerBlockInfoTable = 10000  # v2.3.2 修改
    QUERY_FULL_BLOCK_BY_HEIGHT_SQL = 'SELECT Fblock_with_rwset, Fhmac from %s WHERE Fblock_height=%s'
    MysqlSysInfoTable = 'sysinfo'  # v2.3.2 新增
    MysqlTableCharset = 'utf8mb4'  # v2.3.2 新增
    MySqlTableCollate = 'utf8mb4_unicode_ci'  # v2.3.2 新增
