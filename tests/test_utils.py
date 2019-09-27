# coding=utf8

import os
import threading
import time
from pathlib import Path

from geektime_dl import utils
from geektime_dl.utils import mp3_downloader, m3u8_downloader, log


def test_mp3_downloader(tmp_path: Path):
    dl = mp3_downloader.Downloader(str(tmp_path))
    dl.run(
        url='https://res001.geekbang.org/resource/audio/fd/da/fde5b177af8b243cbd34413535e72cda.mp3',  # noqa: E501
        file_name='mp3.mp3'
    )
    dl.shutdown()
    mp3 = tmp_path / 'mp3.mp3'
    assert mp3.is_file()
    mp3.unlink()


def test_mp4_downloader(tmp_path: Path):
    dl = m3u8_downloader.Downloader(str(tmp_path))
    dl.run('https://res001.geekbang.org/media/video/17/ae/17af9f0d61ff9df13b26f299082d81ae/sd/sd.m3u8', 'mp4')  # noqa: E501
    dl.shutdown()
    mp4 = tmp_path / 'mp4.ts'
    assert mp4.is_file()
    mp4.unlink()


def test_logging():
    log.logger.info('guess where i will be ')

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
            time.sleep(0.2)

        @utils.synchronized()
        def synchronized_func(self):
            time.sleep(0.2)

    a = A()

    start = time.time()
    t_list = []
    for i in range(2):
        t = threading.Thread(target=a.synchronized_func)
        t_list.append(t)
        t.start()
    for t in t_list:
        t.join()
    time_cost = time.time() - start

    assert time_cost >= 0.2 * 2

    start = time.time()
    t_list = []
    for i in range(2):
        t = threading.Thread(target=a.func)
        t_list.append(t)
        t.start()
    for t in t_list:
        t.join()
    time_cost = time.time() - start

    assert time_cost < 0.2 * 2


