"""Miscellaneous tools and shortcuts"""
import inspect
import types
import typing as t
from datetime import datetime
from functools import wraps
from dataclasses import Field, field

from toolz import excepts


def apply(func, args=(), kwargs=None):
    """apply args and kwargs to a function"""
    return func(*args, **kwargs or {})


def notnone(obj):
    """return whether an object is not None"""
    return obj is not None


class StrRepr():
    """mixin which adds a ``__repr__`` based on ``__str__``"""

    def __str__(self):
        return '{0.__class__.__name__} object'.format(self)

    def __repr__(self):
        return '<{0.__class__.__name__}: {0}>'.format(self)


class NO_DEFAULT:
    """sentinel for no default"""


def lookup_defaults(lookup, default):
    return excepts(LookupError, lookup, lambda _: default)


def skipnone(func):
    """wrap a function so that it returns None when getting None as input"""
    @wraps(func)
    def wrapper(arg):
        return None if arg is None else func(arg)

    return wrapper


def parse_iso8601(dtstring: str) -> datetime:
    """naive parser for ISO8061 datetime strings,

    Parameters
    ----------
    dtstring
        the datetime as string in one of two formats:

        * ``2017-11-20T07:16:29+0000``
        * ``2017-11-20T07:16:29Z``

    """
    return datetime.strptime(
        dtstring,
        '%Y-%m-%dT%H:%M:%SZ' if len(dtstring) == 20 else '%Y-%m-%dT%H:%M:%S%z')


def genresult(gen, value):
    """retrieve the return value from a generator"""
    try:
        gen.send(value)
    except StopIteration as e:
        return e.value
    else:
        raise TypeError('generator did not return as expected')


def func_to_fields(func: types.FunctionType) -> t.List[Field]:
    """get dataclass fields from a function signature

    Parameters
    ----------
    func
        a python function

    Notes
    -----
    * keyword-only, varargs, and varkeywords are not supported
    """
    spec = inspect.getfullargspec(func)
    defaults = dict(zip(reversed(spec.args), reversed(spec.defaults or ())))
    if spec.kwonlyargs:
        raise TypeError('keyword-only args not supported')
    elif spec.varargs:
        raise TypeError('varargs not supported')
    elif spec.varkw:
        raise TypeError('varkw not supported')
    return [
        (name,
         spec.annotations.get(name, t.Any),
         field(default=defaults[name]) if name in defaults else field())
        for name in spec.args
    ]
