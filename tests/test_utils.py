# coding=utf8

from geektime_dl.utils import (
    get_working_folder,
    parse_column_ids,
)
from geektime_dl import log


def test_logging():
    log.logger.info('guess where i will be ')

    log_file = get_working_folder() / 'geektime.log'
    with open(log_file) as f:
        logs = f.read()
        assert 'guess where i will be ' in logs
        assert 'INFO' in logs


def test_parse_column_ids():
    ids = '1'
    ids2 = '1-3'
    ids3 = '3,6-8'
    assert parse_column_ids(ids) == [1]
    assert parse_column_ids(ids2) == [1, 2, 3]
    assert parse_column_ids(ids3) == [3, 6, 7, 8]
