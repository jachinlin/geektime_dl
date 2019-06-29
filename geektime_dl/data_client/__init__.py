# coding=utf8

import json
from .gk_apis import GkApiClient
from geektime_dl.utils import Singleton
from geektime_dl.utils._logging import logger
import time

class DataClient(metaclass=Singleton):

    def __init__(self):
        self._gk = GkApiClient()

    @property
    def cookies(self):
        return self._gk.cookies

    def get_course_list(self):
        return self._gk.get_course_list()

    def get_course_intro(self, course_id):
        return self._gk.get_course_intro(course_id)

    def get_post_content(self, post_id):
        data = self._gk.get_post_content(post_id)
        return data

    def _get_post_comments(self, post_id):
        data = self._gk.get_post_comments(post_id)
        return data

    def get_video_play_auth(self, post):
        data = self._gk.get_video_play_auth(post)
        return data
        
    def get_course_content(self, course_id):

        # data
        data = []
        post_ids = self._gk.get_course_content(course_id)

        for post in post_ids:
            post_detail = self._gk.get_post_content(post['id'])
            post_detail['comments'] = self._gk.get_post_comments(post['id'])
            data.append(post_detail)
            time.sleep(1)
        return data



