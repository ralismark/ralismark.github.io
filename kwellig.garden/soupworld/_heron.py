from pathlib import Path

import heron

here = Path(__file__).parent


def main(
    ctx: heron.core.BuildContext,
    make_collection,
    jenv,
):
    interactives = make_collection(
        ctx,
        (
            heron.recipe.PageRecipe(path, f"/interactives/{path.stem}.html", jenv)
            for path in ctx.input(here).iterdir()
            if not path.stem.startswith("_")
        ),
        require_date=False,
    )
    yield from interactives

    return interactives
