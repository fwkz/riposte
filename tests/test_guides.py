from typing import AnyStr, Dict, List, Set, Text
from unittest import mock

import pytest

from riposte import Riposte, guides
from riposte.exceptions import GuideError


@mock.patch("riposte.guides.ast")
def test_literal(mocked_ast):
    value = "foo"

    processed_value = guides.literal(value)

    mocked_ast.literal_eval.assert_called_once_with(value)
    assert processed_value == mocked_ast.literal_eval.return_value


@mock.patch("riposte.guides.ast")
def test_literal_exception(mocked_ast):
    mocked_ast.literal_eval.side_effect = TypeError

    with pytest.raises(GuideError):
        guides.literal("foo")


def test_encode():
    mocked_value = mock.Mock()

    processed_value = guides.encode(mocked_value)

    mocked_value.encode.assert_called_once_with()
    assert processed_value == mocked_value.encode.return_value


def test_encode_exception():
    mocked_value = mock.Mock()
    mocked_value.encode.side_effect = UnicodeEncodeError

    with pytest.raises(GuideError):
        guides.encode(mocked_value)


@pytest.mark.parametrize(
    ("type_", "return_value"),
    (
        (str, tuple()),
        (AnyStr, tuple()),
        (Text, tuple()),
        (bytes, (guides.encode,)),
        (int, (guides.literal,)),
        (Dict, (guides.literal,)),
        (List, (guides.literal,)),
        (Set, (guides.literal,)),
    ),
)
def test_get_guides(type_, return_value):
    assert guides.get_guides(type_) == return_value


@mock.patch("riposte.guides.get_guides")
def test_extract_guides(mocked_get_guides):
    type_hint = int
    func = mock.Mock(__annotations__={"foo": type_hint})

    extracted_guides = guides.extract_guides(func)

    mocked_get_guides.assert_called_once_with(type_hint)
    assert extracted_guides == {"foo": mocked_get_guides.return_value}


@pytest.mark.parametrize(
    ("input", "guide", "expected"),
    (
        ("foobar", str, "foobar"),
        ("'foobar'", str, "foobar"),
        ("'foo bar'", str, "foo bar"),
        ("foobar", bytes, b"foobar"),
        ("'foobar'", bytes, b"foobar"),
        ("'foo bar'", bytes, b"foo bar"),
        ("1", int, 1),
        ("'1'", int, 1),
        ("\"[1, 'foo']\"", list, [1, "foo"]),
        ("\"{'foo': 'bar'}\"", dict, {"foo": "bar"}),
    ),
)
@mock.patch("builtins.input")
def test_guides(mocked_input, input, guide, expected, repl: Riposte):
    mocked_input.return_value = "foobar " + input

    @repl.command("foobar")
    def handler_function(x: guide):
        assert x == expected

    repl._process()
