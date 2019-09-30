# coding=utf8

import os
from geektime_dl.cli import mp4


def test_mp4(tmp_path, mocker, video_course_id):
    stub = mocker.stub(name='sys.stdout.write')
    cfg_file = tmp_path / 'test.cfg'
    cmd = mp4.Mp4()

    if not os.getenv('account'):
        cmd.work(args=[
            str(video_course_id),
            '-a=0',
            '-p=0',
            '--output-folder', str(tmp_path),
            '--config', str(cfg_file),
            '--url-only',
            '--no-login'
        ])
    else:
        cmd.work(args=[
            str(video_course_id),
            '-a={}'.format(os.getenv('account')),
            '-p={}'.format(os.getenv('password')),
            '--output-folder', str(tmp_path),
            '--config', str(cfg_file),
            '--url-only',
        ])

    mp4_txt = tmp_path / 'mp4' / '微服务架构核心20讲' / '微服务架构核心20讲.mp4.txt'
    assert mp4_txt.is_file()
