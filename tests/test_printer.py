from unittest import mock

import pytest

from riposte.printer import Palette
from riposte.printer.mixins import PrinterBaseMixin, PrinterMixin
from riposte.printer.thread import PrintResource


@pytest.fixture
def args():
    return "scoo", "bee", "doo"


@pytest.fixture
def kwargs():
    return {"sep": "-", "end": "+", "file": mock.Mock()}


@pytest.fixture
def printer_mixin():
    mixin = PrinterMixin()
    with mock.patch.object(mixin, "_print"):
        yield mixin


def test_palette():
    value = "scoobeedoo"
    assert (
        Palette.RED.format(value) == f"\033[{Palette.RED.value}m{value}\033[0m"
    )


def test_printer_mixin_info(printer_mixin, args, kwargs):
    printer_mixin.info(*args, **kwargs)
    printer_mixin._print.assert_called_once_with(*args, **kwargs)

    printer_mixin._print.reset_mock()

    printer_mixin.print(*args, **kwargs)
    printer_mixin._print.assert_called_once_with(*args, **kwargs)


def test_printer_mixin_error(printer_mixin, args, kwargs):
    printer_mixin.error(*args, **kwargs)
    printer_mixin._print.assert_called_once_with(
        "\033[91m[-]\033[0m", *args, **kwargs
    )


def test_printer_mixin_status(printer_mixin, args, kwargs):
    printer_mixin.status(*args, **kwargs)
    printer_mixin._print.assert_called_once_with(
        "\033[94m[*]\033[0m", *args, **kwargs
    )


def test_printer_mixin_success(printer_mixin, args, kwargs):
    printer_mixin.success(*args, **kwargs)
    printer_mixin._print.assert_called_once_with(
        "\033[92m[+]\033[0m", *args, **kwargs
    )


def test_printer_mixin_base(args, kwargs):
    printer_base_mixin = PrinterBaseMixin()
    printer_base_mixin._printer_thread = mock.Mock()

    printer_base_mixin._print(*args, **kwargs)

    printer_base_mixin._printer_thread.put.assert_called_once_with(
        PrintResource(content=args, **kwargs)
    )
