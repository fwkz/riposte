# riposte
[![Build Status](https://travis-ci.org/fwkz/riposte.svg?branch=master)](https://travis-ci.org/fwkz/riposte)
[![License](https://img.shields.io/pypi/l/riposte.svg)](https://github.com/fwkz/riposte/blob/master/LICENSE)
[![Version](https://img.shields.io/pypi/v/riposte.svg)](https://pypi.org/project/riposte/)
[![Python](https://img.shields.io/pypi/pyversions/riposte.svg)](https://pypi.org/project/riposte/)
[![Code Style](https://img.shields.io/badge/codestyle-black-black.svg)](https://github.com/ambv/black)

_Riposte_ allows you to easily wrap your application inside a tailored 
interactive shell. Common chores regarding building REPLs was factored out and 
being taken care of so you can really focus on specific domain logic of your 
application.

The motivation for building _Riposte_ coming from many sleepless nights of 
handling numerous tricky cases regarding REPLs during 
[routersploit](https://github.com/threat9/routersploit) development. Like 
every other project it began very innocently but after a while, when the project 
got some real traction and code base was rapidly growing, shell logic started 
to intertwine with domain logic making things less and less readable and 
contributor friendly.

Moreover, to our surprise, people started to fork 
[routersploit](https://github.com/threat9/routersploit) not because they were 
interested in the security of embedded devices but simply because they want to 
leverage our interactive shell logic and build their own tools using similar 
concept. All these years they must have said: _"There must be a better way!"_ 
and they were completely right, the better way is called _Riposte_.

## Table of contents
* [Getting started](#getting-started)
    * [Installing](#installing)
    * [Example usage](#example-usage)
* [Manual](#manual)
    * [Command](#command)
    * [Completer](#completer)
    * [Guides](#guides)
    * [Printing](#printing)
    * [History](#history)
    * [Prompt](#Prompt)
    * [Banner](#Banner)
    * [Inline command execution](#Inline-command-execution)
    * [CLI](#CLI)
    * [Input streams](#input-streams)
* [Project status](#project-status)
* [Contributing](#contributing)
* [Versioning](#versioning)
* [License](#license)
* [Acknowledgments](#acknowledgments)

## Getting Started
### Installing
The package is available on PyPI so please use 
[pip](https://pip.pypa.io/en/stable/quickstart/) to install it: 
```bash
pip install riposte
```
Riposte supports Python 3.6 and newer.

### Example usage
```python
from riposte import Riposte

calculator = Riposte(prompt="calc:~$ ")

MEMORY = []


@calculator.command("add")
def add(x: int, y: int):
    result = f"{x} + {y} = {x + y}"
    MEMORY.append(result)
    calculator.success(result)


@calculator.command("multiply")
def multiply(x: int, y: int):
    result = f"{x} * {y} = {x * y}"
    MEMORY.append(result)
    calculator.success(result)


@calculator.command("memory")
def memory():
    for entry in MEMORY:
        calculator.print(entry)


calculator.run()

```

```bash
calc:~$ add 2 2
[+] 2 + 2 = 4
calc:~$ multiply 3 3
[+] 3 * 3 = 9
calc:~$ memory
2 + 2 = 4
3 * 3 = 9
calc:~$ 
```

## Manual
### Command
First and foremost you want to register some commands to make your REPL 
actionable. Adding command and bounding it with handling function is possible 
through `Riposte.command` decorator.

```python
from riposte import Riposte

repl = Riposte()

@repl.command("hello")
def hello():
    repl.success("Is it me you looking for?")

repl.run()
```
```bash
riposte:~ $ hello
[+] Is it me you looking for?
```
Additionally `Riposte.command` accepts few optional parameters:
* `description` few words describing command which you can later use to build 
meaningful help 
* [`guides`](#guides) definition of how to interpret passed arguments

### Completer
`Riposte` comes with support for tab-completion for commands. You can register 
completer function in a similar way you registering commands, just use `Riposte.complete` 
decorator and point it to a specific command.

```python
from riposte import Riposte

repl = Riposte()

START_SUBCOMMANDS = ["foo", "bar"]


@repl.command("start")
def start(subcommand: str):
    if subcommand in START_SUBCOMMANDS:
        repl.status(f"{subcommand} started")
    else:
        repl.error("Unknown subcommand.")


@repl.complete("start")
def start_completer(text, line, start_index, end_index):
    
    return [
        subcommand
        for subcommand in START_SUBCOMMANDS
        if subcommand.startswith(text)
    ]


repl.run()

```
Completer function is triggered by the TAB key. Every completer function should 
return list of valid options and should accept the following parameters:
* `text` last word in the line
* `line` content of the whole line
* `start_index` starting index of the last word in the line
* `end_index` ending index of the last word in the line

So in the case of our example:

`riposte:~ $ start ba<TAB>`

```
text -> "ba"
line -> "start ba"
start_index -> 6
end_index -> 8
```
Equipped with this information you can build your custom completer functions for 
every command.

### Guides
Guides is a way of saying how [command](#command) should interpret arguments 
passed by the user via prompt. `Riposte` rely on 
[type-hints](https://docs.python.org/3/library/typing.html) in order to do that.
```python
from riposte import Riposte

repl = Riposte()

@repl.command("guideme")
def guideme(x: int, y: str):
    repl.print("x:", x, type(x))
    repl.print("y:", y, type(y))

repl.run()
```
```bash
riposte:~ $ guideme 1 1
x: 1 <class 'int'>
y: 1 <class 'str'>
```
In both cases we've passed value _1_ as `x` and `y`. Based on 
parameter's type-hint passed arguments was interpreted as `int` in case of `x` 
and as `str` in case of `y`. You can also use this technique for different types.

```python
from riposte import Riposte

repl = Riposte()

@repl.command("guideme")
def guideme(x: dict, y: list):
    x["foo"] = "bar"
    repl.print("x:", x, type(x))
    
    y.append("foobar")
    repl.print("y:", y, type(y))

repl.run()
```
```bash
riposte:~ $ guideme "{'bar': 'baz'}" "['barbaz']"
x: {'bar': 'baz', 'foo': 'bar'} <class 'dict'>
y: ['barbaz', 'foobar'] <class 'list'>
```
Another more powerful way of defining guides for handling function parameters 
is defining it straight from`Riposte.command` decorator. In this case guide
defined this way take precedence over the type hints.
```python
from riposte import Riposte

repl = Riposte()

@repl.command("guideme", guides={"x": [int]})
def guideme(x):
    repl.print("x:", x, type(x))

repl.run()
```
```bash
riposte:~ $ guideme 1
x: 1 <class 'int'>
```
Why it is more powerful? Because this way you can chain different guides, 
where output of one guide is input for another, creating validation or cast 
input into more complex types.
```python
from collections import namedtuple

from riposte import Riposte
from riposte.exceptions import RiposteException
from riposte.guides import literal

repl = Riposte()


def non_negative(value: int):
    if value < 0:
        raise RiposteException("Value can't be negative")
    
    return value


Point = namedtuple("Point", ("x", "y"))


def get_point(value: dict):
    return Point(**value)


@repl.command("guideme",
              guides={"x": [int, non_negative], "y": [literal, get_point]})
def guideme(x, y):
    repl.print("x:", x, type(x))
    repl.print("y:", y, type(y))


repl.run()

```
```bash
riposte:~ $ guideme -1 '{"x": 1, "y": 2}'
[-] Value can't be negative
riposte:~ $ guideme 1 '{"x": 1, "y": 2}'
x: 1 <class 'int'>
y: Point(x=1, y=2) <class '__main__.Point'>
riposte:~ $ 
```
Under the hood, it is a simple function call where the input string is passed 
to first guide function in the chain. In this case, the call looks like this:
```python
non_negative(int("-1"))  # guide chain for parameter `x`
get_point(literal('{"x": 1, "y": 2}'))  # guide chain for parameter `y`
```

### Printing
_Riposte_ comes with built-in thread safe printing methods:

* `print`
* `info`
* `error`
* `status`
* `success`

Every method follows the signature of Python's built-in 
[`print()`](https://docs.python.org/3/library/functions.html#print) function. 
Besides `print` all of them provide informative coloring corresponding to its name.

We strongly encourage to stick to our thread safe printing API but if you are 
feeling frisky, know what you are doing and you are 100% sure, that threaded 
execution is something that will never come up at some point in the lifecycle of 
you application feel free to use Python's built-in 
[`print()`](https://docs.python.org/3/library/functions.html#print) function. 

#### Extending `PrinterMixin`
If you want to change the styling of existing methods or add custom one, please 
extend `PrinterMixin` class.

```python
from riposte import Riposte
from riposte.printer.mixins import PrinterMixin


class ExtendedPrinterMixin(PrinterMixin):
    def success(self, *args, **kwargs):  # overwriting existing method
        self.print(*args, **kwargs)
    
    def shout(self, *args, **kwargs):  # adding new one
        self.print((*args, "!!!"), **kwargs)

class CustomRiposte(Riposte, ExtendedPrinterMixin):
    pass
 
repl = CustomRiposte()

@repl.command("foobar")
def foobar(message: str):
    repl.shout(message)

```

#### Customizing `PrinterMixin`
Not happy about existing printing API? No problem, you can also build your own 
from scratch using `PrinterBaseMixin` and its thread safe `_print` method.

```python
from riposte import Riposte
from riposte.printer.mixins import PrinterBaseMixin


class CustomPrinterMixin(PrinterBaseMixin):
    def ask(self, *args, **kwargs):  # adding new one
        self._print((*args, "???"), **kwargs)
        
    def shout(self, *args, **kwargs):  # adding new one
        self._print((*args, "!!!"), **kwargs)

class CustomRiposte(Riposte, CustomPrinterMixin):
    pass
 
repl = CustomRiposte()

@repl.command("foobar")
def foobar(message: str):
    repl.shout(message)
    repl.ask(message)
    repl.success(message)  # It'll raise exception as it's no longer available
```

#### Coloring output with `Pallete`
If you feel like adding a few colors to the output you can always use `Pallete`.

```python
from riposte import Riposte
from riposte.printer import Palette


repl = Riposte()


@repl.command("foo")
def foo(msg: str):
    repl.print(Palette.GREEN.format(msg))  # It will be green
```

`Pallete` goes with the following output formattings:
* `GREY`
* `RED`
* `GREEN`
* `YELLOW`
* `BLUE`
* `MAGENTA`
* `CYAN`
* `WHITE`
* `BOLD`

### History
Command history is stored in your HOME directory in `.riposte` file. 
The default length is 100 lines. Both settings can be changed using 
`history_file` and `history_length` parameters.
```python
from pathlib import Path
from riposte import Riposte


repl = Riposte(
    history_file=Path.home() / ".custom_history_file", 
    history_length=500,
)
```

### Prompt
The default prompt is `riposte:~ $ ` but you can easily customize it:
```python
from riposte import Riposte


repl = Riposte(prompt="custom-prompt >>> ")
repl.run()
```

You can also dynamically resolve prompt layout based on the state of some object 
simply by overwriting `Riposte.prompt` property. In the following example, we'll 
determine prompt based on `MODULE` value:
```python
from riposte import Riposte


class Application:
    def __init__(self):
        self.module = None


class CustomRiposte(Riposte):
    @property
    def prompt(self):
        if app.module:
            return f"foo:{app.module} > "
        else:
            return self._prompt  # reference to `prompt` parameter.


app = Application()
repl = CustomRiposte(prompt="foo > ")


@repl.command("set")
def set_module(module_name: str):
    app.module = module_name
    repl.success("Module has been set.")


@repl.command("unset")
def unset_module():
    app.module = None
    repl.success("Module has been unset.")


repl.run()
```

```bash
foo > set bar
[+] Module has been set.
foo:bar > unset
[+] Module has been unset.
foo >
```

### Banner
```python
# banner.py

from riposte import Riposte

BANNER = """ _   _      _ _         _    _            _     _ _ 
| | | |    | | |       | |  | |          | |   | | |
| |_| | ___| | | ___   | |  | | ___  _ __| | __| | |
|  _  |/ _ \ | |/ _ \  | |/\| |/ _ \| '__| |/ _` | |
| | | |  __/ | | (_) | \  /\  / (_) | |  | | (_| |_|
\_| |_/\___|_|_|\___/   \/  \/ \___/|_|  |_|\__,_(_)
Welcome User Hello World v1.2.3
"""

repl = Riposte(banner=BANNER)


@repl.command("hello")
def hello():
    repl.print("Hello World!")


repl.run()
```
```bash
$ python banner.py
 _   _      _ _         _    _            _     _ _ 
| | | |    | | |       | |  | |          | |   | | |
| |_| | ___| | | ___   | |  | | ___  _ __| | __| | |
|  _  |/ _ \ | |/ _ \  | |/\| |/ _ \| '__| |/ _` | |
| | | |  __/ | | (_) | \  /\  / (_) | |  | | (_| |_|
\_| |_/\___|_|_|\___/   \/  \/ \___/|_|  |_|\__,_(_)
Welcome User Hello World v1.2.3

riposte:~ $
```
If for some reason you don't want to display banner (Maybe you have custom 
[input stream](#adding-custom-input-stream)?) you can set `Riposte.print_banner` attribute 
to `False`.

### Inline command execution
Similarly to the `bash` if you delimit commands with semicolon you can trigger 
execution of multiple commands in one line.
```bash
riposte:~ $ hello; hello; hello
[+] Is it me you looking for?
[+] Is it me you looking for?
[+] Is it me you looking for?
```
`Riposte` also exposes CLI for your applications which gives you the ability to 
pass commands using `-c` switch:
```bash
$ python app.py -c "hello; hello; hello;"
[+] Is it me you looking for?
[+] Is it me you looking for?
[+] Is it me you looking for?
$ 
```
Given all of this, you can also start to treat your application as something 
that could be turned into automated scripts.

### CLI
If you application needs custom CLI arguments _Riposte_ gives you way to 
implement it by overwriting `Riposte.setup_cli()` method. Let's say you want to 
introduce `--verbose` flag into your application:
```python
# custom_cli_args.py

from riposte import Riposte


class CustomArgsRiposte(Riposte):
    def setup_cli(self):
        super().setup_cli()  # preserve default Riposte CLI

        self.parser.add_argument(
            "-v", "--verbose", action="store_true", help="Verbose mode"
        )


repl = CustomArgsRiposte()


@repl.command("foo")
def foo(bar: str):
    repl.success("Foobar executed.")

    if repl.arguments.verbose:
        repl.success("Argument passed as bar: ", bar)


repl.run()

```
```bash
$ python custom_cli_args.py -v
riposte:~ $ foo 123
[+] Foobar executed.
[+] Argument passed as bar:  123
riposte:~ $ 
```
`Riposte.parser` is an instance of Python's builtin [`argparse.ArgumentParser`](https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser) 
so for all further instructions regarding adding CLI arguments please follow 
[`argparse`](https://docs.python.org/3/library/argparse.html#module-argparse) 
documentation.

Passed arguments are being parsed in `Riposte.run()` and stored in 
`Riposte.arguments` so you can access it within your application. If you need 
to access them before entering the main evaluation loop you can overwrite 
`Riposte.parse_cli_arguments()`
```python
from riposte import Riposte


class CustomArgsRiposte(Riposte):
    def setup_cli(self):
        super().setup_cli()  # preserve default Riposte CLI

        self.parser.add_argument(
            "-v", "--verbose", action="store_true", help="Verbose mode"
        )

    def parse_cli_arguments(self):
        super().parse_cli_arguments()  # preserve default Riposte CLI

        if self.arguments.verbose:
            do_something_specific()
```

### Input streams
The input stream is an abstraction telling how you feed _Riposte_ with 
commands. Right now you can use following ones out of the box.
#### Prompt
Default one which allows you input commands using the traditional prompt.
#### CLI
`Riposte` also exposes CLI for your applications which gives you the ability 
to pass commands using `-c` switch:
```bash
$ python app.py -c "hello; hello; hello;"
[+] Is it me you looking for?
[+] Is it me you looking for?
[+] Is it me you looking for?
```
#### File
You can also pass text file containing commands as an argument to your 
application:
```python
# demo.py

from riposte import Riposte

repl = Riposte()

@repl.command("hello")
def hello():
    repl.print("Is it me you looking for?")

repl.run()
```
`commands.rpst` text file containing commands to be executed:
```
hello
hello
hello
```
```bash
$ python demo.py commands.rpst
[+] Is it me you looking for?
[+] Is it me you looking for?
[+] Is it me you looking for?
```
#### Adding custom input stream
If for some reason you need a custom way of feeding _Riposte_ with commands 
you can always add your custom input stream. The input stream is a generator 
that yields function which after calling it returns a string (the command) 
`Generator[Callable[[], str], None, None]`. Let's say you are an evil genius 
and want to make your interactive shell application less interactive by 
feeding it with some kind of messaging system.
```python
import itertools
from typing import Callable, Generator

from riposte import Riposte
from some.messaging.system import Subscriber


def some_messaging_system_input_stream(
    subscriber: Subscriber  # you can parametrize your input streams
) -> Generator[Callable, None, None]:
    # itertools.repeat() make sure that your input stream runs forever
    yield from itertools.repeat(subscriber.poll)  # calling poll() will return command


class CustomInputStreamRiposte(Riposte):
    def setup_cli(self):
        super().setup_cli()  # preserve default Riposte CLI

        self.parser.add_argument(
            "-h", "--host", help="Some messaging system address"
        )

    def parse_cli_arguments(self) -> None:
        super().parse_cli_arguments()  # preserve default Riposte CLI

        if self.arguments.host:
            subscriber = Subscriber(self.arguments.host)
            self.input_stream = some_messaging_system_input_stream(subscriber)
            self.print_banner = False  # I guess you don't want to print banner 
```

## Project status
_Riposte_ is under development. It might be considered to be in beta phase. 
There might be some breaking changes in the future although a lot of concepts 
present here was already battle-tested during 
[routersploit](https://github.com/threat9/routersploit) development.

## Contributing
Please read [CONTRIBUTING.md]() for details on our code of conduct, and the 
process for submitting pull requests to us.

## Versioning
Project uses [SemVer](http://semver.org/) versioning. For the versions 
available, see the [releases](https://github.com/fwkz/riposte/releases). 

## License
_Riposte_ is licensed under the MIT License - see the 
[LICENSE](https://github.com/fwkz/riposte/blob/master/LICENSE) file for details

## Acknowledgments
* [routersploit](https://github.com/threat9/routersploit)
* [click](https://click.palletsprojects.com/)
