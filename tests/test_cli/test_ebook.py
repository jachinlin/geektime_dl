# coding=utf8

import os
from geektime_dl.cli import ebook
from geektime_dl.utils import Singleton


def setup_function(func):
    Singleton.clear_singletons()


def test_ebook(tmp_path, mocker, column_id):
    mocker.stub(name='sys.stdout.write')
    cfg_file = tmp_path / 'test.cfg'
    cmd = ebook.EBook()

    if not os.getenv('account'):
        cmd.work(args=[
            str(column_id),
            '-a=0',
            '-p=0',
            '--output-folder', str(tmp_path),
            '--config', str(cfg_file),
            '--no-login'
        ])
    else:
        cmd.work(args=[
            str(column_id),
            '-a={}'.format(os.getenv('account')),
            '-p={}'.format(os.getenv('password')),
            '--output-folder', str(tmp_path),
            '--config', str(cfg_file),
        ])

    mobi = tmp_path / 'ebook' / '朱赟的技术管理课[免费试读].mobi'
    assert mobi.is_file()
