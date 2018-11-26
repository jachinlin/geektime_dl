# coding=utf8

import os
from geektime_dl.data_client.gk_apis import GkApiClient

gk = GkApiClient()


def test_api_login():
    gk.login(os.getenv('account'), os.getenv('password'))


def test_api_get_course_list():
    gk.get_course_list()


def test_api_get_course_intro():
    gk.get_course_intro(48)


def test_api_get_course_content():
    gk.get_course_content(48)


def test_api_get_post_content():
    gk.get_post_content('333')
