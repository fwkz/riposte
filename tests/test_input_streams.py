from unittest import mock

import pytest

from riposte.input_streams import cli_input, prompt_input


@mock.patch("builtins.input")
def test_prompt_input(mocked_input):
    mocked_prompt = mock.Mock()

    input_stream = prompt_input(mocked_prompt)

    for idx in range(1, 100):
        assert next(input_stream)() == mocked_input.return_value
        assert mocked_prompt.call_count == idx
        assert mocked_input.call_count == idx
        assert mocked_input.call_args == mock.call(mocked_prompt.return_value)


def test_cli_input():
    inline_commands = "foo bar; scoo bee;"

    input_stream = cli_input(inline_commands)

    assert next(input_stream)() == inline_commands
    with pytest.raises(StopIteration):
        next(input_stream)()
