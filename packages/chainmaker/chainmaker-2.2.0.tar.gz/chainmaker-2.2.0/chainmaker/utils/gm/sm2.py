#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# @FileName     :   sm2.py
# @Function     :   SM2算法实现
"""
签名者用户A的密钥对包括其私钥dA和公钥PA=[dA]G= (xA,yA)
签名者用户A具有长度为entlenA比特的可辨别标识IDA，
ENTLA是由整数entlenA转换而成的两个字节
ZA=H256(ENTLA || IDA || a || b || xG || yG|| xA || yA)。
待签名的消息为M，
数字签名(r,s)
"""

import binascii

import asn1

from chainmaker.utils.gm import ec, sm3, func

# 默认用户A id
CRYPTO_DEFAULT_UID = b'1234567812345678'

int2hex = lambda num: hex(num)[2:] if len(hex(num)) % 2 == 0 else '0' + hex(num)[2:]
hex2int = lambda hex_str: int(hex_str, 16)

bytes2list = lambda msg: [i for i in msg]  # bytes转列表List[int]

get_mask = lambda para_len: int('8' + '0' * (para_len - 1), 16)

H256 = lambda *args: bytes.fromhex(''.join(args))  # 拼接所有16进制字符串 并转为 二进制


class SM2P256Curve(ec.Curve):
    name = 'sm2'
    key_size = 256  # 素数域256 位椭圆曲线
    
    gx = '32c4ae2c1f1981195f9904466a39c9948fe30bbff2660be1715a4589334c74c7'  # 基点 Gx, 16进制字符串
    gy = 'bc3736a2f4f6779c59bdcee36b692153d0a9877cc62a474002df32e52139f0a0'  # 基点 Gy, 16进制字符串
    n = 'fffffffeffffffffffffffffffffffff7203df6b21c6052b53bbf40939d54123'  # 如果椭圆曲线上一点P，存在最小的正整数n使得数乘nP=O∞ ,则将n称为P的阶若n不存在，则P是无限阶的
    a = 'fffffffeffffffffffffffffffffffffffffffff00000000fffffffffffffffc'  # 曲线方程 y^2= x^3+ax+b 的系数a, 16进制字符串
    b = '28e9fa9e9d9f5e344d5a9e4bcf6509a7f39789f515ab8f92ddbcbd414d940e93'  # 曲线方程 y^2= x^3+ax+b 的系数a, 16进制字符串
    p = 'fffffffeffffffffffffffffffffffffffffffff00000000ffffffffffffffff'  # 大于3的一个大素数
    
    @property
    def para_len(self):
        return len(self.n)
    
    def scalar_mul(self, k: str, Point: str):
        """kP运算 向量乘"""
        Point = '%s%s' % (Point, '1')
        mask_str = '8'
        for i in range(self.para_len - 1):
            mask_str += '0'
        mask = int(mask_str, 16)
        Temp = Point
        flag = False
        for n in range(self.para_len * 4):
            if (flag):
                Temp = self.double(Temp)
            if (k & mask) != 0:
                if (flag):
                    Temp = self.add(Temp, Point)
                else:
                    flag = True
                    Temp = Point
            k = k << 1
        return self._convert_jacb_to_nor(Temp)
    
    def scalar_base_mul(self, k: str) -> str:
        """基点 向量乘"""
        Point = ''.join([self.gx, self.gy])
        return self.scalar_mul(k, Point)
    
    def double(self, Point: str) -> str:
        """
        倍点
        :param Point:
        :return:
        """
        
        l = len(Point)
        len_2 = 2 * self.para_len
        if l < self.para_len * 2:
            return None
        else:
            x1 = int(Point[0:self.para_len], 16)
            y1 = int(Point[self.para_len:len_2], 16)
            if l == len_2:
                z1 = 1
            else:
                z1 = int(Point[len_2:], 16)
            
            p = int(self.p, 16)
            
            a3 = int(self.a, base=16) + 3 % p
            
            T6 = (z1 * z1) % p
            T2 = (y1 * y1) % p
            T3 = (x1 + T6) % p
            T4 = (x1 - T6) % p
            T1 = (T3 * T4) % p
            T3 = (y1 * z1) % p
            T4 = (T2 * 8) % p
            T5 = (x1 * T4) % p
            T1 = (T1 * 3) % p
            T6 = (T6 * T6) % p
            T6 = (a3 * T6) % p
            T1 = (T1 + T6) % p
            z3 = (T3 + T3) % p
            T3 = (T1 * T1) % p
            T2 = (T2 * T4) % p
            x3 = (T3 - T5) % p
            
            if (T5 % 2) == 1:
                T4 = (T5 + ((T5 + p) >> 1) - T3) % p
            else:
                T4 = (T5 + (T5 >> 1) - T3) % p
            
            T1 = (T1 * T4) % p
            y3 = (T1 - T2) % p
            
            form = '%%0%dx' % self.para_len
            form = form * 3
            return form % (x3, y3, z3)
    
    def add(self, P1: str, P2: str):
        """
        点加函数，P2点为仿射坐标即z=1，P1为Jacobian加重射影坐标
        :param P1:
        :param P2:
        :return:
        """
        
        len_2 = 2 * self.para_len  # 128
        l1 = len(P1)
        l2 = len(P2)
        if (l1 < len_2) or (l2 < len_2):
            return None
        else:
            X1 = int(P1[0:self.para_len], 16)
            Y1 = int(P1[self.para_len:len_2], 16)
            if (l1 == len_2):
                Z1 = 1
            else:
                Z1 = int(P1[len_2:], 16)
            
            x2 = int(P2[0:self.para_len], 16)  #
            y2 = int(P2[self.para_len:len_2], 16)
            p = int(self.p, 16)
            
            T1 = (Z1 * Z1) % p
            T2 = (y2 * Z1) % p
            T3 = (x2 * T1) % p
            
            T1 = (T1 * T2) % p  # Z1 * Z1 * T2
            T2 = (T3 - X1) % p  # x2 * T1 - X1
            T3 = (T3 + X1) % p  # x2 * T1 + X1
            T4 = (T2 * T2) % p  # (y2 * Z1) * (y2 * Z1)
            
            T1 = (T1 - Y1) % p  # Z1 * Z1 * T2 - Y1
            Z3 = (Z1 * T2) % p  # Z1 * (x2 * T1 - X1)
            T2 = (T2 * T4) % p  # (x2 * T1 - X1) * (y2 * Z1) * (y2 * Z1)
            T3 = (T3 * T4) % p  # Z1 * (x2 * T1 - X1) * (y2 * Z1) * (y2 * Z1)
            T5 = (T1 * T1) % p  # (Z1 * Z1 * T2 - Y1) * (Z1 * Z1 * T2 - Y1)
            T4 = (X1 * T4) % p  # X1 * (y2 * Z1) * (y2 * Z1)
            X3 = (
                         T5 - T3) % p  # (Z1 * Z1 * T2 - Y1) * (Z1 * Z1 * T2 - Y1) - Z1 * (x2 * T1 - X1) * (y2 * Z1) * (y2 * Z1)
            T2 = (Y1 * T2) % p  # Y1 * (x2 * T1 - X1) * (y2 * Z1) * (y2 * Z1)
            T3 = (T4 - X3) % p  # X1 * (y2 * Z1) * (y2 * Z1) - Z1 * (x2 * T1 - X1) * (y2 * Z1) * (y2 * Z1)
            T1 = (T1 * T3) % p  # (Z1 * Z1 * T2 - Y1) * Z1 * (x2 * T1 - X1) * (y2 * Z1) * (y2 * Z1)
            Y3 = (
                         T1 - T2) % p  # (Z1 * Z1 * T2 - Y1) * Z1 * (x2 * T1 - X1) * (y2 * Z1) * (y2 * Z1) - Y1 * (x2 * T1 - X1) * (y2 * Z1) * (y2 * Z1)
            
            form = '%%0%dx' % self.para_len
            form = form * 3  # '%063x%063x%063x'
            return form % (X3, Y3, Z3)
    
    def _convert_jacb_to_nor(self, Point):  # Jacobian加重射影坐标转换成仿射坐标
        len_2 = 2 * self.para_len
        x = int(Point[0:self.para_len], 16)
        y = int(Point[self.para_len:len_2], 16)
        z = int(Point[len_2:], 16)
        p = int(self.p, 16)
        z_inv = pow(
            z, p - 2, p)
        z_invSquar = (z_inv * z_inv) % p
        z_invQube = (z_invSquar * z_inv) % p
        x_new = (x * z_invSquar) % p
        y_new = (y * z_invQube) % p
        z_new = (z * z_inv) % p
        if z_new == 1:
            form = '%%0%dx' % self.para_len
            form = form * 2
            return form % (x_new, y_new)
        else:
            return None


