from unittest import mock

import pytest

from riposte import Riposte
from riposte.command import Command
from riposte.exceptions import RiposteException


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
