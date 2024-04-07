"""
Other code can register jinja filters/etc to here.
"""

import typing as t

import jinja2

from .. import core
from .utils import pass_heron

RECIPE_FILTERS: dict[str, t.Callable] = dict()


def jinja_recipe_builder(name: str):
    """
    Register a function that can be used to create a Recipe from within a Jinja
    template.
    """

    assert isinstance(name, str), "Did you forget to call the decorator?"

    def decorate(fn: t.Callable[..., core.Recipe]):
        if name in RECIPE_FILTERS:
            raise ValueError(f"jinja_recipe_builder already exists for name {name!r}")

        fn = pass_heron(fn)

        @jinja2.pass_context
        def decorated(context: jinja2.runtime.Context, *args, **kwargs):
            return core.current_ctx().build(fn(context, *args, **kwargs))
        RECIPE_FILTERS[name] = decorated
        return decorated

    return decorate


jinja_recipe_builder("build")(lambda recipe: recipe)
