from pathlib import Path
from unittest import mock

import pytest

from riposte import Riposte, input_streams
from riposte.command import Command
from riposte.exceptions import CommandError, RiposteException


@mock.patch("riposte.riposte.readline")
def test_setup_history_w_libedit(mocked_readline, history_file):
    mocked_readline.__doc__ = "foo libedit bar"
    Riposte(history_file=history_file, history_length=10)
    with open(history_file) as f:
        assert f.read() == "_HiStOrY_V2_\n\n"


@mock.patch("riposte.riposte.readline")
def test_setup_history(mocked_readline, history_file):
    mocked_readline.__doc__ = "Some other doc-string"
    Riposte(history_file=history_file, history_length=10)
    with open(history_file) as f:
        assert f.read() == ""


def test_command(repl: Riposte):
    @repl.command(name="foo", description="scoobeedoo")
    def foo():
        pass

    assert repl._commands == {"foo": Command("foo", foo, "scoobeedoo")}

    @repl.command(name="bar")
    def bar():
        pass

    assert repl._commands == {
        "foo": Command("foo", foo, "scoobeedoo"),
        "bar": Command("bar", bar, ""),
    }


def test_command_duplicated_command(repl: Riposte, foo_command):
    with pytest.raises(RiposteException):

        @repl.command(name="foo")
        def bar():
            pass


@pytest.mark.parametrize(
    ["raw_line", "parsed_line"],
    [
        ("scoo bee doo", ["scoo", "bee", "doo"]),
        ("  scoo  bee  doo  ", ["scoo", "bee", "doo"]),
        ("\tscoo\tbee\tdoo\n", ["scoo", "bee", "doo"]),
        ("", []),
        ("  \t\n", []),
    ],
)
def test_parse_line(raw_line, parsed_line, repl: Riposte):
    assert repl._parse_line(raw_line) == parsed_line


@pytest.mark.parametrize(
    "invalid_line", ("'scoo", "scoo'", '"scoo', 'scoo"', "'scoo\"", "\"scoo'")
)
def test_parse_line_no_closing_quotation(invalid_line, repl: Riposte):
    with pytest.raises(RiposteException):
        repl._parse_line(invalid_line)


def test_get_command(repl: Riposte, foo_command):
    assert repl._get_command("foo") == foo_command


def test_get_command_handler_no_handling_function(repl: Riposte):
    with pytest.raises(RiposteException):
        repl._get_command("bar")


def test_complete(repl: Riposte, foo_command: Command):
    @repl.complete(foo_command.name)
    def complete_foo(*_):
        pass

    assert foo_command._completer_function is complete_foo


def test_complete_not_registered(repl: Riposte):
    with pytest.raises(RiposteException):

        @repl.complete("foo")
        def complete_foo(*_):
            pass


def test_complete_already_attached(repl: Riposte, foo_command: Command):
    with pytest.raises(RiposteException):

        @repl.complete("foo")
        def complete_foo_alpha(*_):
            pass

        @repl.complete("foo")
        def complete_foo_bravo(*_):
            pass


@pytest.mark.parametrize(
    ("input", "expected"),
    (
        ("foo bar baz", ["foo bar baz"]),
        ("foo bar;", ["foo bar"]),
        ("foo bar; ;", ["foo bar"]),
        ("foo bar; scoo bee; doo bee", ["foo bar", "scoo bee", "doo bee"]),
        ("foo   ;   bar;  ;", ["foo", "bar"]),
        ("foo 'bar;' scoo bee", ["foo 'bar;' scoo bee"]),
        (r"foo bar\; scoo bee", ["foo bar\\; scoo bee"]),
        (r"foo bar\\; scoo bee", ["foo bar\\\\; scoo bee"]),
        (r"foo bar\\\; scoo bee", ["foo bar\\\\\\; scoo bee"]),
    ),
)
def test_split_inline_commands(input, expected, repl: Riposte):
    assert repl._split_inline_commands(input) == expected


def test_split_inline_commands_unexpected_token(repl: Riposte):
    with pytest.raises(CommandError):
        repl._split_inline_commands("foo bar;;")


@mock.patch("builtins.input", return_value="foo bar")
def test_process(mocked_input, repl: Riposte, foo_command: Command):
    repl._process()
    foo_command._func.assert_called_once_with("bar")


@mock.patch("builtins.input", return_value="")
def test_process_no_input(mocked_input, repl: Riposte):
    repl._split_inline_commands = mock.MagicMock()
    repl._parse_line = mock.Mock()
    repl._get_command = mock.Mock()

    repl._process()

    repl._split_inline_commands.assert_not_called()
    repl._parse_line.assert_not_called()
    repl._get_command.assert_not_called()


@mock.patch("builtins.input", return_value="foo bar; scoo bee")
def test_process_multi_line(mocked_input, repl: Riposte):
    repl._get_command = mock.Mock()

    repl._process()

    assert repl._get_command.call_args_list == [
        mock.call("foo"),
        mock.call("scoo"),
    ]

    assert repl._get_command.return_value.execute.call_args_list == [
        mock.call("bar"),
        mock.call("bee"),
    ]


@mock.patch("builtins.print")
def test_banner(mocked_print, repl: Riposte):
    repl.banner = "foobar"
    repl.print_banner = True
    repl._process = mock.Mock(side_effect=StopIteration)
    repl.parse_cli_arguments = mock.Mock()

    repl.run()

    mocked_print.assert_called_once_with(repl.banner)


@mock.patch("builtins.print")
def test_banner_alternative_stream(mocked_print, repl: Riposte):
    repl.banner = "foobar"
    repl.print_banner = False
    repl._process = mock.Mock(side_effect=StopIteration)
    repl.parse_cli_arguments = mock.Mock()

    repl.run()

    mocked_print.assert_not_called()


def test_parse_cli_arguments_prompt(repl: Riposte):
    arguments = mock.Mock(c="", file="")
    repl.parser.parse_args = mock.Mock(return_value=arguments)

    repl.parse_cli_arguments()

    assert repl.input_stream.gi_code is input_streams.prompt_input.__code__


@mock.patch("riposte.riposte.input_streams")
def test_parse_cli_arguments_cli(mocked_input_streams, repl: Riposte):
    arguments = mock.Mock(c="foo bar", file="")
    repl.parser.parse_args = mock.Mock(return_value=arguments)

    repl.parse_cli_arguments()

    mocked_input_streams.cli_input.assert_called_once_with(arguments.c)
    assert repl.input_stream is mocked_input_streams.cli_input.return_value


@mock.patch("riposte.riposte.input_streams")
def test_parse_cli_arguments_file(mocked_input_streams, repl: Riposte):
    arguments = mock.Mock(c="", file="foo.txt")
    repl.parser.parse_args = mock.Mock(return_value=arguments)

    repl.parse_cli_arguments()

    mocked_input_streams.file_input.assert_called_once_with(
        Path(arguments.file)
    )
    assert repl.input_stream is mocked_input_streams.file_input.return_value
