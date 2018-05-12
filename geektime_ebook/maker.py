# coding=utf8

import os
import sqlite3
from jinja2 import Environment, FileSystemLoader

templates_env = Environment(loader=FileSystemLoader('%s/templates/' % os.path.dirname(__file__)))
_output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../output/ebook')

db_url = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../spider/output/sqlite3.db')


def render_file(template_name, context, output_name, output_dir):
    template = templates_env.get_template(template_name)
    with open(os.path.join(output_dir, output_name), "w") as f:
        f.write(template.render(**context))


def render_article_html(title, content, output_dir):
    render_file('article.html', {'title': title, 'content': content}, '{}.html'.format(title), output_dir)


def format_file_name(name):
    return name.replace('/', '').replace(' ', '')


def test():
    os.system("rm -rf {}".format(_output_dir))
    os.system("mkdir -p {}".format(_output_dir))
    conn = sqlite3.connect(db_url)

    cur = conn.cursor()
    column_id = 49
    print('朱赟的技术管理课')
    cur.execute('select article_id from articles where column_id=?', (column_id,))

    id_list = cur.fetchall()
    for article_id in id_list:
        cur.execute('select article_title, article_content from article_details where article_id=?', (article_id[0],))
        title, content = cur.fetchone()
        title = format_file_name(title)
        render_article_html(title, content, _output_dir)
        print('# ' + title)
    cur.close()
    conn.close()



