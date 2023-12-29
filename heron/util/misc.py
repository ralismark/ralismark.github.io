import typing as t
from frozendict import frozendict

T = t.TypeVar("T")
F = t.TypeVar("F")


def setitem(d: dict[T, F], key: T) -> t.Callable[[F], F]:
    """
    Decorator for setting an item in a dict.
    """

    def decorate(fn: F) -> F:
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


class Impurity(t.Generic[T]):
    """
    Explicit impurity that compares equal to other Impurities.
    """

    def __init__(self, fn: t.Callable[[], T]):
        object.__setattr__(self, "_fn", fn)

    def __call__(self) -> T:
        return object.__getattribute__(self, "_fn")()

    def __eq__(self, o):
        return type(o) is type(self)

    def __hash__(self):
        return hash(type(self)) ^ 1

    def __getattribute__(self, name: str):
        return getattr(self(), name)