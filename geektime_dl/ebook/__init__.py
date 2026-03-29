# coding=utf8
"""
Ebook 模块 - 使用 EbookLib 生成 EPUB
"""

import re
import time
import contextlib
import io
from typing import Optional, List
from urllib.parse import urlparse
from pathlib import Path

import requests
from PIL import Image
from ebooklib import epub
from tqdm import tqdm


def format_file_name(path: str) -> str:
    """移除文件名中的非法字符"""
    return re.sub(r'[/\\?%*:|\'"<>.,;=\\s]+', '', path)


def _render_html(title: str, content: str) -> str:
    """渲染文章 HTML"""
    return f"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>{title}</title>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
</head>
<body>
<h1>{title}</h1>

{content}

</body>
</html>"""


class EpubBuilder:
    """EPUB 构建器"""

    def __init__(self, title: str, author: str = ""):
        self._book = epub.EpubBook()
        self._book.set_title(title)
        self._book.add_author(author or "geektime-dl")
        self._book.set_language('zh')

        self._chapters: List[epub.EpubHtml] = []

    def set_cover(self, image_data: bytes):
        """设置封面"""
        self._book.set_cover("cover.jpg", image_data)

    def add_image(self, filename: str, image_data: bytes) -> str:
        """添加图片资源，返回 EPUB 内部路径"""
        img_item = epub.EpubImage()
        img_item.file_name = f"images/{filename}"
        img_item.content = image_data
        self._book.add_item(img_item)
        return img_item.file_name

    def add_chapter(self, title: str, html_content: str):
        """添加章节"""
        file_name = f"chapter_{len(self._chapters) + 1}.xhtml"
        chapter = epub.EpubHtml(
            title=title,
            file_name=file_name,
            lang='zh'
        )
        chapter.content = html_content
        self._book.add_item(chapter)
        self._chapters.append(chapter)

    def save(self, output_path: str):
        """保存 EPUB 文件"""
        # 设置目录
        self._book.toc = self._chapters
        self._book.add_item(epub.EpubNcx())
        self._book.add_item(epub.EpubNav())

        # 设置书脊
        self._book.spine = ['nav'] + self._chapters

        epub.write_epub(output_path, self._book, {})


def _download_image(url: str) -> Optional[bytes]:
    """下载图片"""
    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        return r.content
    except Exception:
        return None


def _resize_image(
    image_data: bytes,
    min_width: int = None,
    min_height: int = None,
    ratio: float = None
) -> bytes:
    """调整图片尺寸"""
    min_width = min_width or 500
    min_height = min_height or 500
    ratio = ratio or 0.5

    img = Image.open(io.BytesIO(image_data))
    w, h = img.size

    if w <= min_width or h <= min_height:
        return image_data

    rw, rh = int(w * ratio), int(h * ratio)
    if rw < min_width:
        # 保持宽高比
        rw, rh = min_width, int(h * min_width / w)
    if rh < min_height:
        # 保持宽高比
        rw, rh = int(w * min_height / h), min_height

    img.thumbnail((rw, rh))
    output = io.BytesIO()
    img.save(output, format=img.format or 'JPEG')
    return output.getvalue()


def _format_url_path(url: str) -> str:
    """从 URL 生成本地文件名"""
    o = urlparse(url)
    u = Path(o.path)
    stem, suffix = u.stem, u.suffix or '.jpg'
    return f'{stem}-{int(time.time())}{suffix}'


def _process_content(
    content: str,
    builder: EpubBuilder,
    **kwargs
) -> str:
    """处理文章内容：下载图片，替换 URL"""
    # 移除 img 标签中的 style 属性
    p = r'img (.{1,15}=".*?") src=".*?"'
    styles = re.findall(p, content)
    for style in styles:
        content = content.replace(style, '')

    # 移除空的 img 标签
    p = r'</?img>'
    empty_imgs = re.findall(p, content)
    for empty_img in empty_imgs:
        content = content.replace(empty_img, '')

    # 下载图片
    p = r'img\s+src="(.*?)"'
    img_url_list = re.findall(p, content)

    for url in img_url_list:
        with contextlib.suppress(Exception):
            img_data = _download_image(url)
            if img_data is None:
                continue

            img_data = _resize_image(
                img_data,
                min_width=kwargs.get('image_min_width'),
                min_height=kwargs.get('image_min_height'),
                ratio=kwargs.get('image_ratio')
            )

            url_local = _format_url_path(url)
            epub_path = builder.add_image(url_local, img_data)
            content = content.replace(url, epub_path)

    return content


def build_epub(
    course_intro: dict,
    articles: list,
    output_path: str,
    **kwargs
):
    """
    构建 EPUB 电子书

    Args:
        course_intro: 课程信息字典
        articles: 文章列表
        output_path: 输出文件路径
        **kwargs: 图片处理参数
    """
    title = course_intro['column_title']
    author = course_intro.get('author_name', '')

    builder = EpubBuilder(title, author)

    # 封面
    cover_url = course_intro.get('column_cover')
    if cover_url:
        cover_data = _download_image(cover_url)
        if cover_data:
            builder.set_cover(cover_data)

    # 简介
    intro_content = course_intro.get('column_intro', '')
    intro_html = _render_html('简介', intro_content)
    builder.add_chapter('简介', intro_html)

    # 文章
    for article in tqdm(articles, desc='生成 EPUB 章节'):
        article_title = article['article_title']
        article_content = article['article_content']

        # 处理图片
        processed_content = _process_content(article_content, builder, **kwargs)

        # 渲染 HTML
        html = _render_html(article_title, processed_content)
        builder.add_chapter(article_title, html)

    # 保存
    builder.save(output_path)
