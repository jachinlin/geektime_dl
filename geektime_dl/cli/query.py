# coding=utf8

import sys

from geektime_dl.cli import Command, add_argument

_COLUMN_INDEX = "1"


class Query(Command):
    """查看专栏列表"""

    @add_argument("--no-cache", dest="no_cache", action='store_true',
                  default=False, help="do not use the cache data")
    def run(self, cfg: dict):

        dc = self.get_data_client(cfg)

        data = dc.get_column_list(no_cache=cfg['no_cache'])

        result_str = ''
        columns = data[_COLUMN_INDEX]['list']
        result_str += '专栏\n'
        result_str += "\t{:<12}{}\t{}\t{:<10}\n".format(
            '课程ID', '已订阅', '已完结', '课程标题')
        for c in columns:
            is_finished = self.is_course_finished(c)
            result_str += "\t{:<15}{}\t{}\t{:<10}\n".format(
                str(c['id']),
                '是' if c['had_sub'] else '否',
                '是' if is_finished else '否',
                c['column_title'],

            )

        sys.stdout.write(result_str)
        return result_str

