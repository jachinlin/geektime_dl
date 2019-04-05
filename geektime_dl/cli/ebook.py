# coding=utf8

import os
import json
import datetime
from geektime_dl.data_client import DataClient
from . import Command
from ..geektime_ebook import maker
from kindle_maker import make_mobi
from geektime_dl.utils.mail import MailServer


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

    def render_column_source_files(self, course_intro, course_content, out_dir, force=False):

        # TODO refactor here
        # cover and introduction
        course_intro = course_intro
        articles = course_content
        column_title = course_intro['column_title']

        output_dir = os.path.join(out_dir, column_title)
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)
            print('mkdir ' + output_dir)

        if not force and os.path.isfile(os.path.join(output_dir, '{}.html'.format('简介'))):
            print('简介' + ' exists')
        else:
            maker.render_article_html('简介', maker.parse_image(course_intro['column_intro'], output_dir), output_dir)
            print('下载' + column_title + '简介' + ' done')
        maker.generate_cover_img(course_intro['column_cover'], output_dir)
        print('下载' + column_title + '封面' + ' done')

        ebook_name = self._title(course_intro)
        maker.render_toc_md(
            ebook_name + '\n',
            ['# 简介\n'] + ['# ' + maker.format_file_name(t['article_title']) + '\n' for t in articles],
            output_dir
        )
        print('下载' + column_title + '目录' + ' done')

        for article in articles:

            title = maker.format_file_name(article['article_title'])
            if not force and os.path.isfile(os.path.join(output_dir, '{}.html'.format(title))):
                print(title + ' exists')
                continue
            maker.render_article_html(title, maker.parse_image(article['article_content'], output_dir), output_dir)
            print('下载' + column_title + '：' + article['article_title'] + ' done')

    def run(self, args):

        course_id = args[0]
        for arg in args[1:]:
            if '--out-dir=' in arg:
                out_dir = arg.split('--out-dir=')[1] or './ebook'
                break
        else:
            out_dir = './ebook'

        force = '--force' in args[1:]
        enable_comments = '--enable-comments' in args[1:]
        source_only = '--source-only' in args[1:]
        push = '--push' in args[1:]

        for arg in args[1:]:
            if '--comment-count=' in arg:
                comment_count = arg.split('--comment-count=')[1] or 10
                break
        else:
            comment_count = 10

        if not os.path.isdir(out_dir):
            os.makedirs(out_dir)

        dc = DataClient()
        course_data = dc.get_course_intro(course_id, force=True)

        if int(course_data['column_type']) not in (1, 2):
            raise Exception('该课程不提供文本:%s' % course_data['column_title'])

        # data
        data = dc.get_course_content(course_id, force=force)

        if enable_comments:
            for post in data:
                post['article_content'] += self._render_comment_html(post['comments'], comment_count)

        # source file
        course_data['column_title'] = maker.format_file_name(course_data['column_title'])
        self.render_column_source_files(course_data, data, out_dir, force=force)

        # ebook
        if not source_only:
            if course_data['update_frequency'] == '全集' and os.path.isfile(os.path.join(out_dir, self._title(course_data)) + '.mobi'):
                print("{} exists ".format(self._title(course_data)))
            else:
                make_mobi(source_dir=os.path.join(out_dir, course_data['column_title']), output_dir=out_dir)
        if push:

            fn = os.path.join(out_dir, "{}.mobi".format(self._title(course_data)))
            if os.path.getsize(fn) / 1024.0 / 1024 > 50:
                print("电子书大小超过50M")
                return
            f = open(fn, 'rb')
            d = f.read()
            f.close()

            with open('smtp.conf') as f:
                smtp_conf = json.loads(f.read())
            m = MailServer(host=smtp_conf['host'], port=smtp_conf['port'], user=smtp_conf['user'], password=smtp_conf['password'], encryption=smtp_conf['encryption'])
            message = m.build_email(email_to=smtp_conf['email_to'], subject='convert', body='', attachments=[("{}.mobi".format(self._title(course_data)), d)])
            m.send_email(message)
            print("push to kindle done")

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
    def run(self, args):
        if '--all' in args:
            dc = DataClient()
            data = dc.get_course_list()

            for c in data['1']['list'] + data['2']['list']:
                if not c['had_sub']:
                    continue
                if c['update_frequency'] == '全集':
                    super(EbookBatch, self).run([str(c['id'])] + args)
                    print('\n')
                else:
                    super(EbookBatch, self).run([str(c['id']), '--source-only'] + args)
                    print('\n')

        else:
            course_ids = args[0]
            cid_list = course_ids.split(',')

            for cid in cid_list:
                super(EbookBatch, self).run([cid.strip()] + args)
                print('\n')



