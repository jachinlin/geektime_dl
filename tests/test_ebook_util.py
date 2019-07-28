# coding=utf8

import os

from geektime_dl.utils.ebook import Render


def test_render_article_html(render: Render, output_folder: str):

    title = 'hello'
    content = '<p>hello world</p>'
    render.render_article_html(title, content)
    fn = os.path.join(output_folder, title+'.html')

    assert os.path.isfile(fn)
    with open(fn) as f:
        assert content in f.read()

    os.remove(fn)


def test_render_toc_md(render: Render, output_folder: str):
    title = 'hello'
    headers = ['标题1', '标题2']
    render.render_toc_md(title, headers)
    fn = os.path.join(output_folder, 'toc.md')

    assert os.path.isfile(fn)
    with open(fn) as f:
        ls = f.readlines()
        assert len(ls) == 3
        assert ls[0].rstrip('\n') == title
        assert ls[1].rstrip('\n') == '# {}'.format(headers[0])
        assert ls[2].rstrip('\n') == '# {}'.format(headers[1])

    os.remove(fn)


def test_format_path(render: Render):
    fn = 'hell\\'
    formated_fn = render.format_file_name(fn)
    assert formated_fn == 'hell'
