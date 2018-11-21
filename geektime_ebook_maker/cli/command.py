# coding=utf8

import sys
import os
import traceback
from ..utils.logging import logger


commands = {}


class CommandType(type):
    def __init__(cls, name, bases, attrs):
        super(CommandType, cls).__init__(name, bases, attrs)
        name = getattr(cls, name, cls.__name__.lower())
        cls.name = name
        if name != 'command':
            commands[name] = cls


Command = CommandType('Command', (object,), {'run': lambda self, args: None})


class Help(Command):
    """Display the list of available commands"""
    def run(self, args):
        result = ["Available commands:"]
        names = list(commands)
        padding = max([len(k) for k in names]) + 2
        for k in sorted(names):
            name = k.ljust(padding, ' ')
            doc = (commands[k].__doc__ or '').strip()
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
            o.run(args)
        except Exception as e:
            print(e)
            logger.error('exception=%s' % traceback.format_exc())
    else:
        print('Unknow command %r\n\n' % (command,))
