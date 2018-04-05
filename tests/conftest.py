import pytest

from riposte import Riposte


@pytest.fixture
def repl():
    return Riposte()
