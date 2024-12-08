from pathlib import Path

import heron

here = Path(__file__).parent

jenv = heron.jinja.base_env.overlay(
    loader=heron.jinja.Loader(here),
)


def inner_main(ctx: heron.core.BuildContext):
    for root_page_glob in ["*.html", "*.md", "*.d"]:
        for path in ctx.input(here).glob(root_page_glob):
            yield heron.recipe.PageRecipe(path, f"/{path.stem}.html", jenv)

    # extra stuff

    yield heron.recipe.CopyRecipe(here / "robots.txt", "/robots.txt")


@heron.recipe.FnRecipe
def main(ctx: heron.core.BuildContext):
    recipes = [r for r in inner_main(ctx)]
    for r in recipes:
        ctx.build(r)
