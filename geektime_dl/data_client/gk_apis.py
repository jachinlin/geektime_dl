# coding=utf8


import threading
import functools
import time
import random

import requests

from geektime_dl.utils import Singleton, synchronized, debug_log

_ua = [
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/534.25 (KHTML, like Gecko) Chrome/12.0.706.0 Safari/534.25",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/534.25 (KHTML, like Gecko) Chrome/12.0.704.0 Safari/534.25",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/534.24 (KHTML, like Gecko) Ubuntu/10.10 Chromium/12.0.703.0 Chrome/12.0.703.0 Safari/534.24",
    "Mozilla/5.0 (X11; Linux i686) AppleWebKit/534.24 (KHTML, like Gecko) Ubuntu/10.10 Chromium/12.0.702.0 Chrome/12.0.702.0 Safari/534.24",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.24 (KHTML, like Gecko) Chrome/12.0.702.0 Safari/534.24",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/534.24 (KHTML, like Gecko) Chrome/12.0.702.0 Safari/534.24",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/534.24 (KHTML, like Gecko) Chrome/11.0.700.3 Safari/534.24",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/534.24 (KHTML, like Gecko) Chrome/11.0.699.0 Safari/534.24",
    "Mozilla/5.0 (Windows NT 6.0; WOW64) AppleWebKit/534.24 (KHTML, like Gecko) Chrome/11.0.699.0 Safari/534.24",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_6) AppleWebKit/534.24 (KHTML, like Gecko) Chrome/11.0.698.0 Safari/534.24",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/534.24 (KHTML, like Gecko) Chrome/11.0.697.0 Safari/534.24",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/534.24 (KHTML, like Gecko) Chrome/11.0.696.71 Safari/534.24",
    "Mozilla/5.0 (X11; U; Linux amd64; rv:5.0) Gecko/20100101 Firefox/5.0 (Debian)",
    "Mozilla/5.0 (X11; U; Linux amd64; en-US; rv:5.0) Gecko/20110619 Firefox/5.0",
    "Mozilla/5.0 (X11; Linux) Gecko Firefox/5.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:5.0) Gecko/20100101 Firefox/5.0 FirePHP/0.5",
    "Mozilla/5.0 (X11; Linux x86_64; rv:5.0) Gecko/20100101 Firefox/5.0 Firefox/5.0",
    "Mozilla/5.0 (X11; Linux x86_64) Gecko Firefox/5.0",
    "Mozilla/5.0 (X11; Linux ppc; rv:5.0) Gecko/20100101 Firefox/5.0",
    "Mozilla/5.0 (X11; Linux AMD64) Gecko Firefox/5.0",
    "Mozilla/5.0 (X11; FreeBSD amd64; rv:5.0) Gecko/20100101 Firefox/5.0",
    "Mozilla/5.0 (Windows NT 6.2; WOW64; rv:5.0) Gecko/20100101 Firefox/5.0",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:5.0) Gecko/20110619 Firefox/5.0",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:5.0) Gecko/20100101 Firefox/5.0",
    "Mozilla/5.0 (Windows NT 6.1; rv:6.0) Gecko/20100101 Firefox/5.0",
    "Mozilla/5.0 (Windows NT 6.1.1; rv:5.0) Gecko/20100101 Firefox/5.0",
    "Mozilla/5.0 (Windows NT 5.2; WOW64; rv:5.0) Gecko/20100101 Firefox/5.0",
    "Mozilla/5.0 (Windows NT 5.1; U; rv:5.0) Gecko/20100101 Firefox/5.0"
]

class GkApiError(Exception):
    """"""


def retry(func):
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
    一个课程，包括专栏、视频、微课等，称作 `course`
    课程下的章节，包括文章、者视频等，称作 `post`
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
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Host': 'account.geekbang.org',
            'Referer': 'https://account.geekbang.org/signin?redirect=https%3A%2F%2Fwww.geekbang.org%2F',
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

        self._cookies = dict(resp.cookies.items())

    @debug_log
    @retry
    def get_course_list(self):
        """获取课程列表"""
        url = 'https://time.geekbang.org/serv/v1/column/all'
        headers = {
            'Referer': 'https://time.geekbang.org/paid-content',
        }

        resp = self._post(url, headers=headers, cookies=self._cookies)
        return resp.json()['data']

    @debug_log
    @retry
    def get_course_content(self, course_id: int):
        """获取课程所有章节列表"""
        url = 'https://time.geekbang.org/serv/v1/column/articles'
        data = {"cid": str(course_id), "size": 1000, "prev": 0, "order": "newest"}
        headers = {
            'Referer': 'https://time.geekbang.org/column/{}'.format(str(course_id)),
        }

        resp = self._post(url, data, headers=headers, cookies=self._cookies)

        if not resp.json()['data']:
            raise Exception('course not exists:%s' % course_id)

        return resp.json()['data']['list'][::-1]

    @debug_log
    @retry
    def get_course_intro(self, course_id: int):
        """课程简介"""
        url = 'https://time.geekbang.org/serv/v1/column/intro'
        headers = {
            'Referer': 'https://time.geekbang.org/column/{}'.format(course_id),
        }

        resp = self._post(url, {'cid': str(course_id)}, headers=headers, cookies=self._cookies)

        data = resp.json()['data']
        if not data:
            raise GkApiError('course not exists:%s' % course_id)
        return data

    @debug_log
    @retry
    def get_post_content(self, post_id: int):
        """课程章节详情"""
        url = 'https://time.geekbang.org/serv/v1/article'
        headers = {
            'Referer': 'https://time.geekbang.org/column/article/{}'.format(str(post_id)),
        }

        resp = self._post(url, {'id': str(post_id)}, headers=headers, cookies=self._cookies)

        return resp.json()['data']

    @debug_log
    @retry
    def get_post_comments(self, post_id: int):
        """课程章节评论"""
        url = 'https://time.geekbang.org/serv/v1/comments'
        headers = {
            'Referer': 'https://time.geekbang.org/column/article/{}'.format(str(post_id)),
        }

        resp = self._post(url, {"aid": str(post_id), "prev": 0}, headers=headers, cookies=self._cookies)

        return resp.json()['data']['list']
