# coding=utf8

import os
from geektime_dl.data_client import DataClient
from ..utils.mp3_downloader import Downloader
from . import Command
from ..utils import format_path


class Mp3(Command):
    """保存专栏音频
    eektime mp3 <course_id> [--url-only] [--out-dir=<out_dir>]

    `[]`表示可选，`<>`表示相应变量值

    course_id: 课程ID，可以从 query subcmd 查看
    --url-only: 只保存音频url
    --out_dir: 音频存放目录，默认当前目录

    notice: 此 subcmd 需要先执行 login subcmd
    e.g.: geektime mp3 48 --out-dir=~/geektime-ebook
    """
    def run(self, args):

        course_id = args[0]
        url_only = '--url-only' in args[1:]
        for arg in args[1:]:
            if '--out-dir=' in arg:
                out_dir = arg.split('--out-dir=')[1] or './mp3'
                break
        else:
            out_dir = './mp3'
        if not os.path.isdir(out_dir):
            os.makedirs(out_dir)

        dc = DataClient()
        course_data = dc.get_course_intro(course_id)
        if int(course_data['column_type']) != 1:
            raise Exception('该课程不提供音频:%s' % course_data['column_title'])

        out_dir = os.path.join(out_dir, course_data['column_title'])
        if not os.path.isdir(out_dir):
            os.makedirs(out_dir)

        data = dc.get_course_content(course_id)

        if url_only:
            with open(os.path.join(out_dir, '%s.mp3.txt' % course_data['column_title']), 'w') as f:
                # TODO alignment
                f.write('\n'.join(["{}:\t\t{}".format(post['article_title'], post['audio_download_url']) for post in data]))

            return

        dl = Downloader()
        for post in data:
            file_name = format_path(post['article_title'] + '.mp3')
            if os.path.isfile(os.path.join(out_dir, file_name)):
                print(file_name + ' exists')
                continue
            if post['audio_download_url']:
                dl.run(post['audio_download_url'], out_file=file_name, out_dir=out_dir)
                print('download mp3 done: ' + file_name)


class Mp3Batch(Mp3):
    """批量下载 mp3
    懒， 不想写参数了
    """
    def run(self, args):
        if '--all' in args:
            dc = DataClient()
            data = dc.get_course_list()
            cid_list = []
            for c in data['1']['list']:
                if c['had_sub']:
                    cid_list.append(str(c['id']))

        else:
            course_ids = args[0]
            cid_list = course_ids.split(',')

        for cid in cid_list:
            super(Mp3Batch, self).run([cid.strip()] + args)

