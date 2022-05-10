# coding=utf8

import os
import threading
import time

import geektime_dl.utils
from geektime_dl import log


def test_logging():
    log.logger.info('guess where i will be ')

    with open(os.path.join('.', 'geektime.log')) as f:
        logs = f.read()
        assert 'guess where i will be ' in logs
        assert 'INFO' in logs


def test_singleton():
    class S(metaclass=geektime_dl.utils.Singleton):
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

        @geektime_dl.utils.synchronized()
        def synchronized_func(self):
            time.sleep(0.2)

    a = A()

    def time_cost(func) -> float:
        start = time.time()
        t_list = []
        for i in range(2):
            t = threading.Thread(target=func)
            t_list.append(t)
            t.start()
        for t in t_list:
            t.join()
        return time.time() - start

    assert time_cost(a.synchronized_func) >= 0.2 * 2
    assert time_cost(a.func) < 0.2 * 2


