from typing import Callable

from .printer import Palette


class RiposteException(Exception):
    pass


class CommandError(RiposteException):
    pass


class ValidationError(RiposteException):
    def __init__(self, value: str, validator: Callable):
        self.value = value
        self.validator = validator

    def __str__(self):
        return (
            f"ValidationError: Can't validate "
            f"{Palette.BOLD.format(self.value)} using "
            f"{Palette.BOLD.format(self.validator.__name__)} validator"
        )
