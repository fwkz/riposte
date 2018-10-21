from unittest.mock import Mock

import pytest

from riposte.exceptions import CommandError


def test_execute(command):
    args = (1, 2, 3)
    mocked_apply_validators = command._apply_validators = Mock(
        return_value=args
    )

    command.execute(*args)

    mocked_apply_validators.assert_called_once_with(*args)
    command._func.assert_called_once_with(*args)


def test_complete(command):
    args = (1, 2, 3)
    kwargs = {"scoo": "bee", "doo": "bee"}
    command._completer_function = Mock()

    command.complete(*args, **kwargs)

    command._completer_function.assert_called_once_with(*args, **kwargs)


def test_attach_completer(command):
    completer_function = Mock()

    command.attach_completer(completer_function)

    assert command._completer_function is completer_function


def test_attach_completer_already_attached(command):
    command._completer_function = Mock()

    with pytest.raises(CommandError):
        command.attach_completer(Mock())


def test_apply_validators(command):
    validator_alpha = Mock(name="alpha")
    validator_bravo = Mock(name="bravo")

    command._func = lambda x: None
    command._validators = {"x": [validator_alpha, validator_bravo]}

    assert command._apply_validators(1) == [validator_bravo.return_value]

    validator_alpha.assert_called_once_with(1)
    validator_bravo.assert_called_once_with(validator_alpha.return_value)


def test_apply_validators_no_validators(command):
    command._func = lambda x, y: None
    assert command._apply_validators(1, 2) == [1, 2]


@pytest.mark.parametrize("validators", (1, "str", (int), [2.0]))
def test_validate_validators(command, validators):
    command._validators = {"foo": validators}
    with pytest.raises(CommandError):
        command._validate_validators()
