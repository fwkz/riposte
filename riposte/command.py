import inspect
from typing import Callable, Dict, Iterable, List, Sequence

from .exceptions import CommandError
from .guides import extract_guides


class Command:
    def __init__(
        self,
        name: str,
        func: Callable,
        description: str,
        guides: Dict[str, Iterable[Callable]] = None,
    ):
        self.name = name
        self.description = description

        self._func = func
        self._completer_function = None

        self._guides = extract_guides(self._func)
        self._guides.update(guides if guides else {})
        self._validate_guides()

    def _validate_guides(self) -> None:
        """ Validate guides setup.

        Check if guides setup is valid and raise exception with
        informative message what is wrong.

        """
        for parameter, command_guides in self._guides.items():
            if not isinstance(command_guides, Iterable):
                raise CommandError(
                    f"Command '{self.name}': guides for parameter "
                    f"'{parameter}' have to be iterable "
                    f"not '{type(command_guides)}'"
                )

            for guide in command_guides:
                if not isinstance(guide, Callable):
                    raise CommandError(
                        f"Command '{self.name}': guide for "
                        f"parameter '{parameter}' have to be "
                        f"callable not {type(guide)}"
                    )

    def _apply_guides(self, *args: str) -> List:
        """ Apply guide functions.

        Apply guide functions to values of type `str` delivered by user
        using `input()`.

        """
        names = inspect.getfullargspec(self._func).args
        processed = []
        for arg, name in zip(args, names):
            guides = self._guides.get(name, [])
            for guide in guides:
                arg = guide(arg)
            processed.append(arg)

        return processed

    def execute(self, *args: str) -> None:
        """ Execute handling function (`self._func`) bound to command.

        In case of argument mismatch during function call we want to give
        user informative feedback that's why we are wrapping
        `TypeError` with `CommandError`.

        """

        args = self._apply_guides(*args)
        try:
            return self._func(*args)
        except TypeError as err:
            raise CommandError(err)

    def complete(self, *args, **kwargs) -> Sequence:
        """ Execute completer function bound to this command. """

        if not self._completer_function:
            return ()

        return self._completer_function(*args, **kwargs)

    def attach_completer(self, completer_function: Callable) -> None:
        """ Attach complater function.

        # TODO: Maybe we should make it @property?
        """
        if self._completer_function:
            raise CommandError(
                f"Command '{self.name}' already has completer function."
            )
        self._completer_function = completer_function

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return all((self.name == other.name, self._func is other._func))
