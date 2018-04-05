import typing

from .exceptions import RiposteException


class Riposte:
    def __init__(self, prompt: str = "riposte:~ $ "):
        self.prompt = prompt

        self.commands: typing.Dict[str, typing.Callable] = {}

    def run(self):
        while True:
            try:
                command, *args = self.parse_line(input(self.prompt))
                self.get_command_handler(command)(*args)
            except RiposteException as err:
                print(err)
            except EOFError:
                print()
                break
            except KeyboardInterrupt:
                print()

    @staticmethod
    def parse_line(line: str) -> typing.List[str]:
        """ Split input line into command and arguments. """
        return line.strip().split()

    def get_command_handler(self, command: str) -> typing.Callable:
        """ Resolve command into handling function. """
        try:
            return self.commands[command]
        except KeyError:
            raise RiposteException(f"Unknown command: '{command}'")

    def command(self, name: str) -> typing.Callable:
        """ Decorator for bounding commands into handling functions. """

        def wrapper(func: typing.Callable):
            if name not in self.commands:
                self.commands[name] = func
            else:
                raise RiposteException(f"'{name}' command already exists.")
            return func

        return wrapper
