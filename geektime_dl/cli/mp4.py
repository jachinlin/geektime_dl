# coding=utf8

import os
import json
import time
from multiprocessing import Pool
from geektime_dl.data_client import DataClient
from . import Command
from ..utils.m3u8_downloader import Downloader
from ..utils import format_path


class Mp4(Command):
    """保存视频课程视频
    geektime mp4 <course_id> [--url-only] [--hd-only] [--out-dir=<out_dir>]

    `[]`表示可选，`<>`表示相应变量值

    course_id: 课程ID，可以从 query subcmd 查看
    --url-only: 只保存视频url
    --hd-only：下载高清视频，默认下载标清视频
    --out_dir: 视频存放目录，默认当前目录

    notice: 此 subcmd 需要先执行 login subcmd
    e.g.: geektime mp4 66 --out-dir=~/geektime-ebook
    """
    def run(self, args):

        course_id = args[0]
        url_only = '--url-only' in args[1:]
        hd_only = '--hd-only' in args[1:]
        for arg in args[1:]:
            if '--out-dir=' in arg:
                out_dir = arg.split('--out-dir=')[1] or './mp4'
                break
        else:
            out_dir = './mp4'

        for arg in args[1:]:
            if '--workers=' in arg:
                workers = int(arg.split('--workers=')[1]) or 1
                break
        else:
            workers = 1

        if not os.path.isdir(out_dir):
            os.makedirs(out_dir)

        dc = DataClient()

        course_data = dc.get_course_intro(course_id)

        if int(course_data['column_type']) != 3:
            raise Exception('该课程不是视频课程:%s' % course_data['column_title'])

        out_dir = os.path.join(out_dir, course_data['column_title'])
        if not os.path.isdir(out_dir):
            os.makedirs(out_dir)

        data = dc.get_course_content(course_id)

        if url_only:
            with open(os.path.join(out_dir, '%s.mp4.txt' % course_data['column_title']), 'w') as f:

                f.write('\n'.join(["{}:\n{}\n{}\n\n".format(
                    post['article_title'],
                    json.loads(post['video_media']).get('hd', {}).get('url'),
                    json.loads(post['video_media']).get('sd', {}).get('url')
                ) for post in data]))
            print("download mp4 url done: " + course_data['column_title'])
            return

        dl = Downloader()
        p = Pool(workers)
        start = time.time()
        for post in data:
            file_name = format_path(post['article_title'] + ('.hd' if hd_only else '.sd'))
            if os.path.isfile(os.path.join(out_dir, file_name) + '.ts'):
                print(file_name + ' exists')
                continue
            if hd_only:  # some post has sd mp4 only
                url = json.loads(post['video_media']).get('hd', {}).get('url') or json.loads(post['video_media']).get(
                    'sd', {}).get('url')
            else:
                url = json.loads(post['video_media']).get('sd', {}).get('url')

            p.apply_async(dl.run, (url, out_dir, file_name))

        p.close()
        p.join()
        print('download {} done, cost {}s\n'.format(course_data['column_title'], int(time.time() - start)))


class Mp4Batch(Mp4):
    """批量下载 mp4
    懒， 不想写参数了
    """
    def run(self, args):

        if '--all' in args:
            dc = DataClient()
            data = dc.get_course_list()
            cid_list = []
            for c in data['3']['list']:
                if c['had_sub']:
                    cid_list.append(str(c['id']))

        else:
            course_ids = args[0]
            cid_list = course_ids.split(',')

        for cid in cid_list:
            super(Mp4Batch, self).run([cid.strip()] + args)
