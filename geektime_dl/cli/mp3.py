# coding=utf8

import os
from geektime_dl.data_client import DataClient
from ..utils.mp3_downloader import Downloader
from . import Command
from ..utils import format_path
from ..geektime_ebook import maker
import time
from configparser import ConfigParser

class Mp3(Command):
    """保存专栏音频
    eektime mp3 <course_id>
    course_id: 课程ID，可以从 query subcmd 查看
    """
    def __init__(self):
        cfg = ConfigParser()
        cfg.read('config.ini')
        self.mp3_out_dir = cfg.get('output','mp3_out_dir') 

    def run(self, args):

        course_id = args[0]
        out_dir = self.mp3_out_dir

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

        dl = Downloader()
        for post in data:
            file_name = maker.format_file_name(post['article_title'] + '.mp3')
            if os.path.isfile(os.path.join(out_dir, file_name)):
                print(file_name + ' exists')
                continue
            if post['audio_download_url']:
                dl.run(post['audio_download_url'], out_file=file_name, out_dir=out_dir)
                print('download mp3 done: ' + file_name)
            time.sleep(1)
        

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
            time.sleep(5)

