import dataclasses
import typing as t
from pathlib import Path, PurePosixPath

import sass

from .. import core
from ..jinja.registry import jinja_recipe_builder
from . import inout


@dataclasses.dataclass(frozen=True)
class SassRecipe(inout.InoutRecipeBase):
    include_paths: tuple[str, ...] = tuple()

    def build_impl(self, ctx: core.BuildContext) -> inout.Inout:
        # TODO there is an impurity with importing here, since adding a file
        # could change what was imported

        def handle_import(name: str, resolved: str):
            ctx.input(Path(resolved))

        content = sass.compile(
            filename=str(ctx.input(self.path)),
            output_style="compressed",
            include_paths=self.include_paths,
            importers=[(0, handle_import)],
        )
        with ctx.output(self.opath).open("w") as f:
            f.write(content)
        return self.inout()

    @jinja_recipe_builder("sass")
    @staticmethod
    def jinja(
        path: str | PurePosixPath,
        out: str,
        include: str | PurePosixPath | t.Sequence[str | PurePosixPath] = tuple(),
        *,
        __file__: Path,
    ) -> "SassRecipe":
        if isinstance(include, (str, PurePosixPath)):
            include = (include,)
        include = tuple(str(__file__.parent / p) for p in include)

        return SassRecipe(
            path=__file__.parent / path,
            out=out,
            include_paths=include,
        )
