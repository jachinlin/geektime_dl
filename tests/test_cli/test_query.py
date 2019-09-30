# coding=utf8

import os
from geektime_dl.cli import query


def test_query(tmp_path, mocker):
    stub = mocker.stub(name='sys.stdout.write')
    cfg_file = tmp_path / 'test.cfg'
    qr = query.Query()

    if not os.getenv('account'):
        res = qr.work(args=[
            '--config', str(cfg_file),
            '-a={}'.format(os.getenv('account')),
            '-p={}'.format(os.getenv('password')),
            '--no-login'
        ])
    else:
        res = qr.work(args=[
            '--config', str(cfg_file),
            '-a={}'.format(os.getenv('account')),
            '-p={}'.format(os.getenv('password'))
        ])

    assert res
