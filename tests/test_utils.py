# coding=utf8

import os
import threading
import time
from geektime_dl import utils
from geektime_dl.utils import mp3_downloader, m3u8_downloader, _logging


def test_mp3_downloader():
    dl = mp3_downloader.Downloader()
    dl.run(
        mp3_url='https://res001.geekbang.org/resource/audio/fd/da/fde5b177af8b243cbd34413535e72cda.mp3',
        out_file='mp3.mp3',
        out_dir='.'
    )


def test_mp4_downloader():
    dl = m3u8_downloader.Downloader()
    dl.run('https://res001.geekbang.org/media/video/17/ae/17af9f0d61ff9df13b26f299082d81ae/sd/sd.m3u8', '.')


def test_logging():
    _logging.logger.info('guess where i will be ')

    with open(os.path.join('.', 'geektime.log')) as f:
        logs = f.read()
        assert 'guess where i will be ' in logs
        assert 'INFO' in logs


def test_singleton():
    class S(metaclass=utils.Singleton):
        pass

    a = S()
    b = S()
    assert a is b


def test_synchronized():

    class A(object):
        def __init__(self):
            self._lock = threading.Lock()

        def func(self):
            time.sleep(2)

        @utils.synchronized()
        def synchronized_func(self):
            time.sleep(2)

    a = A()

    start = time.time()
    t_list = []
    for i in range(3):
        t = threading.Thread(target=a.synchronized_func)
        t_list.append(t)
        t.start()
    for t in t_list:
        t.join()
    time_cost = time.time() - start

    assert time_cost > 6

    start = time.time()
    t_list = []
    for i in range(3):
        t = threading.Thread(target=a.func)
        t_list.append(t)
        t.start()
    for t in t_list:
        t.join()
    time_cost = time.time() - start

    assert time_cost < 3


