# coding=utf8

import json
from .gk_apis import GkApiClient
from .store_client import StoreClient
from geektime_dl.utils import Singleton
from geektime_dl.utils._logging import logger


class DataClient(metaclass=Singleton):

    def __init__(self):
        self._gk = GkApiClient()
        self._sc = StoreClient()

    @property
    def cookies(self):
        return self._gk.cookies

    def get_course_list(self):
        return self._gk.get_course_list()

    def get_course_intro(self, course_id, force=False):

        data = self._sc.get_course_intro(course_id)
        if force or not data:
            data = self._gk.get_course_intro(course_id)
            self._sc.save_column_info(**data)

        return data

    def get_post_content(self, post_id, force=False):

        data = self._sc.get_post_content(post_id)
        if force or not data:
            data = self._gk.get_post_content(post_id)
            self._sc.save_post_content(**data)

        return data

    def _get_post_comments(self, post_id, force=False):

        data = self._sc.get_post_comments(post_id)
        if force or not data:
            data = self._gk.get_post_comments(post_id)
            for c in data:
                c['replies'] = json.dumps(c.get('replies', []))
                self._sc.save_post_comment(article_id=post_id, **c)

        return data

    def get_course_content(self, course_id, force=False):

        # data
        data = []
        post_ids = self._gk.get_course_content(course_id)

        for post in post_ids:
            post_detail = self.get_post_content(post['id'], force=force)
            post_detail['comments'] = self._get_post_comments(post['id'], force=force)
            data.append(post_detail)

        return data



