# coding=utf8

import os
import sys
import time
from multiprocessing import Pool

from geektime_dl.data_client import get_data_client
from geektime_dl.utils.ebook import Render as EbookRender
from . import Command
from ..utils.m3u8_downloader import Downloader


class Mp4(Command):
    """保存视频课程视频
    geektime mp4 -c <course_id> [--url-only] [--hd-only] [--output-folder=<output_folder>]

    `[]`表示可选，`<>`表示相应变量值

    course_id: 课程ID，可以从 query subcmd 查看
    --url-only: 只保存视频url
    --hd-only：下载高清视频，默认下载标清视频
    output_folder: 视频存放目录，默认当前目录

    notice: 此 subcmd 需要先执行 login subcmd
    e.g.: geektime mp4 -c 66 --output-folder=~/geektime-mp4
    """
    def run(self, cfg: dict):

        course_id = cfg['course_id']
        if not course_id:
            sys.stderr.write("ERROR: couldn't find the target course id\n")
            return

        out_dir = os.path.join(cfg['output_folder'], 'mp4')
        out_dir = os.path.expanduser(out_dir)
        if not os.path.isdir(out_dir):
            try:
                os.makedirs(out_dir)
            except OSError:
                sys.stderr.write("ERROR: couldn't create the output folder {}\n".format(out_dir))
                return

        url_only = cfg['url_only']
        hd_only = cfg['hd_only']
        workers = cfg['workers']

        try:
            dc = get_data_client(cfg)
        except:
            sys.stderr.write("ERROR: invalid geektime account or password\n"
                             "Use '%s login --help' for  help.\n" % sys.argv[0].split(os.path.sep)[-1])
            return

        course_data = dc.get_course_intro(course_id)

        if int(course_data['column_type']) != 3:
            raise Exception('该课程不是视频课程:%s' % course_data['column_title'])

        out_dir = os.path.join(out_dir, course_data['column_title'])
        if not os.path.isdir(out_dir):
            os.makedirs(out_dir)

        sys.stdout.write('doing ......\n')
        data = dc.get_course_content(course_id)
        if url_only:
            title = EbookRender.format_file_name(course_data['column_title'])
            with open(os.path.join(out_dir, '%s.mp4.txt' % title), 'w') as f:

                f.write('\n'.join(["{}:\n{}\n{}\n\n".format(
                    EbookRender.format_file_name(post['article_title']),
                    post['video_media_map'].get('hd', {}).get('url'),
                    post['video_media_map'].get('sd', {}).get('url')
                ) for post in data]))
            sys.stdout.write('download {} mp4 url done\n'.format(title))
            return

        dl = Downloader()
        p = Pool(workers)
        start = time.time()
        for post in data:
            file_name = EbookRender.format_file_name(post['article_title']) + ('.hd' if hd_only else '.sd')
            if os.path.isfile(os.path.join(out_dir, file_name) + '.ts'):
                sys.stdout.write(file_name + ' exists\n')
                continue
            if hd_only:  # some post has sd mp4 only
                url = post['video_media_map'].get('hd', {}).get('url') or post['video_media'].get(
                    'sd', {}).get('url')
            else:
                url = post['video_media_map'].get('sd', {}).get('url')

            p.apply_async(dl.run, (url, out_dir, file_name))

        p.close()
        p.join()
        sys.stdout.write('download {} done, cost {}s\n'.format(course_data['column_title'], int(time.time() - start)))


class Mp4Batch(Mp4):
    """批量下载 mp4
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
            for c in data['3']['list']:
                if c['had_sub']:
                    cid_list.append(str(c['id']))

        else:
            course_ids = cfg['course_ids']
            cid_list = course_ids.split(',')

        for cid in cid_list:
            args = cfg.copy()
            args['course_id'] = int(cid)
            super().run(args)
