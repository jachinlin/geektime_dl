# coding=utf8

import json

from .base_spider import Spider
from . import geektime_tools


def parse(url, request_params, html_content):
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
                    'method': 'post',
                    'json': {"cid": str(column['id']), "size": 1000, "prev": 0, "order": "newest"},
                    'cookies': geektime_tools.get_cookies(),
                    'headers': {
                        'Content-Type': 'application/json',
                        'Referer': 'https://time.geekbang.org/column/{}'.format(column['id'])
                    }
                }
            ))

    # 专栏文章
    if url.endswith('/column/articles'):
        column_id = request_params['json']['cid']
        article_list = json.loads(html_content)['data']['list']
        parsed_content = json.dumps({'column_id': column_id, 'article_list': article_list})

        for article in article_list:
            new_url_list.append((
                'https://time.geekbang.org/serv/v1/article',
                {
                    'method': 'post',
                    'json': {'id': str(article['id'])},
                    'cookies': geektime_tools.get_cookies(),
                    'headers': {
                        'Content-Type': 'application/json',
                        'Referer': 'https://time.geekbang.org/column/article/{}'.format(article['id'])
                    }
                }
            ))

    return new_url_list, parsed_content


def save(url, request_params, content):
    # 专栏列表
    if url.endswith('/column/all'):
        column_list = json.loads(content)
        for column in column_list:
            geektime_tools.save_column_info(
                column_id=column.get('id'),
                column_title=column.get('column_title'),
                column_subtitle=column.get('column_subtitle'),
                author_name=column.get('author_name'),
                author_intro=column.get('author_intro'),
                had_sub=column.get('had_sub'),
                update_frequency=column.get('update_frequency'),
                author_header=column.get('author_header'),
                column_unit=column.get('column_unit'),
                column_cover=column.get('column_cover'),
                column_begin_time=column.get('column_begin_time'),
            )
    # save 专栏文章
    if url.endswith('/column/articles'):
        column_id = json.loads(content)['column_id']
        article_list = json.loads(content)['article_list']
        for article in article_list:
            geektime_tools.save_article_info(
                column_id=column_id,
                article_subtitle=article.get('article_subtitle'),
                article_ctime=article.get('article_ctime'),
                article_id=article.get('id'),
                article_cover=article.get('article_cover'),
                article_title=article.get('article_title'),
                article_summary=article.get('article_summary'),
            )


start_url = 'https://time.geekbang.org/serv/v1/column/all'
headers = {
    'Referer': 'https://time.geekbang.org/paid-content',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:59.0) Gecko/20100101 Firefox/59.0'
}
spider = Spider(parse_func=parse, save_func=save)
spider.set_start_url(start_url, method='post', headers=headers, cookies=geektime_tools.get_cookies())
