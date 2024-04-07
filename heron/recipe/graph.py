import dataclasses
from pathlib import Path, PurePosixPath

import graphviz

from .. import core
from ..jinja.registry import jinja_recipe_builder
from . import inout


@dataclasses.dataclass(frozen=True)
class GraphvizRecipe(inout.InoutRecipeBase):
    engine: str

    def build_impl(self, ctx: core.BuildContext) -> inout.Inout:
        # TODO don't fill the background
        # TODO make the stroke color depend on color-scheme -- use CanvasText maybe?
        graphviz.render(
            engine=self.engine,
            filepath=ctx.input(self.path),
            outfile=ctx.output(self.opath),
        )
        return self.inout()

    @jinja_recipe_builder("graphviz")
    @staticmethod
    def jinja(
        path: str | PurePosixPath,
        out: str,
        layout: str = "dot",
        *,
        __file__: Path,
    ) -> "GraphvizRecipe":
        return GraphvizRecipe(
            path=__file__.parent / path,
            out=out,
            engine=layout,
        )
