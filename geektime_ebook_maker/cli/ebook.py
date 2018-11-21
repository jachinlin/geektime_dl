# coding=utf8

from ..gk_apis import *
from ..store_client import StoreClient
from . import Command
from ..geektime_ebook import maker


class EBook(Command):

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

        maker._render_toc_md(
            column_title + '\n',
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

        # source file
        self.render_column_source_files(course_data, data, out_dir)






