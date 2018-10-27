from unittest.mock import Mock

import pytest

from riposte import Riposte
from riposte.command import Command


@pytest.fixture
def repl(history_file):
    return Riposte(history_file=history_file)


@pytest.fixture
def foo_command(repl: Riposte):
    repl.command(name="foo")(
        Mock(name="function_handling_foo", __annotations__={})
    )
    return repl._commands["foo"]


@pytest.fixture
def history_file(tmpdir):
    return tmpdir / ".riposte"


@pytest.fixture
def command():
    return Command(
        name="foo",
        func=Mock(name="mocked_handling_function", __annotations__={}),
        description="foo description",
    )
