# coding=utf8

import sys
import os
import traceback
from ..utils._logging import logger


commands = {}


class CommandType(type):
    def __init__(cls, name, bases, attrs):
        super(CommandType, cls).__init__(name, bases, attrs)
        name = getattr(cls, name, cls.__name__.lower())
        cls.name = name
        if name != 'command':
            commands[name] = cls


def work(self, args):
    if '--help' in args:
        result = (self.__doc__ or '').strip()
        print(result)
        return
    return self.run(args)


Command = CommandType('Command', (object,), {'run': lambda self, args: None, 'work': work})


class Help(Command):
    """Display the list of available commands"""
    def run(self, args):
        result = ["Available commands:"]
        names = list(commands)
        padding = max([len(k) for k in names]) + 2
        for k in sorted(names):
            name = k.ljust(padding, ' ')
            doc = (commands[k].__doc__ or '').split('\n')[0]
            result.append("    %s%s" % (name, doc))
        result.append("\nUse '%s <command> --help' for individual command help." % sys.argv[0].split(os.path.sep)[-1])

        result = '\n'.join(result)
        print(result)
        return result


def main():
    args = sys.argv[1:]

    # default subcommand
    command = Help.name

    # subcommand discovery
    if len(args):
        command = args[0]
        args = args[1:]

    if command in commands:
        o = commands[command]()
        try:
            o.work(args)
        except Exception as e:
            tb = traceback.format_exc()
            if isinstance(e, IndexError) and 'args' in tb:
                # 这个定位有点广了，可能会误杀
                # 当然，我对自己代码比较有信心，其他地方都不会出现index越界的情况
                # 笔芯
                print("参数出错，具体使用方法见下\n")
                print(o.__doc__)
            else:
                print(e)
            logger.error('exception=%s' % tb)
    else:
        print('Unknow command %r\n\n' % (command,))
