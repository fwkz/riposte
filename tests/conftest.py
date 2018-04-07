from unittest.mock import Mock

import pytest

from riposte import Riposte
from riposte.command import Command


@pytest.fixture
def repl(history_file):
    return Riposte(history_file=history_file)


@pytest.fixture
def foo_command(repl):
    repl.command(name="foo")(Mock(name="function_handling_foo"))
    return repl.commands["foo"]


@pytest.fixture
def history_file(tmpdir):
    return tmpdir / ".riposte"


@pytest.fixture
def command():
    cmd = Command(name="foo", func=Mock(name="mocked_handling_function"))
    cmd._completer_function = Mock(name="mocked_completer_function")
    return cmd
