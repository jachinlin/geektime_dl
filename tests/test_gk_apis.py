# coding=utf8

from geektime_dl.data_client.gk_apis import GkApiClient


def test_api_get_course_list(gk: GkApiClient):
    gk.get_course_list()


def test_api_get_course_intro(gk: GkApiClient):
    gk.get_course_intro(48)


def test_api_get_course_content(gk: GkApiClient):
    gk.get_course_content(48)


def test_api_get_post_content(gk: GkApiClient):
    gk.get_post_content(333)


