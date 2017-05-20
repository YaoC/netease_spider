# -*- coding:utf-8 -*-

# Author: ChengYao
# Created time: 2017年5月19日 上午2:05
# Email: chengyao09@hotmail.com
# Description: 下载音乐并保存片段

from pydub import AudioSegment
import os
import user
import requests
import time
import threading
import netease_redis as nr


# 保存原始音乐文件的文件夹
MUSIC_DIR = './music_raw'

# 保存文件片段的文件夹
SLICE_DIR = './music_slice'


def init_dirs():
    if not os.path.exists(MUSIC_DIR):
        os.makedirs(MUSIC_DIR)
    if not os.path.exists(SLICE_DIR):
        os.makedirs(SLICE_DIR)


def download_music(songs):
    print("%s:获取下载链接..."% threading.current_thread().name)
    urls = user.get_music_url(songs)
    for url in urls.items():
        print("%s:下载歌曲 %s ..." % (threading.current_thread().name, url[0]))
        try:
            r = requests.get(url[1])
            with open('%s/%s.mp3' % (MUSIC_DIR, url[0]), 'wb') as f:
                f.write(r.content)
        except Exception as e:
            print("%s:下载歌曲 %s 发生错误：" %
                  (threading.current_thread().name, url[0]), e)
        else:
            print("%s:歌曲 %s 下载完成！" % (threading.current_thread().name, url[0]))
            save_music_slice(url[0])
            nr.add_songs_download(url[0])


def save_music_slice(sid):
    song = AudioSegment.from_mp3('%s/%s.mp3' % (MUSIC_DIR, sid))
    mid = song.duration_seconds // 2
    # 得到歌曲最中间的5秒片段
    song_slice = song[(mid - 2) * 1000:(mid + 3) * 1000]
    song_slice.export("%s/%s.mp3" % (SLICE_DIR, sid), format="mp3")
    print("%s:歌曲 %s 的片段保存成功" % (threading.current_thread().name, sid))
    os.remove('%s/%s.mp3' % (MUSIC_DIR, sid))


def run():
    while nr.get_songs_count() > 0:
        print("%s:获取音乐id..." % threading.current_thread().name)
        songs = nr.get_songs()
        download_music(songs)
    print("%s 结束！" % threading.current_thread().name)

if __name__ == '__main__':
    init_dirs()
    for x in range(10):
        t = threading.Thread(target=run)
        t.start()
    while nr.get_songs_count() > 0:
        print("爬取 %d 首歌曲" % nr.get_download_count())
        time.sleep(10)
