from unittest import mock

import pytest

from riposte.command import Command
from riposte.exceptions import CommandError


def test_execute(command):
    args = (1, 2, 3)
    mocked_apply_guides = command._apply_guides = mock.Mock(return_value=args)

    command.execute(*args)

    mocked_apply_guides.assert_called_once_with(*args)
    command._func.assert_called_once_with(*args)


def test_complete(command):
    args = (1, 2, 3)
    kwargs = {"scoo": "bee", "doo": "bee"}
    command._completer_function = mock.Mock()

    command.complete(*args, **kwargs)

    command._completer_function.assert_called_once_with(*args, **kwargs)


def test_attach_completer(command):
    completer_function = mock.Mock()

    command.attach_completer(completer_function)

    assert command._completer_function is completer_function


def test_attach_completer_already_attached(command):
    command._completer_function = mock.Mock()

    with pytest.raises(CommandError):
        command.attach_completer(mock.Mock())


@mock.patch("riposte.command.extract_guides")
def test_command_setup_guides_validate(mocked_extract_guides):

    with mock.patch.object(
        Command, "_validate_guides"
    ) as mocked_validate_guides:

        Command("foo", mock.Mock(), "description")

        mocked_validate_guides.assert_called_once_with()


@mock.patch(
    "riposte.command.extract_guides", return_value={"foo": (mock.Mock(),)}
)
def test_command_setup_guides_extract(mocked_extract_guides):
    func = mock.Mock()

    command = Command("foo", func, "description")

    mocked_extract_guides.assert_called_once_with(func)
    assert command._guides == mocked_extract_guides.return_value


@mock.patch(
    "riposte.command.extract_guides", return_value={"foo": (mock.Mock(),)}
)
def test_command_setup_guides_update(mocked_extract_guides):
    func = mock.Mock()
    guides = {"foo": [str], "bar": [str]}

    command = Command("foo", func, "description", guides=guides)

    mocked_extract_guides.assert_called_once_with(func)
    assert command._guides == guides


def test_apply_guides(command):
    validator_alpha = mock.Mock(name="alpha")
    validator_bravo = mock.Mock(name="bravo")

    command._func = lambda x: None
    command._guides = {"x": [validator_alpha, validator_bravo]}

    assert command._apply_guides(1) == [validator_bravo.return_value]

    validator_alpha.assert_called_once_with(1)
    validator_bravo.assert_called_once_with(validator_alpha.return_value)


def test_apply_guides_no_guides(command):
    command._func = lambda x, y: None
    assert command._apply_guides(1, 2) == [1, 2]


@pytest.mark.parametrize("guides", (1, "str", (int), [2.0]))
def test_validate_guides(command, guides):
    command._guides = {"foo": guides}
    with pytest.raises(CommandError):
        command._validate_guides()
