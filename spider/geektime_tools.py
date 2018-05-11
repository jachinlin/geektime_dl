# coding=utf8

import requests
import json
import os
import sqlite3
import datetime

account = 'put your register phone here'
password = 'password here'

output_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'output')


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

    assert resp.status_code == 200 and resp.json().get('code') == 0, 'login fail:' + resp.json()['error']['msg'].encode(
        'utf-8')

    return dict(resp.cookies.items())


def _save_cookies_2_db(cookies):
    conn = sqlite3.connect(os.path.join(output_dir, 'sqlite3.db'))

    cur = conn.cursor()
    try:
        cur.execute('CREATE TABLE cookies (id INTEGER PRIMARY KEY, cookies TEXT NOT NULL, create_at TEXT NOT NULL )')
    except sqlite3.OperationalError:  # exist
        pass

    cur.execute('INSERT INTO cookies (cookies, create_at) VALUES (?, ?)',
                (json.dumps(cookies), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    cur.close()
    conn.commit()
    conn.close()


def _get_cookies_from_db():
    os.system("%s -p %s" % ('mkdir', output_dir))
    conn = sqlite3.connect(os.path.join(output_dir, 'sqlite3.db'))

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


def get_cookies():
    cookies = _get_cookies_from_db()
    if cookies is None:
        cookies = _get_cookies()
        _save_cookies_2_db(cookies)

    return cookies


def save_column_info(column_id, column_title, column_subtitle, author_name, author_intro,
                     had_sub, update_frequency, author_header, column_unit, column_cover, column_begin_time):
    conn = sqlite3.connect(os.path.join(output_dir, 'sqlite3.db'))

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

    cur.execute('INSERT INTO columns (column_id, column_title, column_subtitle, author_name, author_intro, had_sub, '
                'update_frequency, author_header, column_unit, column_cover, column_begin_time, create_at) '
                'VALUES (?, ?,?,?, ?,?,?, ?,?,?, ?,?)',
                (column_id, column_title, column_subtitle, author_name, author_intro,
                 had_sub, update_frequency, author_header, column_unit, column_cover, column_begin_time,
                 datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    cur.close()
    conn.commit()
    conn.close()


def save_article_info(column_id, article_id, article_title, article_subtitle, article_ctime,
                      article_cover, article_summary):
    conn = sqlite3.connect(os.path.join(output_dir, 'sqlite3.db'))

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


def save_article_detail(article_content, column_id, article_id, article_title, article_subtitle, article_ctime,
                        article_cover, article_summary, audio_download_url, audio_url, audio_time, author_name,
                        column_cover, article_poster_wxlite):
    conn = sqlite3.connect(os.path.join(output_dir, 'sqlite3.db'))

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

    cur.execute('INSERT INTO article_details (article_content, column_id, article_id, article_title, article_subtitle, '
                'article_ctime, article_cover, article_summary, audio_download_url, audio_url, audio_time,'
                'author_name, column_cover, article_poster_wxlite, create_at) '
                'VALUES (?, ?, ?,?, ?, ?, ?, ?,?,?,?,?,?,?,?)',
                (article_content, column_id, article_id, article_title, article_subtitle, article_ctime,
                 article_cover, article_summary, audio_download_url, audio_url, audio_time, author_name, column_cover,
                 article_poster_wxlite, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    cur.close()
    conn.commit()
    conn.close()


