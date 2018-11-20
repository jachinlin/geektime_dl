# coding=utf8

from ..gk_apis import *
from ..store_client import StoreClient
from . import Command


class Mp4(Command):
    def run(self, args):

        course_id = args[0]
        url_only = args[1] == '--url-only' if len(args) >= 2 else False
        gk = GkApiClient()
        store_client = StoreClient()

        data = gk.get_course_intro(course_id)
        store_client.save_column_info(**data)

        data = gk.get_course_content(course_id)

        for post in data:
            post_detail = gk.get_post_content(post['id'])
            store_client.save_post_content(**post_detail)

        if url_only:
            with open('mp4.txt', 'w') as f:
                # TODO alignment
                f.write('\n'.join(
                    ["{}:\t\t{}".format(post['article_title'], json.loads(post['video_media'])['hd']['url']) for post in data])
                )





