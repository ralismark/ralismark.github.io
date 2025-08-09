#!/usr/bin/env python3

import typing as t
from pathlib import Path
import os
import re
import dataclasses
import datetime

from frozendict import frozendict

import heron

here = Path(__file__).parent

site = {
    "drafts": os.getenv("HERON_ENV") == "development",
    "url": "https://kwellig.garden",
    "fqdn": "kwellig.garden",
    "title": "Kwellig's Garden",
    "description": "Where temmie puts her internet things!",
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


@dataclasses.dataclass(frozen=True)
class Collection:
    pages: tuple[heron.PageRecipe, ...]
    series: frozendict[str, tuple[heron.PageRecipe, ...]]

    def __len__(self):
        return len(self.pages)

    def __iter__(self):
        return iter(self.pages)


def make_collection(
    ctx: heron.core.BuildContext,
    pages: t.Iterable[heron.PageRecipe],
    require_date: bool = True,
) -> t.Generator[heron.Recipe, None, Collection]:
    def post_date(meta: heron.PageInout):
        date = meta.props.get("date")
        if date is None:
            if require_date:
                raise RuntimeError(f"{meta.path:} no date")
            else:
                return datetime.date(9999, 1, 1)
        return date

    def extract_draft(path: Path):
        m = re.match("([A-Z]+)-", path.stem)
        if m is not None:
            return m.group(1)
        return None

    out: Collection

    # do the filtering and ordering
    pairs: t.Iterable[tuple[heron.PageRecipe, heron.PageInout]]
    pairs = ((page.extend_props(draft=extract_draft(page.path)), ctx.build(page.meta)) for page in pages)
    pairs = ((page, meta) for page, meta in pairs if site["drafts"] or not page.props["draft"])
    pairs = sorted(pairs, key=lambda p: post_date(p[1]))
    pairs = (
        (
            page.extend_props(
                prev=heron.util.Impurity(
                    (lambda i: lambda: out.pages[i - 1] if i > 0 else None)(i)
                ),
                next=heron.util.Impurity(
                    (lambda i: lambda: out.pages[i + 1] if i < len(out.pages) - 1 else None)(i)
                ),
                collection=heron.util.Impurity(
                    lambda: out
                ),
            ),
            meta
        )
        for i, (page, meta) in enumerate(pairs)
    )
    pairs = tuple(pairs)

    series: dict[str, list[heron.PageRecipe]] = dict()
    for page, meta in pairs:
        s = meta.props.get("series")
        if not s:
            continue
        if not isinstance(s, str):
            raise RuntimeError(f"{meta.path}: series is not a str")
        series.setdefault(s, list()).append(page)

    out = Collection(
        pages=tuple(page for page, meta in pairs),
        series=frozendict({k: tuple(v) for k, v in series.items()}),
    )
    yield from out.pages
    return out


def inner_main(ctx: heron.core.BuildContext):
    load: t.Callable = lambda path: ctx.build(heron.LoadRecipe(here / path))

    posts = yield from make_collection(
        ctx,
        (
            heron.PageRecipe(path, f"/posts/{path.stem}.html", jenv)
            for path in ctx.input(here / "posts").iterdir()
        ),
    )

    interactives = yield from make_collection(
        ctx,
        (
            heron.PageRecipe(path, f"/interactives/{path.stem}.html", jenv)
            for path in ctx.input(here / "interactives").iterdir()
        ),
    )

    garden = yield from make_collection(
        ctx,
        (
            heron.PageRecipe(
                path, f"/garden/{path.stem}.html", jenv, props=frozendict(noindex=True)
            )
            for path in ctx.input(here / "garden").iterdir()
        ),
        require_date=False,
    )

    soupworld: Collection = yield from load("soupworld/_heron.py")(ctx, make_collection, jenv)

    links: Collection = yield from load("links/_heron.py")(ctx, make_collection, jenv)

    site["collections"] = heron.util.Impurity(
        lambda: {
            "posts": posts,
            "interactives": interactives,
            "garden": garden,
            "soupworld": soupworld,
            "links": links,
        }
    )

    # root pages

    for root_page_glob in ["*.html", "*.md", "*.d"]:
        for path in ctx.input(here).glob(root_page_glob):
            yield heron.PageRecipe(path, f"/{path.stem}.html", jenv)

    # extra stuff

    yield heron.CopyRecipe("/favicon.ico", here / "favicon.ico")
    yield heron.CopyRecipe("/robots.txt", here / "robots.txt")
    yield heron.SassRecipe(
        here / "layout/css/main-foundation.scss",
        "/assets/foundation.css",
        include_paths=(str(here / "layout/css"),),
    )


@dataclasses.dataclass(frozen=True)
class RecursiveCopy(heron.InoutMixin):
    def build_impl(self, ctx: heron.core.BuildContext):
        if ctx.input(self.path).is_dir():
            for entry in ctx.input(self.path).iterdir():
                ctx.build(RecursiveCopy(entry, self.opath / entry.name))
        else:
            ctx.build(heron.CopyRecipe(self.opath, self.path))


@heron.FnRecipe
def main(ctx: heron.core.BuildContext):
    recipes = [r for r in inner_main(ctx)]
    for r in recipes:
        ctx.build(r)
