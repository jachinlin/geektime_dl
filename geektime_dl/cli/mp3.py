# coding=utf8

import os
import sys
from typing import List

from termcolor import colored

from geektime_dl.data_client.gk_apis import GkApiError
from geektime_dl.utils.ebook import Render
from geektime_dl.utils.mp3_downloader import Downloader
from geektime_dl.cli import Command, add_argument


class Mp3(Command):
    """保存专栏音频"""

    def get_all_course_ids(self, dc, type_: str) -> List[int]:

        cid_list = []
        data = dc.get_course_list()
        for c in data['1']['list']:
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
    @add_argument("--url-only", dest="url_only", action='store_true',
                  default=False, help="download mp3/mp4 url only")
    @add_argument("--workers", dest="workers", type=int, save=True,
                  help="specify the number of threads to download mp3/mp4")
    def run(self, cfg: dict):

        dc = self.get_data_client(cfg)
        course_ids = self.parse_course_ids(cfg['course_ids'], dc)
        output_folder = self._format_out_folder(cfg)

        dl = Downloader(output_folder, workers=cfg['workers'])

        for course_id in course_ids:
            try:
                course_data = dc.get_course_intro(course_id)
            except GkApiError as e:
                sys.stderr.write('{}\n\n'.format(e))
                continue
            if int(course_data['column_type']) != 1:
                sys.stderr.write('该课程不提供音频:{} {}\n\n'.format(
                    course_id, course_data['column_title']))
                continue
            out_dir = os.path.join(
                output_folder,
                Render.format_file_name(course_data['column_title']))
            if not os.path.isdir(out_dir):
                os.makedirs(out_dir)

            # fetch raw data
            print(colored('开始下载音频:{}-{}'.format(
                course_id, course_data['column_title']), 'green'))
            pbar_desc = '数据爬取中:{}'.format(course_data['column_title'][:10])
            data = dc.get_course_content(course_id, pbar_desc=pbar_desc)

            # save url
            if cfg['url_only']:
                self._parse_and_save_url(course_data, data, out_dir)
                continue

            # download mp3
            for post in data:
                fn = Render.format_file_name(
                    post['article_title']) + '.mp3'
                if os.path.isfile(os.path.join(out_dir, fn)):
                    sys.stdout.write(fn + ' exists\n')
                    continue
                if post['audio_download_url']:
                    dl.run(post['audio_download_url'],
                           file_name=os.path.join(out_dir, fn))
        dl.shutdown()

    @staticmethod
    def _format_out_folder(cfg):
        output_folder = os.path.join(cfg['output_folder'], 'mp3')
        output_folder = os.path.expanduser(output_folder)
        if not os.path.isdir(output_folder):
            os.makedirs(output_folder)
        return output_folder

    @staticmethod
    def _parse_and_save_url(course_intro: dict,
                            course_data: list, out_dir: str):
        title = Render.format_file_name(course_intro['column_title'])
        fn = os.path.join(out_dir, '{}.mp3.txt'.format(title))
        with open(fn, 'w') as f:
            f.write('\n'.join(["{}:\t\t{}".format(
                Render.format_file_name(post['article_title']),
                post['audio_download_url']
            ) for post in course_data]))
        sys.stdout.write('音频链接下载完成：{}\n\n'.format(fn))

