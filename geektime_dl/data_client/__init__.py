# coding=utf8

import json
import os
import functools
import threading

from tinydb import TinyDB, Query

from geektime_dl.data_client.gk_apis import GkApiClient, GkApiError
from geektime_dl.utils import Singleton, synchronized


def _local_storage(table: str):
    """
    存取本地 课程/章节 内容
    """
    def decorator(func):
        @functools.wraps(func)
        def wrap(self: 'DataClient', *args, **kwargs):
            nonlocal table
            force = kwargs.get('force')
            _id = kwargs.get('{}_id'.format(table)) or args[0]
            collection = Query()

            data = None
            if not force:
                res = self.db.table(table).search(collection.id == _id)
                if res:
                    data = res[0]
            if data is None:
                data = func(self, *args, **kwargs)
                self.db.table(table).upsert(data, collection.id == _id)
            return data
        return wrap
    return  decorator


class DataClient(metaclass=Singleton):

    def __init__(self, gk: GkApiClient, db: TinyDB):
        self._gk = gk
        self.db = db
        self._lock = threading.Lock()  # tinydb 线程不安全

    def get_course_list(self, **kwargs) -> dict:
        """
        获取课程列表
        """
        return self._gk.get_course_list()

    @synchronized()
    @_local_storage('course')
    def get_course_intro(self, course_id: int, **kwargs) -> dict:
        """
        获取 course 简介
        """
        data = self._gk.get_course_intro(course_id)
        return data

    @synchronized()
    @_local_storage('post')
    def get_post_content(self, post_id: int, **kwargs) -> dict:
        """
        获取 post 的所有内容，包括评论
        """
        data = self._gk.get_post_content(post_id)
        data['comments'] = self._get_post_comments(post_id)

        return data

    def _get_post_comments(self, post_id: int) -> list:
        """
        获取 post 的评论
        """
        data = self._gk.get_post_comments(post_id)
        for c in data:
            c['replies'] = json.dumps(c.get('replies', []))
        return data

    def get_course_content(self, course_id: int, force: bool = False) -> list:
        """
        获取课程ID为 course_id 的所有章节内容
        """
        posts = []
        post_ids = self._gk.get_post_list_of(course_id)
        for post in post_ids:
            post_detail = self.get_post_content(post['id'], force=force)
            posts.append(post_detail)
        return posts


def get_data_client(cfg: dict) -> DataClient:
    gk = GkApiClient(
        account=cfg['account'],
        password=cfg['password'],
        area=cfg['area']
    )
    f = os.path.expanduser(
        os.path.join(cfg['output_folder'], 'geektime-localstorage.json'))
    db = TinyDB(f)

    dc = DataClient(gk, db)

    return dc
