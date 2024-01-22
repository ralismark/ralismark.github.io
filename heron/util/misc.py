import typing as t
from frozendict import frozendict

_T = t.TypeVar("_T")
_F = t.TypeVar("_F")


def setitem(d: dict[_T, _F], key: _T) -> t.Callable[[_F], _F]:
    """
    Decorator for setting an item in a dict.
    """

    def decorate(fn: _F) -> _F:
        d[key] = fn
        return fn

    return decorate


Freezable = t.Union[
    t.Iterable["Freezable"],
    t.Mapping["Freezable", "Freezable"],
    t.Hashable,
]


def freeze(x: Freezable) -> t.Hashable:
    """
    Produce a immutable, hashable version of a value.
    """
    if isinstance(x, t.Hashable):
        return x
    elif isinstance(x, t.Mapping):
        return frozendict({freeze(k): freeze(v) for k, v in x.items()})
    elif isinstance(x, t.Iterable):
        return tuple(map(freeze, x))
    else:
        t.assert_never(x)
        raise TypeError("not freezable:", x)


class Impurity(t.Generic[_T]):
    """
    Explicit impurity that compares equal to other Impurities.
    """

    def __init__(self, fn: t.Callable[[], _T]):
        object.__setattr__(self, "_fn", fn)

    def __call__(self) -> _T:
        return object.__getattribute__(self, "_fn")()

    def __eq__(self, o):
        return type(o) is type(self)

    def __hash__(self):
        return hash(type(self)) ^ 1

    def __getattribute__(self, name: str):
        return getattr(self(), name)

    def __getitem__(self, key: str):
        return self()[key]

    def repr(self):
        fn = object.__getattribute__(self, "_fn")
        return f"Impurity({fn!r})"
