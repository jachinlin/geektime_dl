# coding=utf8

import threading
import time

from geektime_dl.utils import (
    get_working_folder,
    Singleton,
    synchronized,
    parse_column_ids
)
from geektime_dl import log


def test_logging():
    log.logger.info('guess where i will be ')

    log_file = get_working_folder() / 'geektime.log'
    with open(log_file) as f:
        logs = f.read()
        assert 'guess where i will be ' in logs
        assert 'INFO' in logs


def test_singleton():
    class S(metaclass=Singleton):
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

        @synchronized()
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


def test_parse_column_ids():
    ids = '1'
    ids2 = '1-3'
    ids3 = '3,6-8'
    assert parse_column_ids(ids) == [1]
    assert parse_column_ids(ids2) == [1, 2, 3]
    assert parse_column_ids(ids3) == [3, 6, 7, 8]
