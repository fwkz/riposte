from unittest.mock import Mock

import pexpect
import pytest

from riposte import Riposte
from riposte.command import Command


@pytest.fixture
def repl(history_file):
    return Riposte(history_file=history_file)


@pytest.fixture
def sut():
    software_under_test = pexpect.spawn(
        "python tests/functional/sut.py",
        timeout=2,
    )

    software_under_test.expect("sut > ")
    yield software_under_test
    software_under_test.close()


@pytest.fixture
def foo_command(repl: Riposte):
    repl.command(name="foo")(Mock(name="function_handling_foo"))
    return repl._commands["foo"]


@pytest.fixture
def history_file(tmpdir):
    return tmpdir / ".riposte"


@pytest.fixture
def command():
    cmd = Command(
        name="foo",
        func=Mock(name="mocked_handling_function"),
        description="foo description",
    )
    cmd.attach_completer(Mock(name="mocked_completer_function"))
    return cmd
