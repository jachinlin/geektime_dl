# coding=utf8
# TODO refactor this file

import os
import uuid
import requests
from jinja2 import Environment, FileSystemLoader

import re
templates_env = Environment(loader=FileSystemLoader('%s/templates/' % os.path.dirname(__file__)))


def _render_file(template_name, context, output_name, output_dir):
    template = templates_env.get_template(template_name)
    with open(os.path.join(output_dir, output_name), "w") as f:
        f.write(template.render(**context))


def render_toc_md(title, headers, output_dir):
    with open(os.path.join(output_dir, 'toc.md'), "w") as f:
        f.writelines([title] + headers)


def render_article_html(title, content, output_dir):
    _render_file('article.html', {'title': title, 'content': content}, '{}.html'.format(title), output_dir)


def format_file_name(name):
    return name.replace('/', '').replace(' ', '').replace('+', 'more').replace('"', '_')


def generate_cover_img(url, output_dir):
    try:
        r = requests.get(url)
        with open(os.path.join(output_dir, 'cover.jpg'), 'wb') as f:
            f.write(r.content)
    except:
        # todo logging
        pass


def parse_image(content, output_dir):

    # remove the xxx `style=xxx`
    p = r'img (.{1,15}=".*?") src=".*?"'
    fucking_styles = re.findall(p, content)
    for style in fucking_styles:
        content = content.replace(style, '')

    p = r'img\s+src="(.*?)"'
    img_url_list = re.findall(p, content)
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






