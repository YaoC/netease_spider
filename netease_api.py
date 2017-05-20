# -*- coding:utf-8 -*-

# Author: ChengYao
# Created time: 2017年5月14日 下午3:20
# Email: chengyao09@hotmail.com
# Description: 网易云音乐API加密

import json
import base64
from secrets import token_hex
from Crypto.Cipher import AES
from binascii import hexlify

modulus = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
nonce = '0CoJUm6Qyw8W8jud'
pubKey = '010001'


def createSecretKey(size):
    return token_hex(size)[:16]


def aesEncrypt(text, secKey):
    try:
        text = text.decode()
    except AttributeError:
        pass
    pad = 16 - len(text) % 16
    text = text + pad * chr(pad)
    encryptor = AES.new(secKey, 2, '0102030405060708')
    ciphertext = encryptor.encrypt(text)
    ciphertext = base64.b64encode(ciphertext)
    return ciphertext


def rsaEncrypt(text, pubKey, modulus):
    text = text[::-1]
    text = bytes(text, 'utf-8')
    text = hexlify(text)
    rs = int(text, 16) ** int(pubKey, 16) % int(modulus, 16)
    return format(rs, 'x').zfill(256)


def encrypted_request(text):
    text = json.dumps(text)
    secKey = createSecretKey(16)
    encText = aesEncrypt(aesEncrypt(text, nonce), secKey)
    encSecKey = rsaEncrypt(secKey, pubKey, modulus)
    data = {
        'params': encText.decode(),
        'encSecKey': encSecKey
    }
    return data

if __name__ == '__main__':
    req = {
        "offset": 0,
        "uid": '45351485'
    }
    print(encrypted_request(req))
