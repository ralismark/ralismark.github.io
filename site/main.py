#!/usr/bin/env python3

import typing as t
from pathlib import Path
import os

from frozendict import frozendict

import heron

here = Path(__file__).parent


jenv = heron.jinja.base_env.overlay(
    loader=heron.jinja.Loader(here),
)
jenv.globals["site"] = site = {
    "drafts": os.getenv("HERON_ENV") == "development",
    "url": "https://www.ralismark.xyz",
    "title": "ralismark.xyz",
    "description": "Where temmie puts her internet things!",
}


@heron.util.setitem(jenv.globals, "parse_tags")
def parse_tags(
    page: t.Union[heron.recipe.PageRecipe, heron.recipe.PageInout, t.Mapping]
):
    if isinstance(page, heron.core.Recipe):
        page = heron.core.current_ctx().build(page)
    if isinstance(page, heron.recipe.PageInout):
        page = page.props
    tags = page.get("tags")
    if tags is None:
        return []
    assert isinstance(tags, str)
    return tags.split()


def make_series(
    ctx: heron.core.BuildContext,
    pages: t.Iterable[heron.recipe.PageRecipe],
) -> tuple[heron.recipe.PageRecipe, ...]:
    def post_date(post: heron.recipe.PageRecipe):
        meta = ctx.build(post.meta)
        date = meta.props.get("date")
        if date is None:
            raise RuntimeError(f"{post.path} does not have date")
        return date

    pages = (
        page.extend_props(draft=page.path.stem.startswith("DRAFT")) for page in pages
    )
    pages = (page for page in pages if site["drafts"] or not page.props["draft"])
    pages = sorted(pages, key=post_date)
    out: tuple[heron.recipe.PageRecipe, ...]
    out = tuple(
        r.extend_props(
            prev=heron.util.Impurity(
                (lambda i: lambda: out[i - 1] if i > 0 else None)(i)
            ),
            next=heron.util.Impurity(
                (lambda i: lambda: out[i + 1] if i < len(out) - 1 else None)(i)
            ),
        )
        for i, r in enumerate(pages)
    )
    for p in out:
        ctx.build(p)
    return out


@heron.recipe.FnRecipe
def main(ctx: heron.core.BuildContext) -> None:
    ctx.build(heron.recipe.WriteRecipe("/CNAME", "www.ralismark.xyz"))
    ctx.build(heron.recipe.CopyRecipe(here / "robots.txt", "/robots.txt"))
    ctx.build(
        heron.recipe.SassRecipe(
            here / "layout/css/main-foundation.scss",
            "/assets/foundation.css",
            include_paths=(str(here / "layout/css"),),
        )
    )

    def build_root_page(glob: str, **kwargs):
        matches = list(ctx.input(here).glob(glob))
        if not matches:
            raise ValueError(f"no files matched glob {glob!r}")
        for path in matches:
            ctx.build(
                heron.recipe.PageRecipe(
                    path,
                    f"/{path.stem}.html",
                    jenv,
                    **kwargs,
                )
            )

    build_root_page("404.*")
    build_root_page("index.*")
    build_root_page("about.*")
    build_root_page("somewhere.*")

    interactives = make_series(
        ctx,
        (
            heron.recipe.PageRecipe(path, f"/interactives/{path.stem}.html", jenv)
            for path in ctx.input(here / "interactives").iterdir()
        ),
    )
    build_root_page("interactives.*", props=frozendict(posts=interactives))

    posts = make_series(
        ctx,
        (
            heron.recipe.PageRecipe(path, f"/posts/{path.stem}.html", jenv)
            for path in ctx.input(here / "posts").iterdir()
        ),
    )
    build_root_page("posts.*", props=frozendict(posts=posts))
