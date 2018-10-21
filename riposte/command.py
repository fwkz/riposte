import inspect
from typing import Callable, Dict, Iterable, List, Sequence

from .exceptions import CommandError


class Command:
    def __init__(
        self,
        name: str,
        func: Callable,
        description: str,
        validators: Dict[str, Iterable[Callable]] = None,
    ):
        self.name = name
        self.description = description

        self._func = func
        self._completer_function = None

        self._validators = {} if not validators else validators
        self._validate_validators()

    def _validate_validators(self) -> None:
        for parameter, command_validators in self._validators.items():
            if not isinstance(command_validators, Iterable):
                raise CommandError(
                    f"Command '{self.name}': validators for parameter "
                    f"'{parameter}' have to be iterable "
                    f"not '{type(command_validators)}'"
                )

            for validator in command_validators:
                if not isinstance(validator, Callable):
                    raise CommandError(
                        f"Command '{self.name}': validator for "
                        f"parameter '{parameter}' have to be "
                        f"callable not {type(validator)}"
                    )

    def _apply_validators(self, *args) -> List:
        names = inspect.getfullargspec(self._func).args
        validated = []
        for arg, name in zip(args, names):
            validators = self._validators.get(name, [])
            for validator in validators:
                arg = validator(arg)
            validated.append(arg)

        return validated

    def execute(self, *args) -> None:
        args = self._apply_validators(*args)
        try:
            return self._func(*args)
        except TypeError as err:
            raise CommandError(err)

    def complete(self, *args, **kwargs) -> Sequence:
        if not self._completer_function:
            return ()

        return self._completer_function(*args, **kwargs)

    def attach_completer(self, completer_function: Callable) -> None:
        if self._completer_function:
            raise CommandError(
                f"Command '{self.name}' already has completer function."
            )
        self._completer_function = completer_function

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return all((self.name == other.name, self._func is other._func))
