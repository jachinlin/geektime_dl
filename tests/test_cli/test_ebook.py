# coding=utf8

from geektime_dl.cli import ebook
from geektime_dl.utils import Singleton


def setup_function(func):
    Singleton.clear_singletons()


def test_ebook(tmp_path, mocker, column_id):
    mocker.stub(name='sys.stdout.write')
    cmd = ebook.EBook()

    cmd.work(args=[
        str(column_id),
        '-a=0',
        '-p=0',
        '--output-folder', str(tmp_path),
        '--no-login'
    ])

    # todo
    # mobi = tmp_path / '朱赟的技术管理课[免费试读].mobi'
    # assert mobi.exists()
