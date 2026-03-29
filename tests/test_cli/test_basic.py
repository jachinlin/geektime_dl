# coding=utf8
"""
测试 CLI 基础功能
"""

from click.testing import CliRunner

from geektime_dl.cli.main import cli


def test_cli_help():
    """测试 CLI 帮助信息"""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "极客时间下载工具" in result.output
    assert "login" in result.output
    assert "query" in result.output
    assert "download" in result.output
    assert "ebook" in result.output


def test_login_help():
    """测试 login 命令帮助"""
    runner = CliRunner()
    result = runner.invoke(cli, ["login", "--help"])
    assert result.exit_code == 0
    assert "验证账号密码" in result.output
    assert "--account" in result.output
    assert "--password" in result.output


def test_query_help():
    """测试 query 命令帮助"""
    runner = CliRunner()
    result = runner.invoke(cli, ["query", "--help"])
    assert result.exit_code == 0
    assert "查询课程列表" in result.output


def test_download_help():
    """测试 download 命令帮助"""
    runner = CliRunner()
    result = runner.invoke(cli, ["download", "--help"])
    assert result.exit_code == 0
    assert "下载课程到 SQLite" in result.output
    assert "COURSE_IDS" in result.output


def test_ebook_help():
    """测试 ebook 命令帮助"""
    runner = CliRunner()
    result = runner.invoke(cli, ["ebook", "--help"])
    assert result.exit_code == 0
    assert "制作课程电子书" in result.output
    assert "--output-folder" in result.output


def test_login_no_args(mocker):
    """测试 login 命令无参数时的提示"""
    # Mock the GeektimeClient to avoid real API calls
    mock_client = mocker.patch('geektime_dl.cli.login.GeektimeClient')
    mock_client.return_value.login.return_value = {"session_id": "test123"}

    runner = CliRunner()
    # 不提供参数应该会提示输入，这里我们只检查不崩溃
    result = runner.invoke(cli, ["login"], input="testaccount\ntestpassword\n\n")

    assert result.exit_code == 0
    assert "验证成功！" in result.output


def test_login_authentication_error(mocker):
    """测试 login 命令处理认证错误"""
    from geektime_dl.api import AuthenticationError

    # Mock the GeektimeClient to raise AuthenticationError
    mock_client = mocker.patch('geektime_dl.cli.login.GeektimeClient')
    mock_client.return_value.login.side_effect = AuthenticationError("Invalid account or password")


    runner = CliRunner()
    result = runner.invoke(cli, ["login", "-a", "test", "-p", "wrong"])

    assert result.exit_code != 0
    assert "验证失败" in result.output
    assert "Invalid account or password" in result.output



def test_query_no_credentials():
    """测试 query 命令不提供凭证"""
    runner = CliRunner()
    result = runner.invoke(cli, ["query"])
    assert result.exit_code != 0
    assert "错误" in result.output
    assert "账号" in result.output


def test_download_no_credentials():
    """测试 download 命令不提供凭证"""
    runner = CliRunner()
    result = runner.invoke(cli, ["download", "123"])
    assert result.exit_code != 0
    assert "错误" in result.output


def test_ebook_no_credentials():
    """测试 ebook 命令不提供凭证"""
    runner = CliRunner()
    result = runner.invoke(cli, ["ebook", "123"])
    assert result.exit_code != 0
    assert "错误" in result.output
