import itertools
from typing import Callable, Generator


def prompt_input(prompt: Callable) -> Generator[Callable, None, None]:
    """ Unexhaustible generator yielding `input` function forever. """
    yield from itertools.repeat(lambda: input(prompt()))


def cli_input(inline_commands: str) -> Generator[Callable, None, None]:
    """ Translate inline command provided via '-c' into input stream. """
    yield lambda: inline_commands
