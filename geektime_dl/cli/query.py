# coding=utf8

import sys

from geektime_dl.cli import Command


_course_map = {
    '1': '专栏', '2': '微课', '3': '视频', '4': '其他'
}


class Query(Command):
    """查看课程列表"""

    def run(self, cfg: dict):

        dc = self.get_data_client(cfg)

        data = dc.get_course_list()

        result_str = ''
        for i in ['1', '2', '3', '4']:
            columns = data[i]['list']
            result_str += _course_map[i] + '\n'
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

