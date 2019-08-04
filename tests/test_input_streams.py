import io
from unittest import mock

import pytest

from riposte import input_streams
from riposte.exceptions import StopRiposteException


@mock.patch("builtins.input")
def test_prompt_input(mocked_input):
    mocked_prompt = mock.Mock()

    input_stream = input_streams.prompt_input(mocked_prompt)

    for idx in range(1, 100):
        assert next(input_stream)() == mocked_input.return_value
        assert mocked_prompt.call_count == idx
        assert mocked_input.call_count == idx
        assert mocked_input.call_args == mock.call(mocked_prompt.return_value)


def test_cli_input():
    inline_commands = "foo bar; scoo bee;"

    input_stream = input_streams.cli_input(inline_commands)

    assert next(input_stream)() == inline_commands
    with pytest.raises(StopIteration):
        next(input_stream)()


@mock.patch(
    "builtins.open", return_value=io.StringIO("foo bar\nscoo bee; doo\nbee")
)
def test_file_input(mock_open):
    path = "foobar.txt"

    input_stream = input_streams.file_input(path)

    assert next(input_stream)() == "foo bar\n"
    assert next(input_stream)() == "scoo bee; doo\n"
    assert next(input_stream)() == "bee"
    mock_open.assert_called_once_with(path, "r")


@mock.patch("builtins.open", side_effect=IOError)
def test_file_input_error(mock_open):
    path = "foobar.txt"

    with pytest.raises(StopRiposteException):
        input_stream = input_streams.file_input(path)
        next(input_stream)()
        mock_open.assert_called_once_with(path, "r")
