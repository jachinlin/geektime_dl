# coding=utf8

import datetime
from ..gk_apis import *
from ..store_client import StoreClient
from . import Command
from ..geektime_ebook import maker
from kindle_maker import make_mobi


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
    def render_column_source_files(course_intro, course_content, out_dir):

        # TODO refactor here
        # cover and introduction
        course_intro = course_intro
        articles = course_content
        column_title = course_intro['column_title']

        output_dir = os.path.join(out_dir, column_title)
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)
            print('mkdir ' + output_dir)

        maker._render_article_html('简介', maker._parse_image(course_intro['column_intro'], output_dir), output_dir)
        print('下载' + column_title + '简介' + ' done')
        maker._generate_cover_img(course_intro['column_cover'], output_dir)
        print('下载' + column_title + '封面' + ' done')

        def _title(c):
            if not c['had_sub']:
                t = c['column_title'] + '[免费试读]'
            elif c['update_frequency'] == '全集':
                t = c['column_title'] + '[更新完毕]'
            else:
                t = c['column_title'] + '[未完待续]'
            return t

        ebook_name = _title(course_intro)
        maker._render_toc_md(
            ebook_name + '\n',
            ['# 简介\n'] + ['# ' + maker._format_file_name(t['article_title']) + '\n' for t in articles],
            output_dir
        )
        print('下载' + column_title + '目录' + ' done')

        for article in articles:

            title = maker._format_file_name(article['article_title'])
            maker._render_article_html(title, maker._parse_image(article['article_content'], output_dir), output_dir)
            print('下载' + column_title + '：' + article['article_title'] + ' done')

    def run(self, args):

        course_id = args[0]
        for arg in args[1:]:
            if '--out-dir=' in arg:
                out_dir = arg.split('--out-dir=')[1] or '.'
                break
        else:
            out_dir = '.'

        for arg in args[1:]:
            if '--enable-comments' in arg:
                enable_comments = True
                break
        else:
            enable_comments = False

        for arg in args[1:]:
            if '--comment-count=' in arg:
                comment_count = arg.split('--comment-count=')[1] or 10
                break
        else:
            comment_count = 10

        if not os.path.isdir(out_dir):
            os.makedirs(out_dir)

        gk = GkApiClient()
        store_client = StoreClient()

        course_data = gk.get_course_intro(course_id)

        store_client.save_column_info(**course_data)

        if int(course_data['column_type']) != 1:
            raise Exception('该课程不提供文本:%s' % course_data['column_title'])

        # data
        data = []
        _data = gk.get_course_content(course_id)

        for post in _data:
            post_detail = gk.get_post_content(post['id'])
            data.append(post_detail)
            store_client.save_post_content(**post_detail)

            # comments
            comments = gk.get_post_comments(post['id'])
            if enable_comments:
                post_detail['article_content'] += self._render_comment_html(comments, comment_count)
            for c in comments:
                store_client.save_post_comment(article_id=post['id'], **c)

        # source file
        self.render_column_source_files(course_data, data, out_dir)

        # ebook
        make_mobi(source_dir=os.path.join(out_dir, course_data['column_title']), output_dir=out_dir)

    def _timestamp2str(self, timestamp):
        if not timestamp:
            return ''
        return datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

    def _render(self, c):
        replies = c.get('replies') or [{}]
        reply = replies[0]
        replies_html = """<br/>
<div>
    <div style="color:#888;font-size:15.25px;font-weight:400;line-height:1.2">{}{}</div>
    <div style="color:#353535;font-size:15.25px;font-weight:400;white-space:normal;word-break:break-all;line-height:1.6">{}</div>
</div>
            """.format(reply.get('user_name'), self._timestamp2str(reply.get('ctime')), reply.get('content')) if reply else ''

        c_html = """
<li>
    <div>
        <div style="color: #888;font-size:15.25px;font-weight:400;line-height:1.2">
            {user_name}  {comment_time}
        </div>
        <div style="color:#353535;font-size:15.25px;font-weight:400;white-space:normal;word-break:break-all;line-height:1.6">
            {comment_content}[👍{like_count}]
        </div>
        {replies}
    </div>
</li>
            """.format(user_name=c['user_name'], like_count=c['like_count'], comment_content=c['comment_content'],
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
