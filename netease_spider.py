# -*- coding:utf-8 -*-

# Author: ChengYao
# Created time: 2017年5月12日 下午1:26
# Email: chengyao09@hotmail.com
# Description: 网易云音乐爬虫

import user
import netease_redis as nr
import time
import threading

MAX_USER = 100000


def init(uid):
    users = user.get_all_followeds(uid)
    nr.add_user_followeds(uid, users)


def run():
    max_user = MAX_USER
    while nr.get_user_count() < max_user:
        uid = nr.get_a_user()
        musics = user.get_user_musics(uid)
        if musics == {}:
            continue
        nr.add_user_musics(uid, musics)
        users = user.get_all_followeds(uid)
        if users == []:
            continue
        nr.add_user_followeds(uid, users)
        nr.add_user(uid)


if __name__ == '__main__':
    # init('482998763')
    for x in range(10):
        t = threading.Thread(target=run)
        t.start()

    max_user = MAX_USER
    user_count = 0
    while user_count < max_user:
        user_count = nr.get_user_count()
        print("爬取 %d 个用户" % user_count)
        time.sleep(10)
