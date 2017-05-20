# -*- coding:utf-8 -*-

# Author: ChengYao
# Created time: 2017年5月14日 下午7:02
# Email: chengyao09@hotmail.com
# Description: 爬取用户关系和播放记录

import sys
import io
import time
import threading
import requests
import json
import netease_api

# 代理服务器
proxyHost = "proxy.abuyun.com"
proxyPort = "9010"

# 代理隧道验证信息
proxyUser = "HD300Y24I4Z1742P"
proxyPass = "99A8A6AFD693F721"

proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
    "host": proxyHost,
    "port": proxyPort,
    "user": proxyUser,
    "pass": proxyPass,
}

# proxies = {
#     "http": proxyMeta,
#     "https": proxyMeta,
# }
#
proxies = None

MAX_OFFSET = 20

headers = {
    'Referer': 'http://music.163.com/',
    'Host': 'music.163.com',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:38.0) Gecko/20100101 Firefox/38.0 Iceweasel/38.3.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Cookie': 'appver=1.5.0.75771;MUSIC_U=e954e2600e0c1ecfadbd06b365a3950f2fbcf4e9ffcf7e2733a8dda4202263671b4513c5c9ddb66f1b44c7a29488a6fff4ade6dff45127b3e9fc49f25c8de500d8f960110ee0022abf122d59fa1ed6a2;',
}
# post的数据
user_data = {
    'uid': '107948356',
    'type': '0',
    'params': 'vRlMDmFsdQgApSPW3Fuh93jGTi/ZN2hZ2MhdqMB503TZaIWYWujKWM4hAJnKoPdV7vMXi5GZX6iOa1aljfQwxnKsNT+5/uJKuxosmdhdBQxvX/uwXSOVdT+0RFcnSPtv',
    'encSecKey': '46fddcef9ca665289ff5a8888aa2d3b0490e94ccffe48332eca2d2a775ee932624afea7e95f321d8565fd9101a8fbc5a9cadbe07daa61a27d18e4eb214ff83ad301255722b154f3c1dd1364570c60e3f003e15515de7c6ede0ca6ca255e8e39788c2f72877f64bc68d29fac51d33103c181cad6b0a297fe13cd55aa67333e3e5'
}


def get_user_musics(uid):
    print("%s,爬取用户 %s 播放最多的歌曲" % (threading.current_thread().name, uid))
    '''get_user_music
    根据用户id获取用户播放最多的歌曲
    Arguments:
        uid {[string]} -- [用户id]
    Returns:
        musics[map] -- [歌曲id->权重]
    '''
    url = 'http://music.163.com/weapi/v1/play/record?csrf_token='
    user_data['uid'] = uid
    musics = {}
    try:
        response = requests.post(url, headers=headers,
                                 data=user_data, proxies=proxies)
        response = response.content
        json_text = json.loads(response.decode("utf-8"))
        json_all_data = json_text['allData']
    except Exception as e:
        print('%s,出现错误啦~错误是:' % threading.current_thread().name, e)
        time.sleep(60)
        return musics
    try:
        # allData:所有时间 weekData:最近一周
        for json_music in json_all_data:
            json_song = json_music['song']
            musics[json_song['privilege']['id']] = json_music['score']
            # print('{}:{}'.format(json_song['name'], json_music['score']))
    except KeyError:
        print('id为', end="")
        print(uid, end="")
        print('%s,的用户听歌排行不可查看~' % threading.current_thread().name)
    except Exception as e:
        print('%s出现错误啦~错误是:' % threading.current_thread().name, e)
    finally:
        return musics


def get_all_followeds(uid):
    offset = 0
    more = True
    users = []
    while more and offset < MAX_OFFSET:
        u, has_next = get_user_followeds(uid, offset=offset)
        more = has_next
        offset += 10
        users += u
    return users


def get_user_followeds(uid, offset=0):
    # print("爬取用户 %s 的粉丝 %d" % (uid, offset))
    request = {
        "offset": offset,
        "userId": uid
    }
    request = netease_api.encrypted_request(request)
    url = 'http://music.163.com/weapi/user/getfolloweds?csrf_token='
    # print(user_data)
    followeds = []
    more = False
    try:
        response = requests.post(url, headers=headers,
                                 data=request, proxies=proxies)
        response = response.content
        json_text = json.loads(response.decode("utf-8"))
        json_all_data = json_text['followeds']
    except Exception as e:
        print('%s,出现错误啦~错误是:' % threading.current_thread().name, e)
        time.sleep(60)
        return followeds, more
    try:
        json_all_data = json_text['followeds']
        more = json_text['more']
        for followed in json_all_data:
            # print(followed['nickname'])
            followeds.append(followed['userId'])
    except KeyError:
        print('%s,id为' % threading.current_thread().name, end="")
        print(uid, end="")
        print(' 的用户好像没有粉丝。。。')
    except Exception as e:
        print('%s 出现错误啦~错误是:' % threading.current_thread().name, e)
    finally:
        return followeds, more


def get_music_url(songs):
    urls = {}
    request = {
        "ids": songs,
        "br": '96000'
    }
    request = netease_api.encrypted_request(request)
    url = 'http://music.163.com/weapi/song/enhance/player/url?csrf_token='
    try:
        response = requests.post(url, headers=headers,
                                 data=request, proxies=proxies)
        response = response.content
        json_text = json.loads(response.decode("utf-8"))
    except Exception as e:
        print('%s,出现错误啦~错误是:' % threading.current_thread().name, e)
        time.sleep(30)
        return urls
    songs_list = json_text['data']
    for song in songs_list:
        urls[song['id']] = song['url']
    # print(urls)
    return urls

if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    # musics = get_user_musics('18461341')
    # print(musics)
    # followeds, more = get_user_followeds('18461341')
    # print(followeds)
    # print(more)
    # followeds, more = get_user_followeds('18461341', offset=1)
    # print(followeds)
    # print(more)
    songs = ["680671", "28838073", "27993445",
             "228200", "27949874", "1142999", "26480490"]
    get_music_url(songs)
