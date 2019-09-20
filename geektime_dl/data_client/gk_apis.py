# coding=utf8


import threading
import functools
import time
import random

import requests

from geektime_dl.utils import Singleton, synchronized

_ua = [
    "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Mobile Safari/537.36"  # noqa: E501
]


class GkApiError(Exception):
    """"""


def _retry(func):
    """
    0.1s 后重试
    """
    @functools.wraps(func)
    def wrap(gk_api: 'GkApiClient', *args, **kwargs):
        try:
            res = func(gk_api, *args, **kwargs)
            return res
        except requests.RequestException:
            time.sleep(0.1)
            gk_api.reset_session()
            return func(gk_api, *args, **kwargs)
        except GkApiError:
            raise
        except Exception as e:
            raise GkApiError("gk api error") from e

    return wrap


class GkApiClient(metaclass=Singleton):
    """
    一个课程，包括专栏、视频、微课等，称作 `course` 或者 `column`
    课程下的章节，包括文章、者视频等，称作 `post` 或者 `article`
    """
    _headers_tmpl = {
        'Content-Type': 'application/json',
        'User-Agent': random.choice(_ua)
    }

    def __init__(self, account: str, password: str, area: str = '86'):
        self._cookies = None
        self._lock = threading.Lock()
        self._account = account
        self._password = password
        self._area = area
        self.reset_session()

    def _post(self, url: str, data: dict = None, **kwargs) -> requests.Response:

        headers = kwargs.setdefault('headers', {})
        headers.update(self._headers_tmpl)
        resp = requests.post(url, json=data, timeout=10, **kwargs)
        resp.raise_for_status()

        if resp.json().get('code') != 0:
            raise GkApiError('gk api fail:' + resp.json()['error']['msg'])
        return resp

    def reset_session(self) -> None:
        self._headers_tmpl['User-Agent'] = random.choice(_ua)
        self._login()

    @synchronized()
    def _login(self) -> None:
        """登录"""
        url = 'https://account.geekbang.org/account/ticket/login'

        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',  # noqa: E501
            'Host': 'account.geekbang.org',
            'Referer': 'https://account.geekbang.org/signin?redirect=https%3A%2F%2Fwww.geekbang.org%2F',  # noqa: E501
        }

        data = {
            "country": self._area,
            "cellphone": self._account,
            "password": self._password,
            "captcha": "",
            "remember": 1,
            "platform": 3,
            "appid": 1
        }

        resp = self._post(url, data, headers=headers)

        self._cookies = resp.cookies

    @_retry
    def get_course_list(self) -> dict:
        """
        获取课程列表
        :return:
            key: value
            '1'
            '2'
            '3'
            '4':
        """
        url = 'https://time.geekbang.org/serv/v1/column/all'
        headers = {
            'Referer': 'https://time.geekbang.org/paid-content',
        }

        resp = self._post(url, headers=headers, cookies=self._cookies)
        return resp.json()['data']

    @_retry
    def get_post_list_of(self, course_id: int) -> list:
        """获取课程所有章节列表"""
        url = 'https://time.geekbang.org/serv/v1/column/articles'
        data = {
            "cid": str(course_id), "size": 1000, "prev": 0, "order": "newest"
        }
        headers = {
            'Referer': 'https://time.geekbang.org/column/{}'.format(course_id),
        }

        resp = self._post(url, data, headers=headers, cookies=self._cookies)

        if not resp.json()['data']:
            raise Exception('course not exists:%s' % course_id)

        return resp.json()['data']['list'][::-1]

    @_retry
    def get_course_intro(self, course_id: int) -> dict:
        """课程简介"""
        url = 'https://time.geekbang.org/serv/v1/column/intro'
        headers = {
            'Referer': 'https://time.geekbang.org/column/{}'.format(course_id),
        }

        resp = self._post(
            url, {'cid': str(course_id)}, headers=headers, cookies=self._cookies
        )

        data = resp.json()['data']
        if not data:
            raise GkApiError('course not exists:%s' % course_id)
        return data

    @_retry
    def get_post_content(self, post_id: int) -> dict:
        """课程章节详情"""
        url = 'https://time.geekbang.org/serv/v1/article'
        headers = {
            'Referer': 'https://time.geekbang.org/column/article/{}'.format(
                '134020')
        }

        resp = self._post(
            url, {'id': post_id}, headers=headers, cookies=self._cookies
        )

        return resp.json()['data']

    @_retry
    def get_post_comments(self, post_id: int) -> list:
        """课程章节评论"""
        url = 'https://time.geekbang.org/serv/v1/comments'
        headers = {
            'Referer': 'https://time.geekbang.org/column/article/{}'.format(
                post_id)
        }

        resp = self._post(
            url, {"aid": str(post_id), "prev": 0},
            headers=headers, cookies=self._cookies
        )

        return resp.json()['data']['list']
