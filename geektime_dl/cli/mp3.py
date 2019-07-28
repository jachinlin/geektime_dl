# coding=utf8

import os
import sys

from geektime_dl.data_client import get_data_client
from geektime_dl.utils.ebook import Render as EbookRender
from geektime_dl.utils.mp3_downloader import Downloader
from geektime_dl.cli import Command


class Mp3(Command):
    """保存专栏音频
    eektime mp3 -c <course_id> [--url-only] [--output-folder=<output_folder>]

    `[]`表示可选，`<>`表示相应变量值

    course_id: 课程ID，可以从 query subcmd 查看
    url_only: 只保存音频url
    output_folder: 音频存放目录，默认当前目录

    notice: 此 subcmd 需要先执行 login subcmd
    e.g.: geektime mp3 -c 48 --output-folder=~/geektime-mp3
    """
    def run(self, cfg: dict):

        course_id = cfg['course_id']
        if not course_id:
            sys.stderr.write("ERROR: couldn't find the target course id\n")
            return

        out_dir = os.path.join(cfg['output_folder'], 'mp3')
        out_dir = os.path.expanduser(out_dir)
        if not os.path.isdir(out_dir):
            try:
                os.makedirs(out_dir)
            except OSError:
                sys.stderr.write("ERROR: couldn't create the output folder {}\n".format(out_dir))
                return

        url_only = cfg['url_only']

        try:
            dc = get_data_client(cfg)
        except:
            sys.stderr.write("ERROR: invalid geektime account or password\n"
                             "Use '%s login --help' for  help.\n" % sys.argv[0].split(os.path.sep)[-1])
            return

        course_data = dc.get_course_intro(course_id)
        if int(course_data['column_type']) != 1:
            raise Exception('该课程不提供音频:%s' % course_data['column_title'])

        out_dir = os.path.join(out_dir, course_data['column_title'])
        if not os.path.isdir(out_dir):
            os.makedirs(out_dir)

        sys.stdout.write('doing ......\n')
        data = dc.get_course_content(course_id)

        if url_only:
            title = EbookRender.format_file_name(course_data['column_title'])
            with open(os.path.join(out_dir, '%s.mp3.txt' % title), 'w') as f:
                # TODO alignment
                f.write('\n'.join(["{}:\t\t{}".format(
                    EbookRender.format_file_name(post['article_title']),
                    post['audio_download_url']
                ) for post in data]))
                sys.stdout.write('download {} mp3 url done\n'.format(title))
            return

        dl = Downloader()
        for post in data:
            file_name = EbookRender.format_file_name(post['article_title']) + '.mp3'
            if os.path.isfile(os.path.join(out_dir, file_name)):
                sys.stdout.write(file_name + ' exists\n')
                continue
            if post['audio_download_url']:
                dl.run(post['audio_download_url'], out_file=file_name, out_dir=out_dir)
                sys.stdout.write('download mp3 {} done\n'.format(file_name))


class Mp3Batch(Mp3):
    """批量下载 mp3
    懒， 不想写参数了
    """
    def run(self, cfg: dict):
        if cfg['all']:
            try:
                dc = get_data_client(cfg)
            except:
                sys.stderr.write("ERROR: invalid geektime account or password\n"
                                 "Use '%s login --help' for  help.\n" % sys.argv[0].split(os.path.sep)[-1])
                return

            data = dc.get_course_list()
            cid_list = []
            for c in data['1']['list']:
                if c['had_sub']:
                    cid_list.append(c['id'])

        else:
            course_ids = cfg['course_ids']
            cid_list = course_ids.split(',')

        for cid in cid_list:
            args = cfg.copy()
            args['course_id'] = int(cid)
            super().run(args)

