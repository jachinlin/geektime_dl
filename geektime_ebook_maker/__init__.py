# coding=utf8

import os
import sys
import getopt
from multiprocessing import Pool
from kindle_maker import make_mobi
from .geektime_ebook.maker import render_column_source_files

from .spider import spider, geektime_tools


def make_column_ebook(column_id, column_title, output_dir):

    db_url = os.path.join(output_dir, 'sqlite3.db')

    # start spider
    start_url = 'https://time.geekbang.org/serv/v1/column/articles'
    json = {"cid": str(column_id), "size": 1000, "prev": 0, "order": "newest"}
    headers = {
        'Content-Type': 'application/json',
        'Referer': 'https://time.geekbang.org/column/{}'.format(column_id)
    }

    geektime_spider = spider.get_spider(backend_db_url=db_url, start_url=start_url, headers=headers, json=json)
    geektime_spider.add_url(url='https://time.geekbang.org/serv/v1/column/intro', headers=headers, json={'cid': str(column_id)})
    geektime_spider.start_crawl()

    # generate source files
    source_dir = os.path.join(output_dir, str(column_id))
    render_column_source_files(column_id, column_title, source_dir, source_db_path=db_url)

    # generate ebook
    make_mobi(source_dir=source_dir, output_dir=output_dir)


def make_book(column_id_list=None, output_dir=None):

    output_dir = output_dir or '.'
    column_id_list = column_id_list or geektime_tools.get_column_list()

    # make ebook
    pool = Pool()
    for column_id, column_tile in column_id_list:
        pool.apply_async(make_column_ebook, args=(column_id, column_tile, output_dir))
    pool.close()
    pool.join()


# -------------------------- command line script -------------------

def query():
    column_list = geektime_tools.get_column_list()

    print('column_id\tcolumn_title[status]')
    for c in column_list:
        print('%9s\t%s' % (c[0], c[1]))


def usage():
    print("""usage: geektime {query, ebook, usage} ...

positional arguments:
    {query ,make_mobi}
    query               query geektime columns info
    ebook               make mobi ebook with given column_id
    usage               see these usage message

short options:
      -u            account
      -p            password
      --area        area/country code
      -c            output directory of the ebook""")


def mobi(column_id, output_dir=None):

    status, msg = geektime_tools.valid_account()
    if not status:
        print('invalid account or password' + str(msg))
        return

    def _get(cid):
        infos = geektime_tools.get_column_list()
        for c in infos:
            if str(cid) == str(c[0]):
                return c
        else:
            print('invalid column id')

    column_id_title = _get(column_id)
    if column_id_title is None:
        return

    # check account

    make_book([column_id_title], output_dir)


def geektime():
    args = sys.argv[1:]

    if len(args) == 0 or args[0] not in ('query', 'usage', 'ebook'):
        return usage()

    options, _ = getopt.getopt(args[1:], "h?u:p:o:c:", ['area='])
    opt_dict = dict(options)
    account = opt_dict.get('-u')
    password = opt_dict.get('-p')
    output_dir = opt_dict.get('-o')
    column_id = opt_dict.get('-c')
    area_code = opt_dict.get('--area')

    os.environ["ACCOUNT"] = str(account)
    os.environ["PASSWORD"] = str(password)
    os.environ["AREA"] = str(area_code or '86')
    action = args[0]

    if action == 'query':
        return query()

    if action == 'usage':
        return usage()

    if action == 'ebook':

        return mobi(column_id, output_dir)


if __name__ == '__main__':
    make_book(column_id_list=geektime_tools.get_column_list())
