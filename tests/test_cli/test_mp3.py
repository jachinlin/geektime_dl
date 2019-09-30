# coding=utf8

import os
from geektime_dl.cli import mp3


def test_mp3(tmp_path, mocker, column_id):
    stub = mocker.stub(name='sys.stdout.write')
    cfg_file = tmp_path / 'test.cfg'
    cmd = mp3.Mp3()

    if not os.getenv('account'):
        cmd.work(args=[
            str(column_id),
            '-a=0',
            '-p=0',
            '--output-folder', str(tmp_path),
            '--config', str(cfg_file),
            '--url-only',
            '--no-login'
        ])
    else:
        cmd.work(args=[
            str(column_id),
            '-a={}'.format(os.getenv('account')),
            '-p={}'.format(os.getenv('password')),
            '--output-folder', str(tmp_path),
            '--config', str(cfg_file),
            '--url-only',
        ])

    mp3_txt = tmp_path / 'mp3' / '朱赟的技术管理课' / '朱赟的技术管理课.mp3.txt'
    assert mp3_txt.is_file()
