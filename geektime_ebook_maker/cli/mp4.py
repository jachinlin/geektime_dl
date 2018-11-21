# coding=utf8

from ..gk_apis import *
from ..store_client import StoreClient
from . import Command
from ..utils.m3u8_downloader import Downloader


class Mp4(Command):
    """保存视频课程视频
    geektime mp4 <course_id> [--url-only] [--hd-only] [--out-dir=xxx]

    course_id: 课程ID，可以从 query subcmd 查看
    --url-only: 只保存视频url
    --hd-only：下载高清视频，默认下载标清视频
    --out_dir: 视频存放目录，默认当前目录

    notice: 此 subcmd 需要先执行 login subcmd
    e.g.: geektime mp4 66 --out-dir=~/geektime-ebook
    """
    def run(self, args):

        course_id = args[0]
        url_only = '--url-only' in args[1:]
        hd_only = '--hd-only' in args[1:]
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

        if int(course_data['column_type']) != 3:
            raise Exception('该课程不是视频课程:%s' % course_data['column_title'])

        out_dir = os.path.join(out_dir, course_data['column_title'])
        if not os.path.isdir(out_dir):
            os.makedirs(out_dir)

        data = gk.get_course_content(course_id)

        for post in data:
            post_detail = gk.get_post_content(post['id'])
            store_client.save_post_content(**post_detail)

        if url_only:
            with open(os.path.join(out_dir, '%s.mp4.txt' % course_data['column_title']), 'w') as f:
                # TODO alignment
                f.write('\n'.join(
                    ["{}:\t\t{}".format(
                        post['article_title'],
                        json.loads(post['video_media'])['hd']['url'] if hd_only else json.loads(post['video_media'])['sd']['url']
                    ) for post in data])
                )
            return

        for post in data:
            file_name = post['article_title'] + ('.hd' if hd_only else '.sd')
            if os.path.isfile(os.path.join(out_dir, file_name) + '.ts'):
                print(file_name + ' exists')
                continue
            url = json.loads(post['video_media'])['hd']['url'] if hd_only else json.loads(post['video_media'])['sd']['url']
            dl = Downloader(1)
            dl.run(url, dir=out_dir, file_name=file_name)





