# coding=utf8

from geektime_dl.data_client import store_client

dc = store_client.DbClient()


def test_dc_execute():
    dc.execute('CREATE TABLE test_table (id INTEGER PRIMARY KEY,column_id INTEGER UNIQUE, column_type TEXT,column_title TEXT,column_subtitle TEXT,author_name TEXT,author_intro TEXT,had_sub INT,update_frequency TEXT,author_header TEXT,column_unit TEXT,column_cover TEXT,column_begin_time TEXT,column_intro TEXT,create_at TEXT NOT NULL )')


def test_dc_select():
    dc.select('SELECT * FROM posts WHERE column_id=? ORDER BY article_id', (11,))

