# coding=utf8

import os
from geektime_dl.cli import mp4


def test_mp4(tmp_path, mocker):
    stub = mocker.stub(name='sys.stdout.write')
    cfg_file = tmp_path / 'test.cfg'
    cmd = mp4.Mp4()

    cmd.work(args=[
        '77', '--config', str(cfg_file), '--url-only',
        '-a={}'.format(os.getenv('account')),
        '-p={}'.format(os.getenv('password'))
    ])

    # assert stub
    cfg_file.unlink()
