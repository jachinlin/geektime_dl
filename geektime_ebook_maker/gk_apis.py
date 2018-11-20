# coding=utf8

import requests


class GkApiClient(object):
    """
    一个课程，包括专栏、视频、微课等，称作 `course`
    课程下的章节，包括文章、者视频等，称作 `post`
    """
    cookies = None

    @classmethod
    def login(cls, acc, psd, area='86'):
        """登录"""
        url = 'https://account.geekbang.org/account/ticket/login'

        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Host': 'account.geekbang.org',
            'Referer': 'https://account.geekbang.org/signin?redirect=https%3A%2F%2Fwww.geekbang.org%2F',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:59.0) Gecko/20100101 Firefox/59.0'
        }

        data = {
            "country": area,
            "cellphone": acc,
            "password": psd,
            "captcha": "",
            "remember": 1,
            "platform": 3,
            "appid": 1
        }

        resp = requests.post(url, headers=headers, json=data, timeout=10)

        if not (resp.status_code == 200 and resp.json().get('code') == 0):
            raise Exception('login fail:' + resp.json()['error']['msg'])
        cls.cookies = dict(resp.cookies.items())

    def get_course_list(self):
        """获取课程列表"""
        url = 'https://time.geekbang.org/serv/v1/column/all'
        headers = {
            'Referer': 'https://time.geekbang.org/paid-content',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:59.0) Gecko/20100101 Firefox/59.0'
        }

        resp = requests.get(url, headers=headers, cookies=self.cookies)

        if not (resp.status_code == 200 and resp.json().get('code') == 0):
            raise Exception('course query fail:' + resp.json()['error']['msg'])
        return resp.json()['data']

    def get_course_content(self, course_id):
        """获取课程所有章节列表"""
        url = 'https://time.geekbang.org/serv/v1/column/articles'
        data = {"cid": str(course_id), "size": 1000, "prev": 0, "order": "newest"}
        headers = {
            'Referer': 'https://time.geekbang.org/column/{}'.format(str(course_id))
        }

        resp = requests.post(url, json=data, headers=headers, cookies=self.cookies, timeout=10)
        if not (resp.status_code == 200 and resp.json().get('code') == 0):
            raise Exception('course query fail:' + resp.json()['error']['msg'])

        return resp.json()['data']['list']

    def get_course_intro(self, course_id):
        """课程简介"""
        url = 'https://time.geekbang.org/serv/v1/column/intro'
        headers = {
            'Content-Type': 'application/json',
            'Referer': 'https://time.geekbang.org/column/{}'.format(course_id)
        }

        resp = requests.post(url, headers=headers, cookies=self.cookies, json={'cid': str(course_id)}, timeout=10)

        if not (resp.status_code == 200 and resp.json().get('code') == 0):
            raise Exception('course query fail:' + resp.json()['error']['msg'])

        return resp.json()['data']

    def get_post_content(self, article_id):
        """课程章节详情"""
        url = 'https://time.geekbang.org/serv/v1/article'
        headers = {
            'Content-Type': 'application/json',
            'Referer': 'https://time.geekbang.org/column/article/{}'.format(str(article_id))
        }

        resp = requests.post(url, headers=headers, cookies=self.cookies, json={'id': str(article_id)}, timeout=10)

        if not (resp.status_code == 200 and resp.json().get('code') == 0):
            raise Exception('course query fail:' + resp.json()['error']['msg'])

        return resp.json()['data']
