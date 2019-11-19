# coding=utf8

import os
import re
import time
import contextlib
import pathlib
from urllib.parse import urlparse
import io

import requests
from jinja2 import Environment, FileSystemLoader
from PIL import Image


class Render:

    def __init__(self, output_folder: str):

        self._output_folder = output_folder
        self._jinja_env = Environment(loader=FileSystemLoader(
            '{}/templates/'.format(os.path.dirname(__file__))
        ))

    def _render_file(
            self, template_name: str, context: dict, filename: str) -> None:
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

    def render_article_html(self, title: str, content: str, **kwargs) -> None:
        """
        生成 html 文件
        """
        content = self._parse_image(content, **kwargs)
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
            cover = os.path.join(self._output_folder, 'cover.jpg')
            with open(cover, 'wb') as f:
                f.write(r.content)

    def _parse_image(self, content: str, **kwargs) -> str:
        """
        下载 content(html text) 中的 image
        """
        # remove the xxx `style=xxx`
        p = r'img (.{1,15}=".*?") src=".*?"'
        fucking_styles = re.findall(p, content)
        for style in fucking_styles:
            content = content.replace(style, '')

        p = r'</?img>'
        empty_imgs = re.findall(p, content)
        for empty_img in empty_imgs:
            content = content.replace(empty_img, '')

        p = r'img\s+src="(.*?)"'
        img_url_list = re.findall(p, content)

        for url in img_url_list:
            with contextlib.suppress(Exception):
                url_local = self._format_url_path(url)
                r = requests.get(url, timeout=20)
                img_fn = os.path.join(self._output_folder, url_local)
                self._save_img(
                    r.content, img_fn,
                    min_width=kwargs.get('image_min_width'),
                    min_height=kwargs.get('image_min_height'),
                    ratio=kwargs.get('image_ratio')
                )
                content = content.replace(url, url_local)

        return content

    @staticmethod
    def _save_img(content: bytes, filename: str,
                  min_width: int = None, min_height: int = None,
                  ratio: float = None) -> None:
        min_width = min_width or 500
        min_height = min_height or 500
        ratio = ratio or 0.5

        img = Image.open(io.BytesIO(content))
        w, h = img.size
        if w <= min_width or h <= min_height:
            img.save(filename, img.format)
            return

        rw, rh = int(w * ratio), int(h * ratio)
        if rw < min_width:
            rw, rh = min_width, int(rh * min_width / rw)
        if rh < min_height:
            rw, rh = int(rw * min_height / rh), min_height
        img.thumbnail((rw, rh))
        img.save(filename, img.format)

    @staticmethod
    def _format_url_path(url: str) -> str:
        o = urlparse(url)
        u = pathlib.Path(o.path)
        stem, suffix = u.stem, u.suffix
        return '{}-{}{}'.format(stem, int(time.time()), suffix)

    @staticmethod
    def format_file_name(path: str) -> str:
        """
        去掉path中的不规则字符
        """
        return path.replace('/', '').replace(' ', '').\
            replace('+', '-').replace('"', '').replace('\\', '').\
            replace(':', '-').replace('|', '-').replace('>','-')
