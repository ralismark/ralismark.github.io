import heron


def inner_main(ctx: heron.core.BuildContext):
    yield heron.recipe.WriteRecipe(
        "index.html",
        """
<!doctype html>
<body>
Hello world!!
        """)
    yield heron.recipe.WriteRecipe(".nojekyll", "")


@heron.recipe.FnRecipe
def main(ctx: heron.core.BuildContext):
    recipes = [r for r in inner_main(ctx)]
    for r in recipes:
        ctx.build(r)
