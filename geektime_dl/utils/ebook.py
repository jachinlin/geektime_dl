# coding=utf8

import os
import uuid
import re
import contextlib

import requests
from jinja2 import Environment, FileSystemLoader


class Render:

    def __init__(self, output_folder: str):

        self._output_folder = output_folder
        self._jinja_env = Environment(loader=FileSystemLoader(
            '{}/templates/'.format(os.path.dirname(__file__))
        ))

    def _render_file(self, template_name: str, context: dict, filename: str) -> None:
        """
        生成 html 文件
        """
        template = self._jinja_env.get_template(template_name)
        with open(os.path.join(self._output_folder, filename), "w") as f:
            f.write(template.render(**context))

    def render_toc_md(self, title: str, headers: list) -> None:
        """
        生成目录文件 toc.mc
        """
        with open(os.path.join(self._output_folder, 'toc.md'), "w") as f:
            headers = ['# {}'.format(h) for h in headers]
            f.writelines('\n'.join([title] + headers))


    def render_article_html(self, title: str, content: str) -> None:
        """
        生成 html 文件
        """
        content = self._parse_image(content)
        self._render_file(
            'article.html',
            {'title': title, 'content': content},
            '{}.html'.format(title)
        )

    def generate_cover_img(self, url: str) -> None:
        """
        下载 url 作为封面
        """
        with contextlib.suppress(Exception):
            r = requests.get(url, timeout=20)
            with open(os.path.join(self._output_folder, 'cover.jpg'), 'wb') as f:
                f.write(r.content)

    def _parse_image(self, content: str) -> str:
        """
        下载 content(html text) 中的 image
        """
        # remove the xxx `style=xxx`
        p = r'img (.{1,15}=".*?") src=".*?"'
        fucking_styles = re.findall(p, content)
        for style in fucking_styles:
            content = content.replace(style, '')

        p = r'img\s+src="(.*?)"'
        img_url_list = re.findall(p, content)
        for url in img_url_list:
            with contextlib.suppress(Exception):
                url_local = str(uuid.uuid4()) + '.jpg'
                r = requests.get(url, timeout=20)
                with open(os.path.join(self._output_folder, url_local), 'wb') as f:
                    f.write(r.content)
                content = content.replace(url, url_local)

        return content

    @staticmethod
    def format_file_name(path: str) -> str:
        """
        去掉path中的不规则字符
        """
        return path.replace('/', '').replace(' ', '').\
            replace('+', '-').replace('"', '').replace('\\', '').\
            replace(':', '-').replace('|', '-')








