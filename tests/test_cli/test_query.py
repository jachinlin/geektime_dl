# coding=utf8

import os
from geektime_dl.cli import query


def test_query(tmp_path, mocker):
    mocker.stub(name='sys.stdout.write')
    qr = query.Query()

    res = qr.work(args=[
        '-a={}'.format(os.getenv('account')),
        '-p={}'.format(os.getenv('password')),
        '--no-login'
    ])

    assert res
