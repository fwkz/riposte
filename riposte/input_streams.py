import itertools
from pathlib import Path
from typing import Callable, Generator

from riposte.exceptions import StopRiposteException


def prompt_input(prompt: Callable) -> Generator[Callable, None, None]:
    """ Unexhaustible generator yielding `input` function forever. """
    yield from itertools.repeat(lambda: input(prompt()))


def cli_input(inline_commands: str) -> Generator[Callable, None, None]:
    """ Translate inline command provided via '-c' into input stream. """
    yield lambda: inline_commands


def file_input(path: Path) -> Generator[Callable, None, None]:
    """ Read file and translate it into input stream """
    try:
        with open(path, "r") as file_handler:
            for line in file_handler:
                yield lambda: line
    except Exception:
        raise StopRiposteException(f"Problem with reading the file: {path}")
