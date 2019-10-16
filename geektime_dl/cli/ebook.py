# coding=utf8

import os
import sys
import json
import datetime
from typing import List

from termcolor import colored
from kindle_maker import make_mobi
from tqdm import tqdm

from geektime_dl.cli import Command, add_argument
from geektime_dl.utils.ebook import Render
from geektime_dl.utils.mail import send_to_kindle
from geektime_dl.data_client.gk_apis import GkApiError
from geektime_dl.data_client import DataClient


class EBook(Command):
    """将专栏文章制作成电子书"""

    def _format_title(self, c):
        """
        课程文件名
        """
        if not c['had_sub']:
            t = c['column_title'] + '[免费试读]'
        elif self.is_course_finished(c):
            t = c['column_title'] + '[更新完毕]'
        else:
            t = c['column_title'] + '[未完待续{}]'.format(datetime.date.today())
        return t

    def _render_source_files(self, course_intro: dict, course_content: list,
                             out_dir: str, force: bool = False,
                             **kwargs) -> None:
        """
        下载课程源文件
        """
        articles = course_content
        column_title = course_intro['column_title']
        _out_dir = os.path.join(out_dir, column_title)
        if not os.path.isdir(_out_dir):
            os.makedirs(_out_dir)

        render = Render(_out_dir)
        # introduction
        if not force and os.path.isfile(os.path.join(_out_dir, '简介.html')):
            sys.stdout.write('{}简介 exists\n'.format(column_title))
        else:
            render.render_article_html(
                '简介', course_intro['column_intro'], **kwargs)
            sys.stdout.write('下载{}简介 done\n'.format(column_title))
        # cover
        if not force and os.path.isfile(os.path.join(_out_dir, 'cover.jpg')):
            sys.stdout.write('{}封面 exists\n'.format(column_title))
        else:
            render.generate_cover_img(course_intro['column_cover'])
            sys.stdout.write('下载{}封面 done\n'.format(column_title))
        # toc
        ebook_name = self._format_title(course_intro)
        render.render_toc_md(
            ebook_name,
            ['简介']
            + [render.format_file_name(t['article_title']) for t in articles]
        )
        sys.stdout.write('下载{}目录 done\n'.format(column_title))
        # articles
        articles = tqdm(articles)
        for article in articles:
            articles.set_description('HTML 文件下载中:{}'.format(
                article['article_title'][:10]))
            title = render.format_file_name(article['article_title'])
            fn = os.path.join(_out_dir, '{}.html'.format(title))
            if not force and os.path.isfile(fn):
                continue
            render.render_article_html(
                title, article['article_content'], **kwargs)

    def get_all_course_ids(self, dc: DataClient, type_: str) -> List[int]:

        cid_list = []
        data = dc.get_course_list()
        for c in data['1']['list'] + data['2']['list']:
            if type_ == 'all':
                cid_list.append(int(c['id']))
            elif type_ == 'all-sub' and c['had_sub']:
                cid_list.append(int(c['id']))
            elif (type_ == 'all-done' and c['had_sub'] and
                  self.is_course_finished(c)):
                cid_list.append(int(c['id']))
        return cid_list

    @add_argument("course_ids", type=str,
                  help="specify the target course ids")
    @add_argument("--force", dest="force", action='store_true', default=False,
                  help="do not use the cache data")
    @add_argument("--comments-count", dest="comments_count", type=int,
                  default=0, save=True,
                  help="the count of comments to fetch each post")
    @add_argument("--push", dest="push", action='store_true', default=False,
                  help="push to kindle")
    @add_argument("--smtp-host", dest="smtp_host", type=str, save=True,
                  help="specify the smtp host")
    @add_argument("--smtp-port", dest="smtp_port", type=int, save=True,
                  help="specify the a smtp port")
    @add_argument("--smtp-encryption", dest="smtp_encryption", save=True,
                  help="specify the a smtp encryption")
    @add_argument("--smtp-user", dest="smtp_user", type=str, save=True,
                  help="specify the smtp user")
    @add_argument("--smtp-password", dest="smtp_password", type=str, save=True,
                  help="specify the smtp password")
    @add_argument("--email-to", dest="email_to", type=str, save=True,
                  help="specify the kindle receiver email")
    @add_argument("--image-min-width", dest="image_min_width", type=int,
                  save=True, help="image min width")
    @add_argument("--image-min-height", dest="image_min_height", type=int,
                  save=True, help="image min height")
    @add_argument("--image-ratio", dest="image_ratio", type=float, save=True,
                  help="image ratio")
    def run(self, cfg: dict) -> None:

        dc = self.get_data_client(cfg)
        course_ids = self.parse_course_ids(cfg['course_ids'], dc)
        output_folder = self._format_output_folder(cfg)

        for course_id in course_ids:
            try:
                course_intro = dc.get_course_intro(course_id, force=True)
            except GkApiError as e:
                sys.stderr.write('{}\n\n'.format(e))
                continue
            if int(course_intro['column_type']) not in (1, 2):
                sys.stderr.write("ERROR: 该课程不提供文本:{}".format(
                    course_intro['column_title']))
                continue
            course_intro['column_title'] = Render.format_file_name(
                course_intro['column_title'])

            # fetch raw data
            print(colored('开始制作电子书:{}-{}'.format(
                course_id, course_intro['column_title']), 'green'))
            pbar_desc = '数据爬取中:{}'.format(course_intro['column_title'][:10])
            data = dc.get_course_content(
                course_id, force=cfg['force'], pbar_desc=pbar_desc)
            if cfg['comments_count'] > 0:
                for post in data:
                    post['article_content'] += self._render_comment_html(
                        post['comments'], cfg['comments_count'])

            # source file
            self._render_source_files(course_intro, data, output_folder, **cfg)

            # ebook 未完结或者 force 都会重新制作电子书
            ebook_name = self._format_title(course_intro)
            fn = os.path.join(output_folder, ebook_name) + '.mobi'
            if (not cfg['force'] and self.is_course_finished(course_intro) and
                    os.path.isfile(fn)):
                sys.stdout.write("{} exists\n".format(ebook_name))
            else:
                src_dir = os.path.join(
                    output_folder, course_intro['column_title'])
                make_mobi(source_dir=src_dir, output_dir=output_folder)

            # push to kindle
            if cfg['push']:
                self._send_to_kindle(cfg, fn)
                sys.stdout.write("{} 已推送到 kindle\n\n".format(ebook_name))

    @staticmethod
    def _send_to_kindle(cfg, fn):
        try:
            send_to_kindle(fn, cfg)
        except Exception as e:
            sys.stderr.write(
                "ERROR: push to kindle failed, e={}\n".format(e))

    @staticmethod
    def _format_output_folder(cfg):
        output_folder = os.path.join(cfg['output_folder'], 'ebook')
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
