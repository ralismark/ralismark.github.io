import inspect
import typing as t

import jinja2

_R = t.TypeVar("_R")


def pass_heron(fn: t.Callable[..., _R]) -> t.Callable[..., _R]:
    """
    Pass heron variables to the wrapped function.
    """

    sig = inspect.signature(fn)

    heron_vars = {"__file__"}
    heron_vars.intersection_update(sig.parameters.keys())

    # HACK internals
    pass_context = getattr(fn, "jinja_pass_arg", None) is jinja2.utils._PassArg.context

    @jinja2.pass_context
    def decorated(context: jinja2.runtime.Context, *args, **kwargs):
        for var in heron_vars:
            kwargs[var] = context.get(var)
        if pass_context:
            return fn(context, *args, **kwargs)
        else:
            return fn(*args, **kwargs)

    return decorated


class GetItemWrapper:
    def __init__(self, d: dict):
        self.__dict = d

    def __getitem__(self, name):
        return self.__dict[name]