sm2p256curve = SM2P256Curve()


class Signature:
    """sm2签名对象"""
    r: int
    s: int
    
    def __init__(self, r: int, s: int):
        self.r = r
        self.s = s
    
    def __str__(self):
        return '%064x%064x' % (self.r, self.s)
    
    def __repr__(self):
        return '<sm2.Signature r="%d" s="%d">' % (self.r, self.s)
    
    @classmethod
    def asn1_load(cls, data: bytes):
        """加载asn1序列化内容构造签名对象"""
        
        dec = asn1.Decoder()
        dec.start(data)
        tag = dec.peek()
        assert tag == (asn1.Numbers.Sequence, asn1.Types.Constructed, asn1.Classes.Universal)
        dec.enter()
        r_tag, r = dec.read()
        s_tag, s = dec.read()
        return cls(r, s)
    
    def asn1_dump(self) -> bytes:
        """按asn1序列化成二进制"""
        enc = asn1.Encoder()
        enc.start()
        enc.enter(asn1.Numbers.Sequence)
        enc.write(self.r)
        enc.write(self.s)
        enc.leave()
        res = enc.output()
        return res


class PublicKey:  # TODO ec.Point
    """
    公钥 公钥是在椭圆曲线上的一个点，由一对坐标（x，y）组成
    公钥字符串可由 x || y 即 x 拼接 y代表
    """
    curve: SM2P256Curve
    x: str  # 公钥X坐标, 16进制字符串
    y: str  # 公钥Y坐标, 16进制字符串
    
    def __init__(self, x: str, y: str, curve: SM2P256Curve = sm2p256curve):
        self.curve = curve
        assert curve.is_on_curve(x=hex2int(x), y=hex2int(y)), '公钥点x,y不在曲线上'
        
        self.x = x
        self.y = y
    
    @staticmethod
    def _calc_ENTLA(uid: bytes) -> str:  # 对勾 ✅
        """
        计算ENTLA, 16进制字符串
        :param uid: uid: 用户A bytes类型的id, 默认为 b'1234567812345678'
        :return: 返回16进制字符串，默认结果为 '0080'
        """
        entla = 8 * len(uid)  # 128
        # 128 >> 8 128(二进制)右移8位, 相当于128 除以 2的8次方, 即 128 // 2 ** 8
        # (整数).to_bytes(1, byteorder='big').hex() 将int转为16进制字符串, 相当于 str(hex(整数))[2:]
        entla1 = (entla >> 8 & 255).to_bytes(1, byteorder='big').hex()
        entla2 = (entla & 255).to_bytes(1, byteorder='big').hex()
        ENTLA = ''.join([entla1, entla2])  # 拼接entla1 || entla2，相当于 entla1 + entla2
        return ENTLA
    
    def _calc_ZA(self, uid: bytes = CRYPTO_DEFAULT_UID) -> str:  # ✅
        """
        使用公钥和用户ID生成ZA-用户身份标识
        ZA=H256(ENTLA || IDA || a || b || G || x || y)  其中G为 Gx || Gy
        :param x: 公钥x坐标, 16进制字符串
        :param y: 公钥y坐标, 16进制字符串
        :param uid: 用户id, bytes字符串, 默认为 b'1234567812345678'
        :return:
        """
        ENTLA = self._calc_ENTLA(uid)  # '0080'
        IDA = uid.hex()  # '31323334353637383132333435363738'
        a, b, gx, gy, x, y = self.curve.a, self.curve.b, self.curve.gx, self.curve.gy, self.x, self.y
        z = H256(ENTLA, IDA, a, b, gx, gy, x, y)
        ZA = sm3.sm3_hash(z)
        return ZA
    
    def sm3_digest(self, msg: bytes, uid: bytes = CRYPTO_DEFAULT_UID) -> str:
        """
        通过SM3哈希算法计算消息摘要
        :param msg: 消息数据, bytes类型
        :param uid: 用户id, bytes字符串, 默认为 b'1234567812345678'
        :return:
        """
        ZA = self._calc_ZA(uid)
        M_ = bytes.fromhex(ZA + msg.hex())  # 待签名消息
        digest = sm3.sm3_hash(M_)
        return digest
    
    def encrypt(self, msg: bytes, k: str = None, mode=1):
        # 公钥加密函数，data消息(bytes)
        msg = msg.hex()  # 消息转化为16进制字符串
        curve = self.curve
        para_len = curve.para_len
        
        if k is None:
            k = func.random_hex(para_len)
            print('k', k)
        
        g = curve.gx + curve.gy
        pub = self.x + self.y
        
        C1 = curve.scalar_mul(int(k, 16), g)
        xy = curve.scalar_mul(int(k, 16), pub)
        x2 = xy[0:para_len]
        y2 = xy[para_len:2 * para_len]
        ml = len(msg)
        t = sm3.sm3_kdf(xy.encode('utf8'), ml // 2)
        if int(t, 16) == 0:
            return None
        else:
            form = '%%0%dx' % ml
            C2 = form % (int(msg, 16) ^ int(t, 16))
            C3 = sm3.sm3_hash([i for i in bytes.fromhex('%s%s%s' % (x2, msg, y2))])
            if mode:
                return bytes.fromhex('%s%s%s' % (C1, C3, C2))
            else:
                return bytes.fromhex('%s%s%s' % (C1, C2, C3))
    
    def verify(self, sig: Signature, msg: bytes):
        # 验签函数，sign签名r||s，E消息hash，public_key公钥
        r, s = sig.r, sig.s
        curve = self.curve
        
        # 消息转化为16进制字符串
        e = hex2int(msg.hex())
        n = hex2int(curve.n)
        
        g = ''.join([curve.gx, curve.gy])
        
        t = (r + s) % n
        if t == 0:
            return 0
        
        pub = self.x + self.y
        P1 = self.curve.scalar_mul(s, g)
        P2 = self.curve.scalar_mul(t, pub)
        if P1 == P2:
            P1 = '%s%s' % (P1, 1)
            P1 = self.curve.double(P1)
        else:
            P1 = '%s%s' % (P1, 1)
            P1 = self.curve.add(P1, P2)
            P1 = self.curve._convert_jacb_to_nor(P1)
        
        x = int(P1[0:self.curve.para_len], 16)
        return r == (e + x) % n
    
    def verify_with_sm3(self, sig: Signature, msg: bytes, uid: bytes = CRYPTO_DEFAULT_UID):
        digest = self.sm3_digest(msg, uid)  # 消息摘要
        sign_data = binascii.a2b_hex(digest.encode('utf-8'))
        return self.verify(sig, sign_data)
    
    def __eq__(self, other):  # TODO Remove
        return self.curve == other.curve and self.x == other.x and self.y == other.y


class PrivateKey:
    """私钥"""
    public_key: PublicKey  # 公钥对象
    d: str  # 私钥本质上就是一个256位的随机整数, 16进制字符串, 私钥可以由d表示
    
    def __init__(self, d: str):
        self.d = d  # int(d, 16) < n
        self.public_key = self.get_public_key()
        
        self.para_len = len(self.public_key.curve.n)  # 64
    
    def __repr__(self):
        return '<sm.PrivateKey "%s">' % self.d
    
    @property
    def value(self):
        return self.d
    
    def public(self) -> PublicKey:
        """
        公钥
        :return: 公钥对象
        """
        return self.public_key
    
    def get_public_key(self, curve=sm2p256curve):
        """根据曲线及私钥数字d通过kG计算出公钥"""
        G = ec.Point(curve, hex2int(curve.gx), hex2int(curve.gy))
        k = hex2int(self.d)  # 私钥
        K = G * k  # 公钥
        return PublicKey(int2hex(K.x), int2hex(K.y), curve=curve)
    
    def sign(self, msg: bytes, k: str) -> (int, int):  # 签名函数, data消息的hash，private_key私钥，K随机数，均为16进制字符串
        # 消息, 私钥数字D, 随机数K, 曲线阶N 转int
        curve = self.public_key.curve
        
        e, d, k, N = map(hex2int, [msg.hex(), self.d, k, curve.n])
        
        # kg运算
        P1 = curve.scalar_base_mul(k)
        
        x = int(P1[0:self.para_len], 16)
        
        r = ((e + x) % N)
        
        if r == 0 or r + k == N:
            return None, None
        
        # 计算 （私钥+1) ^ （N - 2）% N
        d_1 = pow(d + 1, N - 2, N)
        
        # ((私钥+1) * (随机数 + r) - r )  % N
        s = (d_1 * (k + r) - r) % N
        
        if s == 0:
            return None, None
        
        return r, s
    
    def sign_with_sm3(self, msg: bytes, k: str = None, uid: bytes = CRYPTO_DEFAULT_UID) -> Signature:
        """
        签名
        :param msg:
        :param k: 随机数
        :param uid:
        :return:
        """
        digest = self.public_key.sm3_digest(msg, uid)  # 消息摘要
        sign_data = binascii.a2b_hex(digest.encode('utf-8'))
        if k is None:
            k = func.random_hex(self.para_len)
        r, s = self.sign(sign_data, k)  # 16进制
        return Signature(r, s)
    
    def decrypt(self, data, mode=1):
        # 解密函数，data密文（bytes） mode: 0-C1C2C3, 1-C1C3C2 (default is 1)
        curve = self.public_key.curve
        para_len = curve.para_len
        
        data = data.hex()
        len_2 = 2 * para_len
        len_3 = len_2 + 64
        
        C1 = data[0:len_2]
        if mode == 1:  # C1C3C2
            C2 = data[len_3:]
        else:  # C1C2C3
            C2 = data[len_2:-para_len]
        
        xy = curve.scalar_mul(int(self.d, 16), C1)
        
        cl = len(C2)
        t = sm3.sm3_kdf(xy.encode('utf8'), cl // 2)
        if int(t, 16) == 0:
            return None
        else:
            form = '%%0%dx' % cl
            M = form % (int(C2, 16) ^ int(t, 16))
            return bytes.fromhex(M)
