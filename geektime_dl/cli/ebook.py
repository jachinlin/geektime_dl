# coding=utf8

import os
import sys
import json
import datetime
from geektime_dl.data_client import get_data_client
from . import Command
from geektime_dl.utils.ebook import Render
from kindle_maker import make_mobi
from geektime_dl.utils.mail import send_to_kindle


class EBook(Command):
    """将专栏文章制作成电子书

    geektime ebook -c <course_id> [--output-folder=<output_folder>] [--enable-comments] [--comments-count=<comments_count>]

    `[]`表示可选，`<>`表示相应变量值

    course_id: 课程ID，可以从 query subcmd 查看
    output_folder: 电子书存放目录，默认当前目录
    --enable-comments: 启动评论下载，默认不下载评论
    comments_count: 在启动评论下载时，设置评论条数，默认10条

    notice: 此 subcmd 需要先执行 login subcmd
    e.g.: geektime ebook 48 --output-folder=~/geektime-ebook
    """

    @staticmethod
    def _title(c):
        """
        课程文件名
        """
        if not c['had_sub']:
            t = c['column_title'] + '[免费试读]'
        elif c['is_finish']:
            t = c['column_title'] + '[更新完毕]'
        else:
            t = c['column_title'] + '[未完待续{}]'.format(datetime.date.today())
        return t

    def _render_source_files(self, course_intro: dict, course_content: list,
                             out_dir: str, force: bool = False) -> None:
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
            sys.stdout.write( '{}简介 exists\n'.format(column_title))
        else:
            render.render_article_html('简介', course_intro['column_intro'])
            sys.stdout.write('下载{}简介 done\n'.format(column_title))
        # cover
        if not force and os.path.isfile(os.path.join(_out_dir, 'cover.jpg')):
            sys.stdout.write( '{}封面 exists\n'.format(column_title))
        else:
            render.generate_cover_img(course_intro['column_cover'])
            sys.stdout.write('下载{}封面 done\n'.format(column_title))
        # toc
        ebook_name = self._title(course_intro)
        render.render_toc_md(
            ebook_name,
            ['简介'] + [render.format_file_name(t['article_title']) for t in articles]
        )
        sys.stdout.write('下载{}目录 done\n'.format(column_title))
        # articles
        for article in articles:
            title = render.format_file_name(article['article_title'])
            if not force and os.path.isfile(os.path.join(_out_dir, '{}.html'.format(title))):
                sys.stdout.write(title + ' exists\n')
                continue
            render.render_article_html(title, article['article_content'])
            sys.stdout.write('下载{}:{} done\n'.format(column_title, title))

    def run(self, cfg: dict) -> None:

        course_id = cfg['course_id']
        if not course_id:
            sys.stderr.write("ERROR: couldn't find the target course id\n")
            return
        out_dir = os.path.join(cfg['output_folder'], 'ebook')
        out_dir = os.path.expanduser(out_dir)
        if not os.path.isdir(out_dir):
            try:
                os.makedirs(out_dir)
            except OSError:
                sys.stderr.write("ERROR: couldn't create the output folder {}\n".format(out_dir))
                return
        try:
            dc = get_data_client(cfg)
        except:
            sys.stderr.write("ERROR: invalid geektime account or password\n"
                             "Use '%s login --help' for  help.\n" % sys.argv[0].split(os.path.sep)[-1])
            return

        course_data = dc.get_course_intro(course_id, force=True)
        if int(course_data['column_type']) not in (1, 2):
            sys.stderr.write("ERROR: 该课程不提供文本:%s" % course_data['column_title'])
            return

        # data
        sys.stdout.write('doing ......\n')
        data = dc.get_course_content(course_id, force=cfg['force'])
        if cfg['enable_comments']:
            for post in data:
                post['article_content'] += self._render_comment_html(post['comments'], cfg['comments_count'])

        # source file
        course_data['column_title'] = Render.format_file_name(course_data['column_title'])
        self._render_source_files(course_data, data, out_dir, force=cfg['force'])

        # ebook
        ebook_name = self._title(course_data)
        if not cfg['source_only']:
            if course_data['is_finish'] and os.path.isfile(os.path.join(out_dir, ebook_name) + '.mobi'):
                sys.stdout.write("{} exists\n".format(ebook_name))
            else:
                make_mobi(source_dir=os.path.join(out_dir, course_data['column_title']), output_dir=out_dir)

        # push to kindle
        if cfg['push'] and not cfg['source_only']:
            fn = os.path.join(out_dir, "{}.mobi".format(ebook_name))
            try:
                send_to_kindle(fn, cfg)
                sys.stdout.write("push to kindle done\n")
            except Exception as e:
                sys.stderr.write("ERROR: push to kindle failed, e={}\n".format(e))

    @staticmethod
    def _timestamp2str(timestamp: int) -> str:
        if not timestamp:
            return ''
        return datetime.datetime.fromtimestamp(int(timestamp)).strftime("%Y-%m-%d %H:%M:%S")

    def _render(self, c):
        replies = json.loads(c.get('replies'))

        reply = replies[0] if replies else {}
        replies_html = """<br/>
<div>
    <div style="color:#888;font-size:15.25px;font-weight:400;line-height:1.2">{}{}</div>
    <div style="color:#353535;font-weight:400;white-space:normal;word-break:break-all;line-height:1.6">{}</div>
</div>
            """.format(
            reply.get('user_name'),
            self._timestamp2str(reply.get('ctime')),
            reply.get('content')
        ) if reply else ''

        c_html = """
<li>
    <div>
        <div style="color: #888;font-size:15.25px;font-weight:400;line-height:1.2">
            {user_name}  {comment_time}
        </div>
        <div style="color:#353535;font-weight:400;white-space:normal;word-break:break-all;line-height:1.6">
            {comment_content} {like_count}
        </div>
        {replies}
    </div>
</li>
            """.format(
            user_name=c['user_name'],
            like_count="[{}赞]".format(c['like_count']) if c['like_count'] else '',
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


class EbookBatch(EBook):
    """批量制作电子书
    懒， 不想写参数了
    """
    def run(self, cfg: dict):
        cid_list = []
        if cfg['all']:
            try:
                dc = get_data_client(cfg)
            except:
                sys.stderr.write("ERROR: invalid geektime account or password\n"
                                 "Use '{} login --help' for  help.\n".format(
                    sys.argv[0].split(os.path.sep)[-1]))
                return

            data = dc.get_course_list()
            for c in data['1']['list'] + data['2']['list']:
                if c['update_frequency'] == '全集':
                    cid_list.append(c['id'])


        else:
            course_ids = cfg['course_ids']
            cid_list.extend(course_ids.split(','))

        for cid in cid_list:
            args = cfg.copy()
            args['course_id'] = int(cid)
            super().run(args)
            sys.stderr.write('\n')



