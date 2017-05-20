# -*- coding:utf-8 -*-

# Author: ChengYao
# Created time: 2017年5月15日 下午12:37
# Email: chengyao09@hotmail.com
# Description: TEST

import user
import netease_redis as nr


def test_user_relation():
    uid = '18461341'
    followeds, more = user.get_user_followeds(uid)
    nr.add_user_followeds(uid, followeds)


def test_favorite_musics():
    uid = '45351485'
    musics = user.get_user_musics(uid)
    nr.add_user_musics(uid, musics)

if __name__ == '__main__':
    test_favorite_musics()
