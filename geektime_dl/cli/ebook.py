# coding=utf8

import os
import sys
import json
import datetime
from geektime_dl.data_client import get_data_client
from . import Command
from ..geektime_ebook import maker
from kindle_maker import make_mobi
from geektime_dl.utils.mail import send_to_kindle


class EBook(Command):
    """将专栏文章制作成电子书

    geektime ebook <course_id> [--out-dir=<out_dir>] [--enable-comments] [--comment-count=<comment_count>]

    `[]`表示可选，`<>`表示相应变量值

    course_id: 课程ID，可以从 query subcmd 查看
    --out_dir: 电子书存放目录，默认当前目录
    --enable-comments: 启动评论下载，默认不下载评论
    --comment-count: 在启动评论下载时，设置评论条数，默认10条

    notice: 此 subcmd 需要先执行 login subcmd
    e.g.: geektime ebook 48 --out-dir=~/geektime-ebook
    """

    @staticmethod
    def _title(c):
        if not c['had_sub']:
            t = c['column_title'] + '[免费试读]'
        elif c['update_frequency'] == '全集':
            t = c['column_title'] + '[更新完毕]'
        else:
            t = c['column_title'] + '[未完待续{}]'.format(datetime.date.today())
        return t

    def _render_column_source_files(self, course_intro: dict, course_content: list,
                                   out_dir: str, force: bool = False) -> None:

        # TODO refactor here
        # cover and introduction
        articles = course_content
        column_title = course_intro['column_title']

        output_dir = os.path.join(out_dir, column_title)
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)

        # introduction
        if not force and os.path.isfile(os.path.join(output_dir, '简介.html')):
            sys.stdout.write(column_title + '简介' + ' exists\n')
        else:
            maker.render_article_html('简介', maker.parse_image(course_intro['column_intro'], output_dir), output_dir)
            sys.stdout.write('下载' + column_title + '简介' + ' done\n')
        # cover
        if not force and os.path.isfile(os.path.join(output_dir, 'cover.jpg')):
            sys.stdout.write(column_title + '封面' + ' exists\n')
        else:
            maker.generate_cover_img(course_intro['column_cover'], output_dir)
            sys.stdout.write('下载' + column_title + '封面' + ' done\n')

        # toc
        ebook_name = self._title(course_intro)
        maker.render_toc_md(
            ebook_name + '\n',
            ['# 简介\n'] + ['# ' + maker.format_file_name(t['article_title']) + '\n' for t in articles],
            output_dir
        )
        sys.stdout.write('下载' + column_title + '目录' + ' done\n')

        for article in articles:

            title = maker.format_file_name(article['article_title'])
            if not force and os.path.isfile(os.path.join(output_dir, '{}.html'.format(title))):
                sys.stdout.write(title + ' exists\n')
                continue
            maker.render_article_html(title, maker.parse_image(article['article_content'], output_dir), output_dir)
            sys.stdout.write('下载' + column_title + '：' + article['article_title'] + ' done\n')

    def run(self, cfg: dict) -> None:
        # from ipdb import set_trace;set_trace()
        course_id = cfg['course_id']
        if not course_id:
            sys.stderr.write("ERROR: couldn't find the target course id\n")
            return
        out_dir = os.path.join(cfg['output_folder'], 'ebook')
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
                             "Use '%s <command> login --help' for  help.\n" % sys.argv[0].split(os.path.sep)[-1])
            return

        course_data = dc.get_course_intro(course_id, force=True)
        if int(course_data['column_type']) not in (1, 2):
            sys.stderr.write("ERROR: 该课程不提供文本:%s" % course_data['column_title'])
            return

        # data
        data = dc.get_course_content(course_id, force=cfg['force'])

        if cfg['enable_comments']:
            for post in data:
                post['article_content'] += self._render_comment_html(post['comments'], cfg['comments_count'])

        # source file
        course_data['column_title'] = maker.format_file_name(course_data['column_title'])
        self._render_column_source_files(course_data, data, out_dir, force=cfg['force'])

        # ebook
        if not cfg['source_only']:
            if course_data['update_frequency'] == '全集' and os.path.isfile(os.path.join(out_dir, self._title(course_data)) + '.mobi'):
                sys.stdout.write("{} exists\n".format(self._title(course_data)))
            else:
                make_mobi(source_dir=os.path.join(out_dir, course_data['column_title']), output_dir=out_dir)

        # push to kindle
        if cfg['push'] and not cfg['source_only']:
            fn = os.path.join(out_dir, "{}.mobi".format(self._title(course_data)))
            try:
                send_to_kindle(fn, cfg)
                sys.stdout.write("push to kindle done\n")
            except Exception as e:
                sys.stderr.write("ERROR: push to kindle failed, e={}\n".format(e))

    def _timestamp2str(self, timestamp):
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
            """.format(reply.get('user_name'), self._timestamp2str(reply.get('ctime')), reply.get('content')) if reply else ''

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
            """.format(user_name=c['user_name'], like_count="[{}赞]".format(c['like_count']) if c['like_count'] else '',
                       comment_content=c['comment_content'],
                       comment_time=self._timestamp2str(c['comment_ctime']), replies=replies_html)
        return c_html

    def _render_comment_html(self, comments, comment_count):
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
                                 "Use '{} <command> login --help' for  help.\n".format(
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



