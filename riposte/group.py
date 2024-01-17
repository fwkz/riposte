from typing import Callable, Dict, Iterable

from .command import Command
from .exceptions import CommandError, RiposteException


class Group:
    def __init__(self):
        self._commands: Dict[str, Command] = {}

    def _get_command(self, command_name: str) -> Command:
        """Resolve command name into registered `Command` object."""
        try:
            return self._commands[command_name]
        except KeyError:
            raise CommandError(f"Unknown command: {command_name}")

    def command(
        self,
        name: str,
        description: str = "",
        guides: Dict[str, Iterable[Callable]] = None,
    ) -> Callable:
        """Decorator for bounding command with handling function."""

        def wrapper(func: Callable):
            if name not in self._commands:
                self._commands[name] = Command(name, func, description, guides)
            else:
                raise RiposteException(f"'{name}' command already exists.")
            return func

        return wrapper

    def complete(self, command: str) -> Callable:
        """Decorator for bounding complete function with `Command`."""

        def wrapper(func: Callable):
            cmd = self._get_command(command)
            cmd.attach_completer(func)
            return func

        return wrapper
