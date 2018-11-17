import inspect
from unittest import mock

import pytest

from riposte.command import Command
from riposte.exceptions import CommandError


def test_execute(command):
    args = (1, 2, 3)
    mocked_bind_arguments = command._bind_arguments = mock.Mock()
    mocked_apply_guides = command._apply_guides = mock.MagicMock()

    command.execute(*args)

    mocked_bind_arguments.assert_called_once_with(*args)
    mocked_apply_guides.assert_called_once_with(
        mocked_bind_arguments.return_value
    )
    command._func.assert_called_once_with(*mocked_apply_guides.return_value)


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
    def foo(x: int, *args: int):
        pass

    command._func = foo
    args = ("1", "2", "3")
    command._process_arguments = mock.Mock(side_effect=([1], [2, 3]))
    bound_arguments = inspect.signature(foo).bind(*args)

    assert command._apply_guides(bound_arguments) == [1, 2, 3]
    assert command._process_arguments.call_args_list == [
        mock.call("x", "1"),
        mock.call("args", "2", "3"),
    ]


@pytest.mark.parametrize("guides", (1, "str", (int), [2.0]))
def test_validate_guides(command, guides):
    command._guides = {"foo": guides}
    with pytest.raises(CommandError):
        command._validate_guides()


@mock.patch("riposte.command.inspect")
def test_bind_arguments(inspect_mock, command):
    args = (1, 2)
    command._bind_arguments(*args)

    inspect_mock.signature.assert_called_once_with(command._func)
    inspect_mock.signature.return_value.bind.assert_called_once_with(*args)


@mock.patch("riposte.command.inspect")
def test_bind_arguments_exception(inspect_mock, command):
    args = (1, 2)
    inspect_mock.signature.return_value.bind.side_effect = TypeError

    with pytest.raises(CommandError):
        command._bind_arguments(*args)

    inspect_mock.signature.assert_called_once_with(command._func)
    inspect_mock.signature.return_value.bind.assert_called_once_with(*args)


@pytest.mark.parametrize(
    "args, guides, expected_value",
    (
        (("1",), {}, ["1"]),
        (("1",), {"foo": (lambda x: x + "_",)}, ["1_"]),
        (("1", "2"), {"foo": (lambda x: x + "_",)}, ["1_", "2_"]),
        (
            ("1", "2"),
            {"foo": (lambda x: x + "_", lambda x: x + "@")},
            ["1_@", "2_@"],
        ),
    ),
)
def test_process_arguments(args, guides, expected_value, command):
    command._guides = guides
    assert command._process_arguments("foo", *args) == expected_value
