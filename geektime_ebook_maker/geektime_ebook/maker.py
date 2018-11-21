# coding=utf8

import os
import uuid
import sqlite3
import requests
from jinja2 import Environment, FileSystemLoader

import re
templates_env = Environment(loader=FileSystemLoader('%s/templates/' % os.path.dirname(__file__)))


def _render_file(template_name, context, output_name, output_dir):
    template = templates_env.get_template(template_name)
    with open(os.path.join(output_dir, output_name), "w") as f:
        f.write(template.render(**context))


def _render_toc_md(title, headers,  output_dir):
    with open(os.path.join(output_dir, 'toc.md'), "w") as f:
        f.writelines([title] + headers)


def _render_article_html(title, content, output_dir):
    _render_file('article.html', {'title': title, 'content': content}, '{}.html'.format(title), output_dir)


def _format_file_name(name):
    return name.replace('/', '').replace(' ', '').replace('+', 'more').replace('"', '_')


def _generate_cover_img(url, output_dir):
    try:
        r = requests.get(url)
        with open(os.path.join(output_dir, 'cover.jpg'), 'wb') as f:
            f.write(r.content)
    except:
        # todo logging
        pass


def _parse_image(content, output_dir):

    p = r'img src="(.*?)"'
    img_url_list = re.findall(p, content, re.S)
    for url in img_url_list:
        try:
            url_local = str(uuid.uuid4()) + '.jpg'
            r = requests.get(url)
            with open(os.path.join(output_dir, url_local), 'wb') as f:
                f.write(r.content)
            content = content.replace(url, url_local)
        except:
            # todo logging
            pass
    return content


def render_column_source_files(column_id, column_title, output_dir, source_db_path):
    """
    render all source files of `column_id`, and put the source files to `output_dir`
    source data are stored in `source_path` sqlite3 db
    :param column_id: column id
    :param column_title: column title
    :param output_dir:  output directory of the source files
    :param source_db_path: db url
    :return:
    """
    os.system("rm -rf {}".format(output_dir))
    os.system("mkdir -p {}".format(output_dir))
    conn = sqlite3.connect(source_db_path)

    cur = conn.cursor()
    column_id = column_id

    # cover and introduction
    cur.execute('SELECT column_cover, column_intro FROM columns WHERE column_id=? LIMIT 1', (column_id,))
    column_info = cur.fetchone()
    _render_article_html('简介', _parse_image(column_info[1], output_dir), output_dir)
    _generate_cover_img(column_info[0], output_dir)

    cur.execute('SELECT article_id, article_title FROM articles WHERE column_id=? ORDER BY article_id', (column_id,))

    articles = cur.fetchall()
    _render_toc_md(column_title+'\n', ['# 简介\n'] + ['# ' + _format_file_name(t[1]) + '\n' for t in articles], output_dir)
    for article in articles:
        cur.execute('SELECT article_content FROM article_details WHERE article_id=?', (article[0],))
        content = cur.fetchone()[0]
        title = _format_file_name(article[1])
        _render_article_html(title, _parse_image(content, output_dir), output_dir)

    cur.close()
    conn.close()


def render_all_source_files(source_db_path, output_dir):
    """

    :param source_db_path: sqlite db url
    :param output_dir: output directory of the source files
    :return:
    """

    # get all column info from sqlite3.db `source_path`
    conn = sqlite3.connect(source_db_path)
    cur = conn.cursor()
    cur.execute('SELECT column_id, column_title, had_sub, update_frequency FROM columns ORDER BY column_id')
    columns = cur.fetchall()
    cur.close()
    conn.close()

    # format column title
    def _title(c):
        if not c[2]:
            title = c[1] + '[免费试读]'
        elif c[3] == '更新完毕':
            title = c[1] + '[更新完毕]'
        else:
            title = c[1] + '[未完待续]'
        return title
    columns = [(c[0], _title(c)) for c in columns]

    # for each column, render source files which are needed to make ebook
    for column_id, column_title in columns:
        _output_dir = os.path.join(output_dir, str(column_id))

        render_column_source_files(column_id, column_title, _output_dir, source_db_path)





