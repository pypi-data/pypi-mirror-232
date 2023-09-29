#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# @FileName     :   test_cert_alias_manage.py
# @Function     :   测试证书别名接口

import allure
import pytest


@allure.feature('证书别名')
class TestCertAlias:
    @allure.story('添加证书别名')
    def test_add_alias(self, cc, random_alias):   # ✅
        if cc.enabled_alias is True:
            pytest.skip("MemberType must be MemberType_CERT")
        cc.user.alias = random_alias
        res = cc.add_alias()    # "add alias failed, MemberType must be MemberType_CERT "
        assert res.contract_result.code in [0, 1]
        if 0 == res.contract_result.code:
            assert res.contract_result.result == b'ok'

    @allure.story('查询证书别名')
    def test_query_cert_alias(self, cc, random_alias):   # ✅
        cc.user.alias = cc.user.alias or random_alias
        if not cc.enabled_alias:
            cc.enable_alias()
        aliases = [cc.alias]
        res = cc.query_cert_alias(aliases)
        assert cc.alias == res.alias_infos[0].alias

    @allure.story('检查证书别名')
    def test_check_alias(self, cc, random_alias):   # ✅
        cc.alias = cc.alias or random_alias
        if not cc.enabled_alias:
            cc.enable_alias()
        result = cc.check_alias()
        assert result is True

    @allure.story('启用证书别名')
    def test_enable_alias(self, cc, random_alias):  # ✅
        cc.alias = cc.alias or random_alias
        # cc.enabled_alias = True
        if not cc.enabled_alias:
            cc.enable_alias()
        assert cc.check_alias() is True

    @allure.story('更新证书别名')
    def test_update_alias(self, cc, random_alias):  # ✅
        new_cert_pem = cc.user.sign_cert_bytes.decode()
        cc.user.alias = cc.user.alias or random_alias
        if not cc.enabled_alias:
            cc.enable_alias()
        payload = cc.create_update_cert_by_alias_payload(cc.alias, new_cert_pem)
        res = cc.send_manage_request(payload)
        assert 0 == res.contract_result.code, res.contract_result
        assert cc.check_alias() is True

    @allure.story('删除证书别名')  # Fixme
    @pytest.mark.skip(reason='待修复')
    def test_delete_alias(self, cc, random_alias):  # Fixme
        cc.alias = cc.alias or random_alias
        if not cc.enabled_alias:
            cc.enable_alias()
        payload = cc.create_delete_cert_alias_payload([cc.alias])
        res = cc.send_manage_request(payload)
        assert 0 == res.contract_result.code, res.contract_result
        assert cc.check_alias() is False
        
