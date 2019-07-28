# coding=utf8

from geektime_dl.data_client.gk_apis import GkApiClient


def test_api_get_course_list(gk: GkApiClient):
    res = gk.get_course_list()

    assert isinstance(res, dict)
    assert {'1', '2', '3', '4'} & set(res.keys())
    for type_ in {'1', '2', '3', '4'}:
        course_list = res[type_]['list']
        course = course_list[0]
        assert isinstance(course, dict)
        for key in  {'id', 'column_title', 'had_sub', 'is_finish', 'update_frequency'}:
            assert course.get(key) is not None, '{} 不存在'.format(key)


def test_api_get_course_intro(gk: GkApiClient):
    course = gk.get_course_intro(48)
    assert isinstance(course, dict)
    for key in {'id', 'column_title', 'had_sub', 'is_finish', 'update_frequency'}:
        assert course.get(key) is not None, '{} 不存在'.format(key)


def test_api_get_course_post_list(gk: GkApiClient):
    course = gk.get_post_list_of(48)
    assert course and isinstance(course, list)
    article = course[0]
    for key in {'id'}:
        assert article.get(key) is not None, '{} 不存在'.format(key)


def test_api_get_post_content(gk: GkApiClient):
    article = gk.get_post_content(333)
    assert article and isinstance(article, dict)
    for key in {'id', 'article_title', 'article_content', 'column_id'}:
        assert article.get(key) is not None, '{} 不存在'.format(key)

    # mp3
    assert article.get('audio_download_url')
    # mp4
    article = gk.get_post_content(2184)
    vm = article.get('video_media_map')
    assert vm, 'video_media_map 不存在'
    assert vm['sd']['url']
    assert vm['hd']['url']


def test_api_get_post_comments(gk: GkApiClient):
    res = gk.get_post_comments(109572)
    assert res and isinstance(res, list)
    comment = res[0]
    for key in {'user_name', 'like_count', 'comment_content', 'comment_ctime'}:
        assert comment.get(key) is not None, '{} 不存在'.format(key)
