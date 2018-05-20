import os
from multiprocessing import Pool
from kindle_maker import make_mobi
from geektime_ebook.maker import render_column_source_files

from spider import spider, geektime_tools


def make_column_ebook(column_id, column_title, output_dir, db_url):

    # start spider
    start_url = 'https://time.geekbang.org/serv/v1/column/articles'
    json = {"cid": str(column_id), "size": 1000, "prev": 0, "order": "newest"}
    headers = {
        'Content-Type': 'application/json',
        'Referer': 'https://time.geekbang.org/column/{}'.format(column_id)
    }

    geektime_spider = spider.get_spider(backend_db_url=db_url, start_url=start_url, headers=headers, json=json)
    geektime_spider.start_crawl()

    # generate source files
    source_dir = os.path.join(output_dir, str(column_id))
    render_column_source_files(column_id, column_title, source_dir, source_db_path=db_url)

    # generate ebook
    make_mobi(source_dir=source_dir, output_dir=output_dir)


def make_book(db_url=None, column_id_list=None, output_dir=None):

    db_url = db_url or './sqlite3.db'
    output_dir = output_dir or '.'

    column_id_list = column_id_list or [(42, '123'), (48, '345')]

    # make ebook
    pool = Pool()
    for column_id, column_tile in column_id_list:
        pool.apply_async(make_column_ebook, args=(column_id, column_tile, output_dir, db_url))
    pool.close()
    pool.join()


def query():
    column_list = geektime_tools.get_column_list()

    print('column_id\tcolumn_title[status]')
    for c in column_list:
        print('%9s\t%s' % (c[0], c[1]))


make_book(column_id_list=geektime_tools.get_column_list())
