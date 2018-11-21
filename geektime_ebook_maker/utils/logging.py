# coding=utf8

import logging

LOG_PATH = './geektime.log'
LOG_FORMAT = '\t'.join([
    'log_time=%(asctime)s',
    'levelname=%(levelname)s',
    'process=%(process)d',
    '%(message)s',
    'location=%(pathname)s:%(lineno)d\n'])

logger = logging.getLogger('geektime')
file_handler = logging.FileHandler(filename=LOG_PATH)

file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)

