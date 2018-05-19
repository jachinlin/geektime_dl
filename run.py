
import os
import time
from multiprocessing import Pool
import sqlite3
from kindle_maker import make_mobi
from geektime_ebook.maker import render_all_source_files
from spider import spider as geektime_spider


_db_url = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output/sqlite3.db')
_source_base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output/ebook_source')
_output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output/ebook')


def _make_column_to_ebook(source_dir, output_dir):
    """

    :param source_dir: source_dir of column
    :param output_dir: output_dir of ebook
    :return:
    """

    make_mobi.make_ebook(source_dir=source_dir, output_dir=output_dir)


def make_book(db_url, source_base_dir, output_dir):

    # get columns info from sqlite db of db_url
    conn = sqlite3.connect(db_url)
    cur = conn.cursor()
    cur.execute('SELECT column_id, column_title FROM columns ORDER BY column_id')
    columns = cur.fetchall()
    cur.close()
    conn.close()

    # make ebook
    pool = Pool()
    for column_id, column_title in columns:
        source_dir = os.path.join(source_base_dir, str(column_id))
        pool.apply_async(_make_column_to_ebook, args=(source_dir, output_dir))
    pool.close()
    pool.join()


start = time.time()

# start spider
geektime_spider.start_crawl()
print('spider time cost is %s' % (time.time() - start))

# render all source files
render_all_source_files(_db_url, _source_base_dir)

# make book
make_book(_db_url, _source_base_dir, _output_dir)
print('book maker cost time: ' + str(time.time() - start))



