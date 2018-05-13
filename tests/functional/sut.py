from pathlib import Path
from tempfile import TemporaryDirectory

from riposte import Riposte

with TemporaryDirectory() as tempdir:
    repl = Riposte(
        prompt="sut > ",
        history_file=Path(tempdir) / Path(".sut_history"),
    )

    @repl.command("foo")
    def foo(x, y):
        repl.info("foo executed with", x, y)

    @repl.complete("foo")
    def complete_foo(text, *args, **kwargs):
        elements = ["ddd", "bbb", "aaa", "abba"]
        return [element for element in elements if element.startswith(text)]

    @repl.command("bar")
    def bar():
        repl.info("bar executed")


if __name__ == "__main__":
    repl.run()
