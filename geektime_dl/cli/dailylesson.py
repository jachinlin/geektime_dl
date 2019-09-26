# coding=utf8

from geektime_dl.cli import Command


class Daily(Command):
    """保存每日一课视频
    geektime daily -v <video_id> [--url-only] [--hd-only] \
    [--output-folder=<output_folder>]

    `[]`表示可选，`<>`表示相应变量值

    --url-only: 只保存视频url
    --hd-only：下载高清视频，默认下载标清视频
    output_folder: 视频存放目录，默认当前目录
    """
    def run(self, cfg: dict):  # noqa: C901

        pass
