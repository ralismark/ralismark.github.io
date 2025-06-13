from pathlib import Path

import heron

here = Path(__file__).parent


def main(
    ctx: heron.core.BuildContext,
    make_collection,
    jenv,
):
    yield heron.PageRecipe(
        here / "_index.html",
        "/links/index.html",
        jenv,
    )

    interactives = yield from make_collection(
        ctx,
        (
            heron.PageRecipe(path, f"/links/{path.stem}.html", jenv)
            for path in ctx.input(here).iterdir()
            if not path.stem.startswith("_")
        ),
        require_date=False,
    )

    return interactives
