from enum import Enum


class Palette(Enum):
    GREY = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37

    BOLD = 1

    def format(self, obj: str):
        return f"\033[{self.value}m{obj}\033[0m"
