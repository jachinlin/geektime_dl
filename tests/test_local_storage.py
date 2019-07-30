# coding=utf8

import json
import time

from tinydb import Query, TinyDB

from geektime_dl.data_client import DataClient, _JSONStorage


def test_get_course_list(dc: DataClient):
    assert  isinstance(dc.get_course_list(), dict)


def test_get_course_intro(dc: DataClient):
    assert dc.get_course_intro(212)


def test_get_post_content(dc: DataClient):
    assert dc.get_post_content(333)


def test_get_course_content(dc: DataClient):
    assert dc.get_course_content(212)


def test_local_storage(dc: DataClient):
    course_id = 212
    dc.get_course_intro(course_id)

    course = Query()
    assert dc.db.table('course').search(course.id==course_id)[0]


def test_force(dc: DataClient):
    course_id = 212
    course = Query()
    # read from gk api
    res = dc.get_course_intro(course_id)
    assert res['access_count'] == 1
    # check local storage
    res = dc.db.table('course').search(course.id == course_id)
    assert len(res) == 1
    assert res[0]['access_count'] == 1

    # read from local storage
    res = dc.get_course_intro(course_id)
    assert  res['access_count'] == 1
    # force read from gk api
    res = dc.get_course_intro(course_id, force=True)
    assert res['access_count'] == 2
    # check local storage
    res = dc.db.table('course').search(course.id == course_id)
    assert  len(res) == 1
    assert  res[0]['access_count'] == 2


def test_json_storage(db_file):
    """
    test my own json storage
    """

    db = TinyDB(db_file, storage=_JSONStorage)
    item = {'name': 'A very long entry'}

    db.insert(item)
    with open(db_file) as f:
        assert not f.read()

    time.sleep(10)
    db.insert(item)
    with open(db_file) as f:
        assert json.loads(f.read()) == {'_default': {'1': {'name': 'A very long entry'}, '2': {'name': 'A very long entry'}}}

    db.close()


def test_json_storage_atexit():
    # how to ?
    pass
