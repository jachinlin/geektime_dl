# coding=utf8

from geektime_dl.geektime_ebook import maker
import os


def test__render_article_html_output_dir_and_title():

    title = 'hello'
    content = '<p>hello world</p>'
    output_dir = '/tmp'
    os.system("mkdir -p %s" % output_dir)
    maker._render_article_html(title, content, output_dir)
    assert os.path.exists(os.path.join(output_dir, title+'.html'))


def test__render_article_html_content():

    title = 'hello'
    content = '<p>hello world</p>'
    output_dir = '/tmp'
    os.system("mkdir -p %s" % output_dir)
    maker._render_article_html(title, content, output_dir)
    filename = os.path.join(output_dir, title+'.html')

    with open(filename, 'r') as f:
        c = f.read()

    assert content in c
