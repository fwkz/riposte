import ast
from typing import Any, AnyStr, Callable, Dict, Tuple

from riposte.exceptions import GuideError


def literal(value: str) -> Any:
    try:
        return ast.literal_eval(value)
    except Exception:
        raise GuideError(value, literal)


def encode(value: str) -> Any:
    try:
        return value.encode()
    except Exception:
        raise GuideError(value, encode)


def get_guides(annotation) -> Tuple[Callable]:
    """ Based on given annotation get chain of guides. """

    if annotation is AnyStr:
        return ()
    elif issubclass(annotation, str):
        return ()
    elif issubclass(annotation, bytes):
        return (encode,)
    else:
        return (literal,)


def extract_guides(func: Callable) -> Dict[str, Tuple[Callable]]:
    """ Extract guides out of type-annotations. """
    return {
        arg: get_guides(annotation)
        for arg, annotation in func.__annotations__.items()
    }
