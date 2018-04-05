import pytest

from riposte import Riposte
from riposte.exceptions import RiposteException


def test_command(repl: Riposte):
    @repl.command(name="foo")
    def foo():
        pass
    assert len(repl.commands) == 1
    assert repl.commands["foo"] is foo

    @repl.command(name="bar")
    def bar():
        pass
    assert len(repl.commands) == 2
    assert repl.commands["bar"] is bar


def test_command_duplicated_command(repl: Riposte):
    with pytest.raises(RiposteException):
        @repl.command(name="foo")
        def foo():
            pass

        @repl.command(name="foo")
        def bar():
            pass


@pytest.mark.parametrize(["raw_line", "parsed_line"], [
    ("scoo bee doo", ["scoo", "bee", "doo"]),
    ("  scoo  bee  doo  ", ["scoo", "bee", "doo"]),
    ("\tscoo\tbee\tdoo\n", ["scoo", "bee", "doo"]),
])
def test_parse_line(raw_line, parsed_line, repl: Riposte):
    assert repl.parse_line(raw_line) == parsed_line


def test_get_command_handler(repl: Riposte):
    @repl.command(name="foo")
    def foo():
        pass
    assert repl.get_command_handler("foo") is foo


def test_get_command_handler_no_handling_function(repl: Riposte):
    @repl.command(name="foo")
    def foo():
        pass
    with pytest.raises(RiposteException):
        repl.get_command_handler("bar")
