# coding=utf8

import json

from .mini_spider import Spider
from .geektime_tools import GeektimeData


def get_spider(backend_db_url, start_url=None, **kwargs):
    geektime_data = GeektimeData(backend_db_url)

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
                        'cookies': geektime_data.get_cookies(),
                        'headers': {
                            'Content-Type': 'application/json',
                            'Referer': 'https://time.geekbang.org/column/{}'.format(column['id'])
                        }
                    }
                ))

        # 专栏信息
        if url.endswith('/column/intro'):
            column_intro = json.loads(html_content)
            parsed_content = json.dumps(column_intro['data'])

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
                        'cookies': geektime_data.get_cookies(),
                        'headers': {
                            'Content-Type': 'application/json',
                            'Referer': 'https://time.geekbang.org/column/article/{}'.format(article['id'])
                        }
                    }
                ))
        # 文章详情
        if url.endswith('/serv/v1/article'):
            article_detail = json.loads(html_content)
            parsed_content = json.dumps(article_detail['data'])

        return new_url_list, parsed_content

    def save(url, request_params, content):

        # 专栏信息
        if url.endswith('/column/intro'):
            intro = json.loads(content)
            cid = request_params['json']['cid']
            geektime_data.save_column_info(
                column_id=cid,
                column_title=intro.get('column_title'),
                column_subtitle=intro.get('column_subtitle'),
                author_name=intro.get('author_name'),
                author_intro=intro.get('author_intro'),
                had_sub=intro.get('had_sub'),
                update_frequency=intro.get('update_frequency'),
                author_header=intro.get('author_header'),
                column_unit=intro.get('column_unit'),
                column_cover=intro.get('column_cover'),
                column_begin_time=intro.get('column_begin_time'),
                column_intro=intro['column_intro']
            )

        # save 专栏文章
        if url.endswith('/column/articles'):
            column_id = json.loads(content)['column_id']
            article_list = json.loads(content)['article_list']
            for article in article_list:
                geektime_data.save_article_info(
                    column_id=column_id,
                    article_subtitle=article.get('article_subtitle'),
                    article_ctime=article.get('article_ctime'),
                    article_id=article.get('id'),
                    article_cover=article.get('article_cover'),
                    article_title=article.get('article_title'),
                    article_summary=article.get('article_summary'),
                )

        if url.endswith('/serv/v1/article'):
            detail = json.loads(content)
            geektime_data.save_article_detail(
                article_content=detail['article_content'],
                article_subtitle=detail['article_subtitle'],
                audio_download_url=detail['audio_download_url'],
                audio_time=detail['audio_time'],
                author_name=detail['author_name'],
                article_ctime=detail['article_ctime'],
                article_id=detail['id'],
                article_cover=detail['article_cover'],
                audio_url=detail['audio_url'],
                column_cover=detail.get('column_cover'),
                article_title=detail['article_title'],
                column_id=detail.get('column_id'),
                article_summary=detail['article_summary'],
                article_poster_wxlite=detail['article_poster_wxlite'],
            )

    start_url = start_url or 'https://time.geekbang.org/serv/v1/column/all'
    headers = kwargs.get('headers') or {
        'Referer': 'https://time.geekbang.org/paid-content',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:59.0) Gecko/20100101 Firefox/59.0'
    }
    spider = Spider(parse_func=parse, save_func=save)
    spider.set_start_url(start_url, method='post', headers=headers, json=kwargs.get('json'), cookies=geektime_data.get_cookies())

    return spider



