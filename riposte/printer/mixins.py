import sys
import typing

from riposte.printer.thread import PrintResource


class PrinterBaseMixin:
    def _print(
        self,
        *args,
        sep: typing.Optional[str] = " ",
        end: typing.Optional[str] = "\n",
        file: typing.Optional[typing.IO] = sys.stdout,
    ):
        self._printer_thread.put(
            PrintResource(content=args, sep=sep, end=end, file=file)
        )


class PrinterMixin(PrinterBaseMixin):
    def print(self, *args, **kwargs):
        self._print(*args, **kwargs)

    def info(self, *args, **kwargs):
        self.print(*args, **kwargs)

    def error(self, *args, **kwargs):
        self._print("\033[91m[-]\033[0m", *args, **kwargs)

    def status(self, *args, **kwargs):
        self._print("\033[94m[*]\033[0m", *args, **kwargs)

    def success(self, *args, **kwargs):
        self._print("\033[92m[+]\033[0m", *args, **kwargs)
