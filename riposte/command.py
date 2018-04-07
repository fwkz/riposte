import typing


class Command:
    def __init__(self, name: str, func: typing.Callable):
        self.name = name

        self._func = func
        self._completer_function = None

    def execute(self, *args, **kwargs):
        return self._func(*args, **kwargs)

    def complete(self, *args, **kwargs) -> typing.Sequence:
        if not self._completer_function:
            return ()

        return self._completer_function(*args, **kwargs)

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return all((
            self.name == other.name,
            self._func is other._func,
        ))
