# coding=utf8

import requests
import os
import json
import threading
from geektime_dl.utils import Singleton, synchronized, debug_log
import base64
import traceback
import time
from configparser import ConfigParser

class GkApiClient(metaclass=Singleton):
    """
    一个课程，包括专栏、视频、微课等，称作 `course`
    课程下的章节，包括文章、者视频等，称作 `post`
    """

    _headers_tmpl = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:59.0) Gecko/20100101 Firefox/59.0'
    }
    def __init__(self):

        cfg = ConfigParser()
        cfg.read('config.ini')

        self.username = cfg.get('user','username')
        self.password = cfg.get('user','password') 

        self.cookies = None
        self._cookie_file = cfg.get('user','cookie_path') 
        self._lock = threading.Lock()

        if os.path.exists(self._cookie_file):
            with open(self._cookie_file) as f:
                cookies = f.read()
                self.cookies = json.loads(cookies) if cookies else None

    @synchronized()
    def login(self, ):
        """登录"""
        url = 'https://account.geekbang.org/account/ticket/login'

        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Host': 'account.geekbang.org',
            'Referer': 'https://account.geekbang.org/signin?redirect=https%3A%2F%2Fwww.geekbang.org%2F',
            **self._headers_tmpl
        }
        data = {
            "country": '86',
            "cellphone": self.username,
            "password": self.password,
            "captcha": "",
            "remember": 1,
            "platform": 3,
            "appid": 1
        }
        resp = requests.post(url, headers=headers, json=data, timeout=10)

        if not (resp.status_code == 200 and resp.json().get('code') == 0):
            raise Exception('login fail:' + resp.json()['error']['msg'])

        self.cookies = dict(resp.cookies.items())
        with open(self._cookie_file, 'w') as f:
            f.write(json.dumps(self.cookies))

    @debug_log
    def get_course_list(self):
        """获取课程列表"""
        url = 'https://time.geekbang.org/serv/v1/column/all'
        headers = {
            'Referer': 'https://time.geekbang.org/paid-content',
            **self._headers_tmpl
        }
        if self.cookies == None:
            self.login()
            
        resp = requests.get(url, headers=headers, cookies=self.cookies)

        if not (resp.status_code == 200 and resp.json().get('code') == 0):
            time.sleep(5)
            self.login()
            return self.get_course_list()
            #raise Exception('course query fail:' + resp
            #raise Exception('course query fail:' + resp.json()['error']['msg'])
        return resp.json()['data']

    @debug_log
    def get_course_content(self, course_id):
        """获取课程所有章节列表"""
        url = 'https://time.geekbang.org/serv/v1/column/articles'
        data = {"cid": str(course_id), "size": 1000, "prev": 0, "order": "newest"}
        headers = {
            'Referer': 'https://time.geekbang.org/column/{}'.format(str(course_id)),
            **self._headers_tmpl
        }
        if self.cookies == None:
            self.login()
            
        resp = requests.post(url, json=data, headers=headers, cookies=self.cookies, timeout=10)

        if not (resp.status_code == 200 and resp.json().get('code') == 0):
            print('--------------------------- wait 5 seconds to retry ------------------------------------')
            time.sleep(5)
            self.login()
            return self.get_course_content(course_id)
            #raise Exception('course query fail:' + resp.json()['error']['msg'])
        if not data:
            raise Exception('course not exists:%s' % course_id)
        return resp.json()['data']['list'][::-1]

    @debug_log
    def get_course_intro(self, course_id):
        """课程简介"""
        url = 'https://time.geekbang.org/serv/v1/column/intro'
        headers = {
            'Referer': 'https://time.geekbang.org/column/{}'.format(course_id),
            **self._headers_tmpl
        }
        if self.cookies == None:
            self.login()
        resp = requests.post(url, headers=headers, cookies=self.cookies, json={'cid': str(course_id)}, timeout=10)

        if not (resp.status_code == 200 and resp.json().get('code') == 0):
            print('--------------------------- wait 5 seconds to retry ------------------------------------')
            time.sleep(5)
            self.login()
            return self.get_course_intro(course_id)
            # raise Exception('course query fail:' + resp.json()['error']['msg'])
        data = resp.json()['data']
        if not data:
            raise Exception('course not exists:%s' % course_id)
        return data

    @debug_log
    def get_post_content(self, post_id):
        """课程章节详情"""
        url = 'https://time.geekbang.org/serv/v1/article'
        headers = {
            'Referer': 'https://time.geekbang.org/column/article/{}'.format(str(post_id)),
            **self._headers_tmpl
        }
        if self.cookies == None:
            self.login()
        resp = requests.post(url, headers=headers, cookies=self.cookies, json={'id': str(post_id)}, timeout=10)

        if not (resp.status_code == 200 and resp.json().get('code') == 0):
            print("get_post_content error: " + resp.text)
            time.sleep(5)
            self.login()
            return self.get_post_content(post_id)
            #raise Exception('course query fail:' + resp.json()['error']['msg'])

        return resp.json()['data']

    @debug_log
    def get_post_comments(self, post_id):
        """课程章节评论"""
        url = 'https://time.geekbang.org/serv/v1/comments'
        headers = {
            'Referer': 'https://time.geekbang.org/column/article/{}'.format(str(post_id)),
            **self._headers_tmpl
        }
        result = []
        prev = 0
        while True:
            if self.cookies == None:
                self.login()
            resp = requests.post(url, headers=headers, cookies=self.cookies, json={"aid": str(post_id), "prev": prev}, timeout=10)
            if not (resp.status_code == 200 and resp.json().get('code') == 0):
                print('--------------------------- wait 5 seconds to retry ------------------------------------')
                time.sleep(5)
                self.login()
                return self.get_post_comments(post_id)
                #raise Exception('course query fail:' + resp.json()['error']['msg'])
            if len(resp.json()['data']['list']) > 0:
                prev = resp.json()['data']['list'][-1]['comment_ctime']
                result.extend(resp.json()['data']['list']) 
            return result
    
    @debug_log
    def get_video_play_auth(self, post):
        url = 'https://time.geekbang.org/serv/v3/source_auth/video_play_auth'
        
        headers = {
            'Referer': 'https://time.geekbang.org/course/detail/190-{}'.format(str(post['id'])),
            **self._headers_tmpl
        }
        if self.cookies == None:
            self.login()
        resp = requests.post(url, headers=headers, cookies=self.cookies, json={
            "aid": post['id'],
            "sku": str(post['sku']),
            "video_id": str(post['video_id']),
            "source_type": 1
        }, timeout=10)
        if not (resp.status_code == 200 and resp.json().get('code') == 0):
            print('--------------------------- wait 5 seconds to retry ------------------------------------')
            time.sleep(5)
            self.login()
            return self.get_video_play_auth(post)
        play_auth = resp.json().get('data').get('play_auth')
        return json.loads(base64.b64decode(play_auth))

    
    
