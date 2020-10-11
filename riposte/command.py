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
        """Validate guides setup.

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

    def _process_arguments(self, name: str, *args) -> List:
        """Process each argument according to selected chain of guides

        Process each argument according to selected chain of guides. Each
        guide from the collection is applied to the every argument.
        Guide as input uses output from previous guide e.g.

            guide_3(guide_2(guide_1("scoo")))

        """
        processed = []
        for arg in args:
            for guide in self._guides.get(name, []):
                arg = guide(arg)
            processed.append(arg)

        return processed

    def _apply_guides(self, bound_arguments: inspect.BoundArguments) -> List:
        """Apply guide functions.

        Apply guide functions to values of type `str` delivered by user
        using `input()`.

        Assumes that `args` have been already validated `_bind_arguments`,
        hence `args` is matching `_func` signature, (`args <= parameters`)

        """
        processed = []
        for name, value in bound_arguments.arguments.items():
            if (
                bound_arguments.signature.parameters[name].kind
                is inspect.Parameter.VAR_POSITIONAL
            ):
                arguments = self._process_arguments(name, *value)
            else:
                arguments = self._process_arguments(name, value)

            processed.extend(arguments)

        return processed

    def _bind_arguments(self, *args) -> inspect.BoundArguments:
        """ Check whether given `args` match `_func` signature. """
        try:
            return inspect.signature(self._func).bind(*args)
        except TypeError as e:
            raise CommandError(e)

    def execute(self, *args: str) -> None:
        """Execute handling function (`self._func`) bound to command.

        In case of argument mismatch during function call we want to give
        user informative feedback that's why we are wrapping
        `TypeError` with `CommandError`.

        """
        return self._func(*self._apply_guides(self._bind_arguments(*args)))

    def complete(self, *args, **kwargs) -> Sequence:
        """ Execute completer function bound to this command. """

        if not self._completer_function:
            return ()

        return self._completer_function(*args, **kwargs)

    def attach_completer(self, completer_function: Callable) -> None:
        """Attach complater function.

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
