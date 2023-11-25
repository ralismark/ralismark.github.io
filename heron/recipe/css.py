import dataclasses
from pathlib import Path

import sass

from .. import core
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
