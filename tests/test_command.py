def test_execute(command):
    args = (1, 2, 3)
    kwargs = {"scoo": "bee", "doo": "bee"}
    command.execute(*args, **kwargs)
    command._func.assert_called_once_with(*args, **kwargs)


def test_complete(command):
    args = (1, 2, 3)
    kwargs = {"scoo": "bee", "doo": "bee"}
    command.complete(*args, **kwargs)
    command._completer_function.assert_called_once_with(*args, **kwargs)
