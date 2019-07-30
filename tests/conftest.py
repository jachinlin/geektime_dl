# coding=utf8

import os

import pytest
from tinydb import TinyDB
from tinydb.storages import MemoryStorage

from geektime_dl.data_client.gk_apis import GkApiClient
from geektime_dl.data_client import DataClient
from geektime_dl.utils.ebook import Render


@pytest.fixture
def gk() -> GkApiClient:
    account = os.getenv('account')
    password = os.getenv('password')
    return GkApiClient(account=account, password=password)


class FakeGk(GkApiClient):
    def __init__(self):
        self._access_count = 0

    def get_course_intro(self, course_id: int):
        self._access_count += 1
        return {'id': course_id, 'access_count': self._access_count}

    def get_course_list(self):
        return {'1': {'list': []}, '2': {'list': []}, '3': {'list': []}, '4': {'list': []}}

    def get_post_content(self, post_id: int):
        return {'id': post_id}

    def get_post_list_of(self, course_id: int):
        return [{'id': 123}, {'id': 456}]

    def get_post_comments(self, post_id: int):
        return []


@pytest.fixture
def dc() -> DataClient:
    db = TinyDB(storage=MemoryStorage)
    _gk = FakeGk()
    _dc = DataClient(_gk, db)
    yield _dc

    _dc.db.close()


@pytest.fixture
def output_folder() -> str:
    return '/tmp'


@pytest.fixture
def render(output_folder) -> Render:
    r = Render(output_folder)
    return r


@pytest.fixture
def db_file() -> str:
    path = '/tmp/test.json'
    if os.path.exists(path):
        os.remove(path)
    yield path
    os.remove(path)
