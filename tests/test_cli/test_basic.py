# coding=utf8

import pytest

from geektime_dl.cli import command


def test_command_type():
    class MyCMD(metaclass=command.CommandType):
        pass

    assert MyCMD.name == 'mycmd'
    assert MyCMD.name in command.commands
    assert command.commands[MyCMD.name] is MyCMD


def test_command_of_help():
    Help = command.commands[command.Help.name]
    result = Help().work(args=[])
    assert "Available commands:" in result


# test command base class
def test_add_argument_basic():
    class ArgsParse(command.Command):
        @command.add_argument("-n", "--name", dest="name")
        def run(self, cfg):
            return cfg

    cmd = ArgsParse()
    args = cmd.work([])
    assert isinstance(args, dict)
    assert 'name' in args and args['name'] is None

    args = cmd.work(['--name', 'geektime'])
    assert isinstance(args, dict)
    assert 'name' in args and args['name'] == 'geektime'


def test_add_argument_required():
    class ArgsParse(command.Command):
        @command.add_argument("-n", "--name", dest="name", required=True)
        def run(self, cfg):
            return cfg

    cmd = ArgsParse()
    with pytest.raises(SystemExit):
        cmd.work([])


def test_add_argument_save(tmp_path):
    class ArgsParse(command.Command):
        @command.add_argument("-n", "--name", dest="name", save=True)
        def run(self, cfg):
            return cfg

    # default
    cfg_file = tmp_path / 'test.cfg'
    cmd = ArgsParse()
    cmd.work(['--config', str(cfg_file)])
    args = command.Command.load_cfg(str(cfg_file))
    assert set(args.keys()) == {'area', 'output_folder'}

    # will save name=geektime to cfg_file
    cmd.work(['--config', str(cfg_file), '-n=geektime'])
    args = command.Command.load_cfg(str(cfg_file))
    assert 'name' in args and args['name'] == 'geektime'

    # retrieve name=geektime in cfg_file
    cmd.work(['--config', str(cfg_file)])
    args = command.Command.load_cfg(str(cfg_file))
    assert 'name' in args and args['name'] == 'geektime'

    cfg_file.unlink()


def test_parse_course_ids():
    ids = '1'
    ids2 = '1-3'
    ids3 = '3,6-8'
    assert command.Command.parse_course_ids(ids) == [1]
    assert command.Command.parse_course_ids(ids2) == [1, 2, 3]
    assert command.Command.parse_course_ids(ids3) == [3, 6, 7, 8]
