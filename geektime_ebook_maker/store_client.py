# coding=utf8
import sqlite3
import datetime
import os


class DbClient(object):
    def __init__(self, **kwargs):
        self._db_client = sqlite3.connect(kwargs.get('db_url') or os.path.join('.', 'sqlite3.db'))
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

    def execute(self, *args, **kwargs):

        cur = self._db_client.cursor()
        try:
            cur.execute(*args, **kwargs)
        except (sqlite3.IntegrityError, sqlite3.OperationalError) as e:
            print(e)
            pass
        self._db_client.commit()

        cur.close()


class StoreClient(object):
    def __init__(self, **kwargs):
        self._db_conn = DbClient()

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
