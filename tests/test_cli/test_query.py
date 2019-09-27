# coding=utf8

import os
from geektime_dl.cli import query


def test_query(tmp_path, mocker):
    stub = mocker.stub(name='sys.stdout.write')
    cfg_file = tmp_path / 'test.cfg'
    qr = query.Query()

    qr.work(args=[
        '--config', str(cfg_file),
        '-a={}'.format(os.getenv('account')),
        '-p={}'.format(os.getenv('password'))
    ])

    # assert stub
    cfg_file.unlink()
