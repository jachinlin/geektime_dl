# coding=utf8
import sqlite3
import datetime
import os
import traceback
from geektime_dl.utils._logging import logger
from geektime_dl.utils import Singleton
from geektime_dl.utils import debug_log


class DbClient(object):
    def __init__(self, **kwargs):
        self._db_client = sqlite3.connect(kwargs.get('db_url') or os.path.join('.', 'sqlite3.db'))
        self._db_client.row_factory = sqlite3.Row
        self._init_tables()

    def _init_tables(self):

        self.execute(
            'CREATE TABLE columns ('
                     'id INTEGER PRIMARY KEY,'
                     'column_id INTEGER UNIQUE, '
                     'column_type TEXT,'
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
                     'column_intro TEXT,'
                     'create_at TEXT NOT NULL '
            ')'
        )

        self.execute(
            'CREATE TABLE posts ('
                'id INTEGER PRIMARY KEY,'
                'article_content TEXT,'
                'column_id INTEGER, '
                'article_id INTEGER UNIQUE,'
                'article_title TEXT,'
                'article_subtitle TEXT,'
                'article_ctime TEXT,'
                'article_cover TEXT,'
                'video_cover TEXT,'
                'video_media TEXT,'
                'article_summary TEXT,'
                'audio_download_url TEXT,'
                'audio_url TEXT,'
                'audio_time TEXT,'
                'author_name TEXT,'
                'article_poster_wxlite TEXT,'
                'create_at TEXT NOT NULL '
            ')'
        )

        self.execute(
            'CREATE TABLE comments ('
                'id INTEGER PRIMARY KEY,'
                'user_name TEXT,'
                'like_count INTEGER, '
                'comment_id INTEGER UNIQUE,'
                'article_id INTEGER, '
                'comment_content TEXT,'
                'comment_ctime TEXT,'
                'replies TEXT,'
                'create_at TEXT NOT NULL '
            ')'
        )

    def execute(self, *args, **kwargs):

        cur = self._db_client.cursor()
        try:
            cur.execute(*args, **kwargs)
        except sqlite3.OperationalError:
            pass
        except sqlite3.IntegrityError:
            logger.warn('exception=%s' % traceback.format_exc())

        self._db_client.commit()

        cur.close()

    def select(self, *args, **kwargs):

        cur = self._db_client.cursor()
        cur.execute(*args, **kwargs)
        result = cur.fetchall()
        data = [dict(zip(row.keys(), row)) for row in result]
        cur.close()
        return data


class StoreClient(metaclass=Singleton):
    def __init__(self, **kwargs):
        self._db_conn = DbClient()

    @debug_log
    def save_column_info(self, **kwargs):
        self._db_conn.execute(
            'INSERT INTO columns ('
                'column_id, column_type, column_title, column_subtitle, author_name, author_intro, had_sub, '
                'update_frequency, author_header, column_unit, column_cover, column_begin_time, column_intro, create_at'
            ')'
            'VALUES (?, ?,?,?, ?,?,?, ?,?,?, ?,?,?, ?)', (
                kwargs['id'], kwargs['column_type'], kwargs['column_title'], kwargs['column_subtitle'], kwargs['author_name'],
                kwargs['author_intro'], kwargs['had_sub'], kwargs['update_frequency'], kwargs['author_header'],
                kwargs['column_unit'], kwargs['column_cover'], kwargs['column_begin_time'], kwargs['column_intro'],
                datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
        )

    @debug_log
    def save_post_content(self, **kwargs):

        self._db_conn.execute(
            'INSERT INTO posts (article_content, column_id, article_id, article_title, '
                'article_subtitle, article_ctime, article_cover, article_summary, audio_download_url, '
                'video_cover, video_media, '
                'audio_url, audio_time, author_name, article_poster_wxlite, create_at) '
            'VALUES (?, ?, ?,?, ?,?, ?, ?,?, ?,?,?,?,?,?,?)', (
                kwargs['article_content'], kwargs['column_id'], kwargs['id'], kwargs['article_title'],
                kwargs['article_subtitle'], kwargs['article_ctime'], kwargs['article_cover'],  kwargs['article_summary'],
                kwargs['audio_download_url'], kwargs['video_cover'],
                kwargs.get('video_media'), kwargs['audio_url'], kwargs['audio_time'], kwargs['author_name'],
                kwargs['article_poster_wxlite'], datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
        )

    @debug_log
    def save_post_comment(self, **kwargs):

        self._db_conn.execute(
            'INSERT INTO comments (user_name, like_count, comment_id, article_id, '
                'comment_content, comment_ctime, replies, create_at) '
            'VALUES (?, ?, ?,?, ?,?, ?, ?)', (
                kwargs['user_name'], kwargs['like_count'], kwargs['id'], kwargs['article_id'],
                kwargs['comment_content'], kwargs['comment_ctime'], kwargs.get('replies', []),
                datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
        )

    @debug_log
    def get_course_content(self, course_id):
        data = self._db_conn.select(
            'SELECT * FROM posts WHERE column_id=? ORDER BY article_id', (int(course_id),)
        )
        return data

    @debug_log
    def get_course_intro(self, course_id):
        data = self._db_conn.select(
            'SELECT * FROM columns WHERE column_id=? ORDER BY create_at DESC LIMIT 1', (int(course_id),)
        )

        return data[0] if data else {}

    @debug_log
    def get_post_content(self, post_id):
        data = self._db_conn.select(
            'SELECT * FROM posts WHERE article_id=? LIMIT 1', (int(post_id),)
        )

        return data[0] if data else {}

    @debug_log
    def get_post_comments(self, post_id):
        data = self._db_conn.select(
            'SELECT * FROM comments WHERE article_id=? ORDER BY like_count DESC', (int(post_id),)
        )

        return data
