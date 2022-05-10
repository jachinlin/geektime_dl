# coding=utf8

import os
import logging

from geektime_dl.utils import get_working_folder

LOG_PATH = str(get_working_folder() / 'geektime.log')
LOG_FORMAT = '\t'.join([
    'log_time=%(asctime)s',
    'levelname=%(levelname)s',
    '%(message)s',
    'location=%(pathname)s:%(lineno)d'])

level = logging.DEBUG if os.getenv('DEBUG') == '1' else logging.INFO
logger = logging.getLogger('geektime')
file_handler = logging.FileHandler(filename=LOG_PATH)

file_handler.setLevel(level)
file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
logger.setLevel(level)
logger.addHandler(file_handler)

