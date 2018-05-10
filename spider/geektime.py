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


def parse(url, html_content):
    new_url_list = []
    parsed_content = None

    # 专栏列表
    if url.endswith('/column/all'):
        column_list = json.loads(html_content)['data']['1']['list']
        parsed_content = json.dumps(column_list)

        for column in column_list:
            new_url_list.append((
                'https://time.geekbang.org/serv/v1/column/articles',
                {
                    'json': {"cid": str(column['id']), "size": 1000, "prev": 0, "order": "newest"},
                    'cookies': get_cookies(),
                    'headers': {
                        'Content-Type': 'application/json',
                        'Referer': 'https://time.geekbang.org/column/{}'.format(column['id'])
                    }
                }
            ))

    return new_url_list, parsed_content


def save(url, content):
    pass

# system("%s -rf %s" % ('rm', output_dir))
