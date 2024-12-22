#!/usr/bin/env python3

import typing as t
from pathlib import Path
import os
import re
import dataclasses

from frozendict import frozendict

import heron

here = Path(__file__).parent

site = {
    "drafts": os.getenv("HERON_ENV") == "development",
    "url": "https://www.ralismark.xyz",
    "title": "ralismark.xyz",
    "description": "Where temmie puts her internet things!",
    "me": {
        "email": "tem@ralismark.xyz",
    },
}

jenv = heron.jinja.base_env.overlay(
    loader=heron.jinja.Loader(here),
)
jenv.globals["site"] = heron.util.Impurity(lambda: site)


def one(x: t.Iterable):
    items = list(x)
    if len(items) == 1:
        return items[0]
    raise ValueError(f"expected 1 item, got {len(items)}")


@heron.util.setitem(jenv.globals, "parse_tags")
def parse_tags(
    page: t.Mapping
):
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

    def extract_draft(path: Path):
        m = re.match("([A-Z]+)-", path.stem)
        if m is not None:
            return m.group(1)
        return None

    pages = (page.extend_props(draft=extract_draft(page.path)) for page in pages)
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
            posts=heron.util.Impurity(
                lambda: tuple(r.meta for r in out),
            ),
        )
        for i, r in enumerate(pages)
    )
    return out


def inner_main(ctx: heron.core.BuildContext):
    posts: tuple
    interactives: tuple
    garden: tuple

    site["series"] = heron.util.Impurity(
        lambda: {
            "posts": posts,
            "interactives": interactives,
            "garden": garden,
        }
    )

    # initialise series

    posts = make_series(
        ctx,
        (
            heron.recipe.PageRecipe(path, f"/posts/{path.stem}.html", jenv)
            for path in ctx.input(here / "posts").iterdir()
        ),
    )
    yield from posts

    interactives = make_series(
        ctx,
        (
            heron.recipe.PageRecipe(path, f"/interactives/{path.stem}.html", jenv)
            for path in ctx.input(here / "interactives").iterdir()
        ),
    )
    yield from interactives

    garden = tuple(
        heron.recipe.PageRecipe(
            path, f"/garden/{path.stem}.html", jenv, props=frozendict(noindex=True)
        )
        for path in ctx.input(here / "garden").iterdir()
    )
    yield from garden

    # root pages

    for root_page_glob in ["*.html", "*.md", "*.d"]:
        for path in ctx.input(here).glob(root_page_glob):
            yield heron.recipe.PageRecipe(path, f"/{path.stem}.html", jenv)

    # extra stuff

    yield heron.recipe.CopyRecipe(here / "robots.txt", "/robots.txt")
    yield heron.recipe.SassRecipe(
        here / "layout/css/main-foundation.scss",
        "/assets/foundation.css",
        include_paths=(str(here / "layout/css"),),
    )

    yield RecursiveCopy(here / "the-fruit-loop", "/the-fruit-loop")


@dataclasses.dataclass(frozen=True)
class RecursiveCopy(heron.recipe.InoutRecipeBase):
    def build_impl(self, ctx: heron.core.BuildContext):
        if ctx.input(self.path).is_dir():
            for entry in ctx.input(self.path).iterdir():
                ctx.build(RecursiveCopy(entry, self.opath / entry.name))
        else:
            ctx.build(heron.recipe.CopyRecipe(self.path, self.opath))


@heron.recipe.FnRecipe
def main(ctx: heron.core.BuildContext):
    recipes = [r for r in inner_main(ctx)]
    for r in recipes:
        ctx.build(r)
