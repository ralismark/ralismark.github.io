import typing as t
from pathlib import Path
import datetime as dt

import heron

here = Path(__file__).parent


def book_page_recipe(
    ctx: heron.core.BuildContext,
    path: Path,
    jenv,
):
    r = heron.PageRecipe(path, f"/media/{path.stem}.html", jenv)
    meta = t.cast(heron.PageInout, ctx.build(r.meta))

    rating_str: str | None = None

    rating = meta.get("rating")
    if isinstance(rating, int):
        rating_str = ("🟡" * rating).ljust(5, "⚫")

    return r.extend_props(
        rating_str=rating_str,
        excerpt=f"By {meta['author']} — Read {t.cast(dt.date, meta["date"]).strftime('%-d %b %Y')} — {rating_str}",
    )


def main(
    ctx: heron.core.BuildContext,
    make_collection,
    jenv,
):
    yield heron.PageRecipe(
        here / "_index.html",
        "/media/index.html",
        jenv,
    )

    interactives = yield from make_collection(
        ctx,
        (
            book_page_recipe(ctx, path, jenv)
            for path in ctx.input(here).iterdir()
            if not path.stem.startswith("_")
        ),
    )

    return interactives
