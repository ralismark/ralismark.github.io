import dataclasses

import graphviz

from .. import core
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
