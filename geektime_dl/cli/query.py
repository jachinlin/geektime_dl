# coding=utf8

import sys
import os

from geektime_dl.data_client import get_data_client
from . import Command


_course_map = {
    '1': '专栏', '2': '微课', '3': '视频', '4': '其他'
}


class Query(Command):
    """查看课程列表
    geektime query

    notice: 此 subcmd 需要先执行 login subcmd
    e.g.: geektime query
    """
    def run(self, cfg: dict):
        try:
            dc = get_data_client(cfg)
        except Exception:
            sys.stderr.write(
                "ERROR: invalid geektime account or password\n"
                "Use '{} login --help' for  help.\n".format(
                    sys.argv[0].split(os.path.sep)[-1]))
            return

        data = dc.get_course_list()

        result_str = ''
        for i in ['1', '2', '3', '4']:
            columns = data[i]['list']
            result_str += _course_map[i] + '\n'
            result_str += "\t{:<12}{}\t{}\t{:<10}\n".format(
                '课程ID', '已订阅', '已完结', '课程标题')
            for c in columns:
                is_finished = c['update_frequency'] == '全集' or c['is_finish']
                result_str += "\t{:<15}{}\t{}\t{:<10}\n".format(
                    str(c['id']),
                    '是' if c['had_sub'] else '否',
                    '是' if is_finished else '否',
                    c['column_title'],

                )

        sys.stdout.write(result_str)

