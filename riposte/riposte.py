import argparse
import atexit
from pathlib import Path
import readline
import shlex
from typing import Callable, Dict, Iterable, List, Optional, Sequence

from . import input_streams
from .command import Command
from .exceptions import CommandError, RiposteException, StopRiposteException
from .printer.mixins import PrinterMixin
from .printer.thread import PrinterThread


def is_libedit():
    return "libedit" in readline.__doc__


class Riposte(PrinterMixin):
    def __init__(
        self,
        prompt: str = "riposte:~ $ ",
        banner: Optional[str] = None,
        history_file: Path = Path.home() / ".riposte",
        history_length: int = 100,
    ):
        self.banner = banner
        self.print_banner = True
        self.parser = None
        self.arguments = None
        self.input_stream = input_streams.prompt_input(lambda: self.prompt)

        self._prompt = prompt
        self._commands: Dict[str, Command] = {}

        self.setup_cli()

        self._printer_thread = PrinterThread()
        self._setup_history(history_file, history_length)
        self._setup_completer()

    @staticmethod
    def _setup_history(history_file: Path, history_length: int) -> None:
        if not history_file.exists():
            with open(history_file, "a+") as history:
                if is_libedit():
                    history.write("_HiStOrY_V2_\n\n")

        readline.read_history_file(str(history_file))
        readline.set_history_length(history_length)
        atexit.register(readline.write_history_file, str(history_file))

    def _setup_completer(self) -> None:
        readline.set_completer(self._complete)
        readline.set_completer_delims(" \t\n;")
        readline.parse_and_bind(
            "bind ^I rl_complete" if is_libedit() else "tab: complete"
        )

    def _complete(self, text: str, state: int) -> Optional[Sequence[str]]:
        """Return the next possible completion for `text`.

        If a command has not been entered, then complete against command list.
        Otherwise try to call specific command completer function to get list
        of completions.
        """
        if state == 0:
            original_line = readline.get_line_buffer()
            line = original_line.lstrip()
            stripped = len(original_line) - len(line)
            start_index = readline.get_begidx() - stripped
            end_index = readline.get_endidx() - stripped

            if start_index > 0 and line:
                cmd, *_ = self._parse_line(line)
                try:
                    complete_function = self._get_command(cmd).complete
                except CommandError:
                    return
            else:
                complete_function = self._raw_command_completer

            self.completion_matches = complete_function(
                text, line, start_index, end_index
            )

        try:
            return self.completion_matches[state]
        except IndexError:
            return

    def contextual_complete(self) -> List[str]:
        """Entry point for contextual tab completion.

        Entry point for contextual tab completion depending on `Riposte` app
        state. Overwrite this method to suggest suitable commands.
        """
        return list(self._commands.keys())

    def _raw_command_completer(
        self, text, line, start_index, end_index
    ) -> List[str]:
        """ Complete command w/o any argument """
        return [
            command
            for command in self.contextual_complete()
            if command.startswith(text)
        ]

    @staticmethod
    def _split_inline_commands(line: str) -> List[str]:
        """ Split multiple inline commands. """
        parsed = shlex.split(line, posix=False)

        commands = []
        command = []
        for element in parsed:
            if element[-2:] == "\\;":
                command.append(element)
            elif element[-2:] == ";;":
                raise CommandError("unexpected token: ;;")
            elif element[-1] == ";" and element[:-1] != "":
                command.append(element[:-1])
                commands.append(command)
                command = []
            elif element[-1] == ";" and element[:-1] == "":
                commands.append(command)
                command = []
            else:
                command.append(element)

        if command:
            commands.append(command)

        return [" ".join(command) for command in commands if command]

    @staticmethod
    def _parse_line(line: str) -> List[str]:
        """ Split input line into command's name and its arguments. """
        try:
            return shlex.split(line)
        except ValueError as err:
            raise RiposteException(err)

    def _get_command(self, command_name: str) -> Command:
        """ Resolve command name into registered `Command` object. """
        try:
            return self._commands[command_name]
        except KeyError:
            raise CommandError(f"Unknown command: {command_name}")

    def setup_cli(self):
        """Initialize CLI

        Overwrite this method in case of adding custom arguments.
        """
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("file", nargs="?", default=None)
        self.parser.add_argument(
            "-c",
            metavar="commands",
            help="commands passed in as string, delimited with semicolon",
        )

    def parse_cli_arguments(self) -> None:
        """Parse passed CLI arguments

        Overwrite this method in order to parse custom CLI arguments.
        """
        self.arguments = self.parser.parse_args()
        if self.arguments.c:
            self.print_banner = False
            self.input_stream = input_streams.cli_input(self.arguments.c)
        elif self.arguments.file:
            self.print_banner = False
            self.input_stream = input_streams.file_input(
                Path(self.arguments.file)
            )

    @property
    def prompt(self):
        """Entrypoint for customizing prompt

        Please overwrite this method to provide contextual prompt depending on
        different state of `Riposte` app.
        """
        return self._prompt

    def command(
        self,
        name: str,
        description: str = "",
        guides: Dict[str, Iterable[Callable]] = None,
    ) -> Callable:
        """ Decorator for bounding command with handling function. """

        def wrapper(func: Callable):
            if name not in self._commands:
                self._commands[name] = Command(name, func, description, guides)
            else:
                raise RiposteException(f"'{name}' command already exists.")
            return func

        return wrapper

    def complete(self, command: str) -> Callable:
        """ Decorator for bounding complete function with `Command`. """

        def wrapper(func: Callable):
            cmd = self._get_command(command)
            cmd.attach_completer(func)
            return func

        return wrapper

    def _process(self) -> None:
        """Process input provided by the input stream.

        Get provided input, parse it, pick appropriate handling
        function and execute it.
        """
        user_input = next(self.input_stream)()
        if not user_input:
            return

        for line in self._split_inline_commands(user_input):
            command_name, *args = self._parse_line(line)
            self._get_command(command_name).execute(*args)

    def run(self) -> None:
        self._printer_thread.start()

        self.parse_cli_arguments()

        if self.banner and self.print_banner:
            # builtin print() to avoid race condition with input()
            print(self.banner)

        while True:
            try:
                self._process()
            except RiposteException as err:
                self.error(err)
            except StopRiposteException as err:
                self.error(err)
                break
            except EOFError:
                self.print()
                break
            except StopIteration:
                break
            except KeyboardInterrupt:
                self.print()
            finally:
                self._printer_thread.wait()
