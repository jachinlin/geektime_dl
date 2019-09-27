# coding=utf8

import os
from geektime_dl.cli import ebook
from geektime_dl.utils import Singleton


def setup_function(func):
    Singleton.clear_singletons()


def test_ebook(tmp_path, mocker):
    stub = mocker.stub(name='sys.stdout.write')
    cfg_file = tmp_path / 'test.cfg'
    cmd = ebook.EBook()

    cmd.work(args=[
        '234', '--config', str(cfg_file),
        '-a={}'.format(os.getenv('account')),
        '-p={}'.format(os.getenv('password'))
    ])

    # assert stub
    cfg_file.unlink()
