# coding=utf8

import os
import sqlite3
from jinja2 import Environment, FileSystemLoader

templates_env = Environment(loader=FileSystemLoader('%s/templates/' % os.path.dirname(__file__)))
_output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../output/ebook_source')

db_url = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../spider/output/sqlite3.db')


def render_file(template_name, context, output_name, output_dir):
    template = templates_env.get_template(template_name)
    with open(os.path.join(output_dir, output_name), "w") as f:
        f.write(template.render(**context))


def render_toc_md(title, headers,  output_dir):
    with open(os.path.join(output_dir, 'toc.md'), "w") as f:
        f.writelines([title] + headers)


def render_article_html(title, content, output_dir):
    render_file('article.html', {'title': title, 'content': content}, '{}.html'.format(title), output_dir)


def format_file_name(name):
    return name.replace('/', '').replace(' ', '')


def render_column_source_files(column_id, column_title, output_dir):
    os.system("rm -rf {}".format(output_dir))
    os.system("mkdir -p {}".format(output_dir))
    conn = sqlite3.connect(db_url)

    cur = conn.cursor()
    column_id = column_id
    cur.execute('SELECT article_id, article_title FROM articles WHERE column_id=? ORDER BY article_id', (column_id,))

    articles = cur.fetchall()
    render_toc_md(column_title+'\n', ['# ' + format_file_name(t[1]) + '\n' for t in articles], output_dir)
    for article in articles:
        cur.execute('SELECT article_content FROM article_details WHERE article_id=?', (article[0],))
        content = cur.fetchone()[0]
        title = format_file_name(article[1])
        render_article_html(title, content, output_dir)

    cur.close()
    conn.close()


def render_all_source_files():
    conn = sqlite3.connect(db_url)

    cur = conn.cursor()
    cur.execute('SELECT column_id, column_title FROM columns ORDER BY column_id')

    columns = cur.fetchall()
    cur.close()
    conn.close()

    for column_id, column_title in columns:
        output_dir = os.path.join(_output_dir, str(column_id))

        render_column_source_files(column_id, column_title, output_dir)





