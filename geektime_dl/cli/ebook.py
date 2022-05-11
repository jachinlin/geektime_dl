# coding=utf8

import os
import pathlib
import sys
import json
import datetime

from termcolor import colored
from ebook import make_ebook
from ebook.ebooklib import format_file_name
from tqdm import tqdm

from geektime_dl.cli import Command, add_argument
from geektime_dl.ebook.ebook import Render
from geektime_dl.gt_apis import GkApiError
from geektime_dl.utils import (
    get_working_folder,
    parse_column_ids
)


class EBook(Command):
    """将专栏文章制作成电子书"""

    def _format_title(self, c):
        """
        课程文件名
        """

        t = format_file_name(c['column_title'])
        if not c['had_sub']:
            t += '[免费试读]'
        elif self.is_course_finished(c):
            pass
        else:
            t += '[未完待续{}]'.format(datetime.date.today())
        return t

    def _generate_source_files(self, course_intro: dict, articles: list,
                               source_folder: str, no_cache: bool = False,
                               **kwargs) -> None:
        """
        下载课程源文件
        """
        column_title = course_intro['column_title']
        _out_dir = source_folder

        render = Render(str(_out_dir))
        # introduction
        if not no_cache and os.path.isfile(os.path.join(_out_dir, '简介.html')):
            sys.stdout.write('{}简介 exists\n'.format(column_title))
        else:
            render.render_article_html(
                '简介', course_intro['column_intro'], **kwargs)
            sys.stdout.write('下载{}简介 done\n'.format(column_title))
        # cover
        if not no_cache and os.path.isfile(os.path.join(_out_dir, 'cover.jpg')):
            sys.stdout.write('{}封面 exists\n'.format(column_title))
        else:
            render.generate_cover_img(course_intro['column_cover'])
            sys.stdout.write('下载{}封面 done\n'.format(column_title))
        # toc
        ebook_name = self._format_title(course_intro)
        render.render_toc_md(
            ebook_name,
            ['简介']
            + [format_file_name(t['article_title']) for t in articles]
        )
        sys.stdout.write('下载{}目录 done\n'.format(column_title))
        # articles
        articles = tqdm(articles)
        for article in articles:
            articles.set_description('HTML 文件下载中:{}'.format(
                article['article_title'][:10]))
            file_basename = format_file_name(article['article_title'])
            fn = os.path.join(_out_dir, '{}.html'.format(file_basename))
            if not no_cache and os.path.isfile(fn):
                continue
            render.render_article_html(
                file_basename, article['article_content'], **kwargs)

    @add_argument("course_ids", type=str,
                  help="specify the target course ids")
    @add_argument("--no-cache", dest="no_cache", action='store_true',
                  default=False, help="do not use the cache data")
    @add_argument("--comments-count", dest="comments_count", type=int,
                  default=0, save=True,
                  help="the count of comments to fetch each post")
    @add_argument("--image-min-width", dest="image_min_width", type=int,
                  save=True, help="image min width")
    @add_argument("--image-min-height", dest="image_min_height", type=int,
                  save=True, help="image min height")
    @add_argument("--image-ratio", dest="image_ratio", type=float, save=True,
                  help="image ratio")
    @add_argument("--format", dest="format", type=str, save=True,
                  default='mobi', help="ebook format")
    def run(self, cfg: dict) -> None:
        course_ids = parse_column_ids(cfg['course_ids'])

        for course_id in course_ids:
            self._run_once(course_id, cfg)

    def _run_once(self, course_id: int, cfg: dict):
        dc = self.get_data_client(cfg)
        output_folder = self._make_output_folder(cfg['output_folder'])
        no_cache = cfg['no_cache']
        wf = get_working_folder()
        try:
            course_intro = dc.get_column_intro(course_id, no_cache=no_cache)
        except GkApiError as e:
            sys.stderr.write('{}\n\n'.format(e))
            return
        if int(course_intro['column_type']) not in (1, 2):
            sys.stderr.write("ERROR: 该课程不提供文本:{}".format(
                course_intro['column_title']))
            return

        # fetch raw data
        print(colored('开始制作电子书:{}-{}'.format(
            course_id, course_intro['column_title']), 'green'))
        pbar_desc = '数据爬取中:{}'.format(course_intro['column_title'][:10])
        article_ids = course_intro['articles']
        article_ids = tqdm(article_ids)
        article_ids.set_description(pbar_desc)
        articles = list()
        for a in article_ids:
            aid = a['id']
            article = dc.get_article_content(aid, no_cache=no_cache)
            if cfg['comments_count'] > 0:
                article['article_content'] += self._render_comment_html(
                    article['comments'],
                    cfg['comments_count']
                )
            articles.append(article)

        if cfg.get('dont_ebook', False):
            return

        # source file
        source_folder = wf / format_file_name(course_intro['column_title'])
        source_folder.mkdir(exist_ok=True)
        self._generate_source_files(
            course_intro, articles, str(source_folder), **cfg
        )

        # ebook 未完结或者 no_cache 都会重新制作电子书
        ebook_name = '{}.{}'.format(
            self._format_title(course_intro), cfg['format'])
        fp = pathlib.Path(output_folder) / ebook_name
        if (not no_cache and self.is_course_finished(course_intro)
                and fp.exists()):
            print(colored("{} exists\n".format(ebook_name), 'green'))
        else:
            make_ebook(
                source_dir=str(source_folder),
                output_dir=output_folder,
                format=cfg['format']
            )
            print(colored('制作电子书完成:{}-{}'.format(
                course_id, course_intro['column_title']), 'green'))

    @staticmethod
    def _make_output_folder(output_folder: str):
        output_folder = os.path.expanduser(output_folder)
        if not os.path.isdir(output_folder):
            os.makedirs(output_folder)
        return output_folder

    @staticmethod
    def _timestamp2str(timestamp: int) -> str:
        if not timestamp:
            return ''
        return datetime.datetime.fromtimestamp(
            int(timestamp)).strftime("%Y-%m-%d %H:%M:%S")

    def _render(self, c):
        replies = json.loads(c.get('replies'))

        reply = replies[0] if replies else {}
        replies_html = """<br/>
<div>
    <div style="color:#888;font-size:15.25px;font-weight:400;\
        line-height:1.2">{}{}</div>
    <div style="color:#353535;font-weight:400;white-space:normal;\
        word-break:break-all;line-height:1.6">{}</div>
</div>
            """.format(
            reply.get('user_name'),
            self._timestamp2str(reply.get('ctime')),
            reply.get('content')
        ) if reply else ''

        likes = "[{}赞]".format(c['like_count']) if c['like_count'] else ''
        c_html = """
<li>
    <div>
        <div style="color: #888;font-size:15.25px;font-weight:400;\
            line-height:1.2">
            {user_name}  {comment_time}
        </div>
        <div style="color:#353535;font-weight:400;white-space:normal;\
            word-break:break-all;line-height:1.6">
            {comment_content} {like_count}
        </div>
        {replies}
    </div>
</li>
            """.format(
            user_name=c['user_name'],
            like_count=likes,
            comment_content=c['comment_content'],
            comment_time=self._timestamp2str(c['comment_ctime']),
            replies=replies_html
        )
        return c_html

    def _render_comment_html(self, comments, comment_count):
        """
        生成评论的 html 文本
        """
        if not comments:
            return ''

        count = min(len(comments), int(comment_count))
        comments = comments[:count]

        html = '\n<br/>\n'.join([
            self._render(c)
            for c in comments
        ])
        h = """<h2>精选留言：</h2>
        <ul>
        """
        f = '</ul>'
        return h + html + f
