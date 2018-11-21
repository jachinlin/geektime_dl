# coding=utf8

from ..gk_apis import *
from ..store_client import StoreClient
from ..mp3_downloader import Downloader
from . import Command


class Mp3(Command):
    def run(self, args):

        course_id = args[0]
        url_only = '--url-only' in args[1:]
        for arg in args[1:]:
            if '--out-dir=' in arg:
                out_dir = arg.split('--out-dir=')[1] or '.'
                break
        else:
            out_dir = '.'
        if not os.path.isdir(out_dir):
            os.makedirs(out_dir)

        gk = GkApiClient()
        store_client = StoreClient()

        course_data = gk.get_course_intro(course_id)

        store_client.save_column_info(**course_data)

        if int(course_data['column_type']) != 1:
            raise Exception('该课程不提供音频:%s' % course_data['column_title'])

        data = []
        _data = gk.get_course_content(course_id)

        for post in _data:
            post_detail = gk.get_post_content(post['id'])
            data.append(post_detail)
            store_client.save_post_content(**post_detail)

        if url_only:
            with open(os.path.join(out_dir, '%s.mp3.txt' % course_data['column_title']), 'w') as f:
                # TODO alignment
                f.write('\n'.join(["{}:\t\t{}".format(post['article_title'], post['audio_download_url']) for post in data]))

            return

        dl = Downloader()
        for post in data:
            file_name = post['article_title'] + '.mp3'
            if os.path.isfile(os.path.join(out_dir, file_name)):
                print(file_name + ' exists')
                continue
            if post['audio_download_url']:
                dl.run(post['audio_download_url'], out_file=file_name, out_dir=out_dir)
                print('download mp3 done: ' + file_name)




