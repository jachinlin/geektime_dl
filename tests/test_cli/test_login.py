# coding=utf8

import os
import builtins
import time

import pytest

from geektime_dl.cli import login
from geektime_dl.data_client.gk_apis import GkApiError
from geektime_dl.utils import Singleton


def setup_function(func):
    Singleton.clear_singletons()


def test_login(tmp_path, mocker):
    cfg_file = tmp_path / 'test.cfg'
    lg = login.Login()
    with mocker.patch.object(builtins, 'input', return_value='xx'):
        # failed
        with pytest.raises(GkApiError):
            lg.work(args=['--config', str(cfg_file)])

        # succ
        if os.getenv('account'):
            lg.work(args=[
                '--config', str(cfg_file),
                '-a={}'.format(os.getenv('account')),
                '-p={}'.format(os.getenv('password'))
            ])
            cfg = lg.load_cfg(str(cfg_file))
            assert 'account' in cfg and cfg['account'] == os.getenv('account')

