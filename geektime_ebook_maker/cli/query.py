# coding=utf8

import sys
from ..gk_apis import *
from . import Command


class Query(Command):
    """查看课程列表
    geektime query

    notice: 此 subcmd 需要先执行 login subcmd
    e.g.: geektime query
    """
    def run(self, args):
        gk = GkApiClient()
        if not gk.cookies:
            login_now = input("尚未登录，是否现在登录(Y/N): ")
            if login_now.strip().upper() == 'Y':
                area = '86'
                account = input("enter your registered account(phone): ")
                password = input("enter password: ")

                gk.login(account, password, area)
                print('登录成功')

        data = gk.get_course_list()

        result_str = ''
        for i in ['1', '2', '3', '4']:
            columns = data[i]['list']
            result_str += {'1': '专栏', '2': '微课', '3': '视频', '4': '其他'}[i] + '\n'
            result_str += "\t{:<12}{:<10}{}\t\t{}\n".format('课程ID', '已订阅', '课程标题', '更新频率/课时·时长')
            for c in columns:
                result_str += "\t{:<15}{:<10}{}\t({})\n".format(
                    str(c['id']), '是' if c['had_sub'] else '否', c['column_title'], c['update_frequency'] or None
                )

        print(result_str)

