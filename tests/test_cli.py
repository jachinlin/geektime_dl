# coding=utf8

from geektime_dl.cli import command


def test_command_metaclass1():
    assert command.Help.name == 'help'
    assert command.Help.name in command.commands


def test_command_metaclass2():
    assert command.Help.name in command.commands


def test_command_metaclass3():
    assert command.commands[command.Help.name] == command.Help


def test_command_metaclass4():
    Help = command.commands[command.Help.name]
    result = Help().run(cfg=None)
    assert "Available commands:" in result
