"""
Heron recipes wrapped into functions that build them, so that they can be
easily used from Jinja.
"""

import typing as t
from pathlib import Path, PurePath

import jinja2
from frozendict import frozendict

from .. import core, util, recipe
from .utils import pass_heron

RECIPE_FILTERS: dict[str, t.Any] = dict()

_R = t.TypeVar("_R")


@util.setitem(RECIPE_FILTERS, "build")
@pass_heron
def recipe_build(
    recipe: core.Recipe[_R],
) -> _R:
    return core.current_ctx().build(recipe)


@util.setitem(RECIPE_FILTERS, "read")
@pass_heron
def recipe_read(
    path: t.Union[str, PurePath],
    *,
    __file__: Path,
) -> str:
    return core.current_ctx().build(
        recipe.ReadTextRecipe(
            __file__.parent / path,
        )
    )


@util.setitem(RECIPE_FILTERS, "write")
def recipe_write(
    content: t.Union[str, bytes],
    out: str,
) -> str:
    return core.current_ctx().build(
        recipe.WriteRecipe(
            util.canonicalise_opath(out),
            content,
        )
    )


@util.setitem(RECIPE_FILTERS, "readdir")
@pass_heron
def recipe_readdir(
    path: t.Union[str, PurePath],
    *,
    __file__: Path,
) -> tuple[Path, ...]:
    return core.current_ctx().build(
        recipe.ReadDirRecipe(
            __file__.parent / path,
        )
    )


@util.setitem(RECIPE_FILTERS, "copy")
@pass_heron
def recipe_copy(
    path: t.Union[str, PurePath],
    out: str,
    *,
    __file__: Path,
) -> recipe.Inout:
    return core.current_ctx().build(
        recipe.CopyRecipe(
            __file__.parent / path,
            out,
        )
    )


@util.setitem(RECIPE_FILTERS, "page")
@pass_heron
@jinja2.pass_context
def recipe_page(
    ctx: jinja2.runtime.Context,
    path: t.Union[str, PurePath],
    out: str,
    *,
    ext: t.Optional[str] = None,
    props: t.Mapping[str, util.Freezable] = dict(),
    inherit: t.Iterable[str] = tuple(),
    __file__: Path,
) -> recipe.Inout:
    child_props = {**props, **{k: ctx[k] for k in inherit}}

    return core.current_ctx().build(
        recipe.PageRecipe(
            __file__.parent / path,
            out,
            ctx.environment,
            ext=ext,
            props=t.cast(t.Any, util.freeze(child_props)),
        )
    )


@util.setitem(RECIPE_FILTERS, "sass")
@pass_heron
def recipe_sass(
    path: t.Union[str, PurePath],
    out: str,
    include: t.Union[str, PurePath, t.Sequence[t.Union[str, PurePath]]] = tuple(),
    *,
    __file__: Path,
) -> recipe.Inout:
    if isinstance(include, (str, PurePath)):
        include = [include]
    include = tuple(str(__file__.parent / p) for p in include)

    return core.current_ctx().build(
        recipe.SassRecipe(
            __file__.parent / path,
            out,
            include,
        )
    )


@util.setitem(RECIPE_FILTERS, "graphviz")
@pass_heron
def recipe_graphviz(
    path: t.Union[str, PurePath],
    out: str,
    layout: str = "dot",
    *,
    __file__: Path,
) -> recipe.Inout:
    return core.current_ctx().build(
        recipe.GraphvizRecipe(
            __file__.parent / path,
            out,
            layout,
        )
    )


@util.setitem(RECIPE_FILTERS, "posse_github")
def recipe_posse_github(
    owner: str,
    repo: str,
    title: str,
) -> str | None:
    return core.current_ctx().build(
        recipe.GitHubIssueRecipe(
            owner,
            repo,
            title,
        )
    )
