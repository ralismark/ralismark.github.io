"""
Other code can register jinja filters/etc to here.
"""

import dataclasses
import inspect
import typing as t
from pathlib import Path

import jinja2

from .. import core

RECIPE_FILTERS: dict[str, t.Callable] = dict()


def pass_heron[R](fn: t.Callable[..., R]) -> t.Callable[..., R]:
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


def recipe_class_as_builder(cls: type[core.Recipe]) -> t.Callable:
    # get class construction signature signature
    sig = inspect.signature(cls.__init__)
    sig = sig.replace(parameters=list(sig.parameters.values())[1:])

    @jinja2.pass_context
    def builder(context: jinja2.runtime.Context, *args, **kwargs):
        # bind to get names (and thus associated type) for each arg
        bound: inspect.BoundArguments = sig.bind(*args, **kwargs)

        # munge values based on type
        for name, value in bound.arguments.items():
            param: inspect.Parameter = sig.parameters[name]
            # input paths are relative to processed file
            if param.annotation in (Path, dataclasses.InitVar[Path]):
                assert isinstance(value, Path) or (isinstance(value, str) and not value.startswith("/"))
                bound.arguments[name] = context.get("__file__").parent / value
            # output paths are absolute
            if param.annotation in (core.Pathish, dataclasses.InitVar[core.Pathish]):
                assert isinstance(value, str) and value.startswith("/")

        recipe = cls(*bound.args, **bound.kwargs)
        return core.current_ctx().build(recipe)

    return builder


class RecipeBook:
    def __getattr__(self, name):
        registered = RECIPE_FILTERS.get(name)
        if registered:
            return registered

        classname = "".join(word.title() for word in name.split("_")) + "Recipe"
        for recipe in core.RECIPES_FROM_DECORATION:
            if recipe.__name__ == classname:
                return recipe_class_as_builder(recipe)

        raise AttributeError(f"No recipe {name!r} or recipe class {classname!r}")
