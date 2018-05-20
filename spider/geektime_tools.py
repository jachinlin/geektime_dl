# coding=utf8

import requests
import json
import os
import sqlite3
import datetime
import requests

account = 'put your register phone here'
password = 'password here'


class GeektimeData(object):
    def __init__(self, db_url):
        self._db_url = db_url
        os.system("%s -p %s" % ('mkdir', os.path.dirname(self._db_url)))

    @staticmethod
    def _get_cookies():
        url = 'https://account.geekbang.org/account/ticket/login'

        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Content-Type': 'application/json',
            'Host': 'account.geekbang.org',
            'Referer': 'https://account.geekbang.org/signin?redirect=https%3A%2F%2Fwww.geekbang.org%2F',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:59.0) Gecko/20100101 Firefox/59.0'
        }

        data = {
            "country": 86,
            "cellphone": os.getenv('ACCOUNT') or account,
            "password": os.getenv('PASSWORD') or password,
            "captcha": "",
            "remember": 1,
            "platform": 3,
            "appid": 1
        }

        resp = requests.post(url, headers=headers, json=data)

        assert resp.status_code == 200 and resp.json().get('code') == 0, 'login fail:' + resp.json()['error']['msg']

        return dict(resp.cookies.items())

    def _save_cookies_2_db(self, cookies):
        conn = sqlite3.connect(self._db_url)

        cur = conn.cursor()
        try:
            cur.execute(
                'CREATE TABLE cookies (id INTEGER PRIMARY KEY, cookies TEXT NOT NULL, create_at TEXT NOT NULL )')
        except sqlite3.OperationalError:  # exist
            pass

        cur.execute('INSERT INTO cookies (cookies, create_at) VALUES (?, ?)',
                    (json.dumps(cookies), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        cur.close()
        conn.commit()
        conn.close()

    def _get_cookies_from_db(self):

        conn = sqlite3.connect(self._db_url)

        cur = conn.cursor()
        value = None

        try:
            cur.execute('SELECT cookies FROM cookies ORDER BY create_at DESC LIMIT 1')
            value = cur.fetchone()
        except sqlite3.OperationalError:  # not exist
            pass
        finally:
            cur.close()
            conn.close()

        if value is None:
            return

        return json.loads(value[0])

    def get_cookies(self):
        cookies = self._get_cookies_from_db()
        if cookies is None:
            cookies = self._get_cookies()
            self._save_cookies_2_db(cookies)

        return cookies

    def save_column_info(self, column_id, column_title, column_subtitle, author_name, author_intro,
                         had_sub, update_frequency, author_header, column_unit, column_cover, column_begin_time):
        conn = sqlite3.connect(self._db_url)

        cur = conn.cursor()
        try:
            cur.execute('CREATE TABLE columns ('
                        'id INTEGER PRIMARY KEY,'
                        'column_id INTEGER, '
                        'column_title TEXT,'
                        'column_subtitle TEXT,'
                        'author_name TEXT,'
                        'author_intro TEXT,'
                        'had_sub INT,'
                        'update_frequency TEXT,'
                        'author_header TEXT,'
                        'column_unit TEXT,'
                        'column_cover TEXT,'
                        'column_begin_time TEXT,'
                        'create_at TEXT NOT NULL )'
                        )
        except sqlite3.OperationalError:  # exist
            pass

        cur.execute(
            'INSERT INTO columns (column_id, column_title, column_subtitle, author_name, author_intro, had_sub, '
            'update_frequency, author_header, column_unit, column_cover, column_begin_time, create_at) '
            'VALUES (?, ?,?,?, ?,?,?, ?,?,?, ?,?)',
            (column_id, column_title, column_subtitle, author_name, author_intro,
             had_sub, update_frequency, author_header, column_unit, column_cover, column_begin_time,
             datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        cur.close()
        conn.commit()
        conn.close()

    def save_article_info(self, column_id, article_id, article_title, article_subtitle, article_ctime,
                          article_cover, article_summary):
        conn = sqlite3.connect(self._db_url)

        cur = conn.cursor()
        try:
            cur.execute('CREATE TABLE articles ('
                        'id INTEGER PRIMARY KEY,'
                        'column_id INTEGER, '
                        'article_id INTEGER,'
                        'article_title TEXT,'
                        'article_subtitle TEXT,'
                        'article_ctime TEXT,'
                        'article_cover TEXT,'
                        'article_summary TEXT,'
                        'create_at TEXT NOT NULL )'
                        )
        except sqlite3.OperationalError:  # exist
            pass

        cur.execute('INSERT INTO articles (column_id, article_id, article_title, article_subtitle, article_ctime, '
                    'article_cover, article_summary, create_at) '
                    'VALUES (?, ?, ?,?, ?, ?, ?, ?)',
                    (column_id, article_id, article_title, article_subtitle, article_ctime,
                     article_cover, article_summary, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        cur.close()
        conn.commit()
        conn.close()

    def save_article_detail(self, article_content, column_id, article_id, article_title, article_subtitle,
                            article_ctime,
                            article_cover, article_summary, audio_download_url, audio_url, audio_time, author_name,
                            column_cover, article_poster_wxlite):
        conn = sqlite3.connect(self._db_url)

        cur = conn.cursor()
        try:
            cur.execute('CREATE TABLE article_details ('
                        'id INTEGER PRIMARY KEY,'
                        'article_content TEXT,'
                        'column_id INTEGER, '
                        'article_id INTEGER,'
                        'article_title TEXT,'
                        'article_subtitle TEXT,'
                        'article_ctime TEXT,'
                        'article_cover TEXT,'
                        'article_summary TEXT,'
                        'audio_download_url TEXT,'
                        'audio_url TEXT,'
                        'audio_time TEXT,'
                        'author_name TEXT,'
                        'column_cover TEXT,'
                        'article_poster_wxlite TEXT,'

                        'create_at TEXT NOT NULL )'
                        )
        except sqlite3.OperationalError:  # exist
            pass

        cur.execute('INSERT INTO article_details (article_content, column_id, article_id, article_title, '
                    'article_subtitle, article_ctime, article_cover, article_summary, audio_download_url, '
                    'audio_url, audio_time, author_name, column_cover, article_poster_wxlite, create_at) '
                    'VALUES (?, ?, ?,?, ?, ?, ?, ?,?,?,?,?,?,?,?)',
                    (article_content, column_id, article_id, article_title, article_subtitle, article_ctime,
                     article_cover, article_summary, audio_download_url, audio_url, audio_time, author_name,
                     column_cover,
                     article_poster_wxlite, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        cur.close()
        conn.commit()
        conn.close()


def get_column_list():
    url = 'https://time.geekbang.org/serv/v1/column/all'
    headers = {
        'Referer': 'https://time.geekbang.org/paid-content',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:59.0) Gecko/20100101 Firefox/59.0'
    }

    try:
        cookies = GeektimeData._get_cookies()
    except:
        cookies = None
    r = requests.get(url, headers=headers, cookies=cookies)

    content = r.json()['data']['1']['list']
    column_list = []

    def _title(c):
        if not c[2]:
            title = c[1] + '[免费试读]'
        elif c[3] == '更新完毕':
            title = c[1] + '[更新完毕]'
        else:
            title = c[1] + '[未完待续]'
        return title

    for column in content:
        c = (column.get('id'), column.get('column_title'), column.get('had_sub'), column.get('update_frequency'))
        column_list.append((c[0], _title(c)))

    return column_list


