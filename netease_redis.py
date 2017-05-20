# -*- coding:utf-8 -*-

# Author: ChengYao
# Created time: 2017年5月14日 下午5:33
# Email: chengyao09@hotmail.com
# Description: redis 操作

import redis
import csv
from collections import defaultdict

pool = redis.ConnectionPool(host='47.94.107.21', port=6379, db=0, password='chengyao001')

USERS = "users"
NEXT_USERS = "nUsers"
SONGS = "songs"

SONGS_DOWNLOAD = "songs_download"

FOLLOWEDS_PREFIX = "followeds-"
SONGS_PREFIX = "songs-"


def add_user_followeds(uid, users):
    r = redis.Redis(connection_pool=pool)
    pipe = r.pipeline()
    pipe.sadd(FOLLOWEDS_PREFIX + uid, *users)
    pipe.sadd(NEXT_USERS, *users)
    pipe.execute()


def get_user_count():
    r = redis.Redis(connection_pool=pool)
    return r.scard(USERS)


def add_user_musics(uid, musics):
    songs = musics.keys()
    r = redis.Redis(connection_pool=pool)
    pipe = r.pipeline()
    pipe.hmset(SONGS_PREFIX + uid, musics)
    pipe.sadd(SONGS, *songs)
    pipe.execute()


def get_a_user():
    r = redis.Redis(connection_pool=pool)
    user = r.spop(NEXT_USERS)
    return user.decode()


def add_user(uid):
    r = redis.Redis(connection_pool=pool)
    r.sadd(USERS, uid)


def get_musics(uid):
    r = redis.Redis(connection_pool=pool)
    musics = r.hgetall(SONGS_PREFIX + uid)
    return musics


def export_csv():
    r = redis.Redis(connection_pool=pool)
    file_name = 'netease_user_records.csv'
    count = 0
    total = 0
    with open(file_name, 'w') as file:
        writer = csv.writer(file)
        for user in r.sscan_iter(USERS):
            user = user.decode()
            musics = r.hgetall(SONGS_PREFIX + user)
            if musics == {}:
                print('%s is empty!' % user)
                continue
            num = len(musics)
            total += num
            for music in musics.items():
                writer.writerow([user, music[0].decode(), music[1].decode()])
            count += 1
            if count % 5000 == 0:
                print('export %d users...' % count)
    print('OK,total users %d' % count)
    print('average = %d' % (total // count))


def export_users():
    r = redis.Redis(connection_pool=pool)
    file_name = 'users.txt'
    count = 0
    with open(file_name, 'w') as f:
        for user in r.sscan_iter(USERS):
            f.write(user.decode() + '\n')
            count += 1
            if count % 10000 == 0:
                print('export %d users...' % count)
    print('OK,total users %d' % count)


def export_songs():
    r = redis.Redis(connection_pool=pool)
    file_name = 'songs.txt'
    count = 0
    with open(file_name, 'w') as f:
        for song in r.sscan_iter(SONGS):
            f.write(song.decode() + '\n')
            count += 1
            if count % 20000 == 0:
                print('export %d songs...' % count)
    print('OK,total songs %d' % count)


def get_songs(count=10):
    r = redis.Redis(connection_pool=pool)
    res = r.spop(SONGS, count)
    res = [s.decode() for s in res]
    return res


def get_songs_count():
    r = redis.Redis(connection_pool=pool)
    count = r.scard(SONGS)
    return count


def add_songs_download(sid):
    r = redis.Redis(connection_pool=pool)
    r.sadd(SONGS_DOWNLOAD, sid)


def get_download_count():
    r = redis.Redis(connection_pool=pool)
    count = r.scard(SONGS_DOWNLOAD)
    return count

if __name__ == '__main__':
    # r = redis.StrictRedis(host='localhost', port=6379, db=0)
    # r.set('foo', 'bar')
    # print(r.get('foo'))
    # user = get_a_user()
    # add_user(user)
    # print(get_user_count())

    # export_csv()
    # export_users()
    # export_songs()
    print(get_user_count())
