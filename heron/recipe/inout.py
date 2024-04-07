import dataclasses
import shutil
import typing as t
from pathlib import Path, PurePosixPath

from .. import core, util
from .basic import InputMixin, OutputMixin
from ..jinja.registry import jinja_recipe_builder


@dataclasses.dataclass(frozen=True)
class Inout:
    """
    Result type for recipes producing a single file from a single file.
    """

    path: Path
    opath: PurePosixPath
    url: str = dataclasses.field(init=False)

    def __post_init__(self):
        object.__setattr__(self, "url", util.permalink(self.opath))

    def __str__(self):
        return self.url


InoutT = t.TypeVar("InoutT", bound=Inout)


@dataclasses.dataclass(frozen=True)
class InoutRecipeBase(t.Generic[InoutT], core.Recipe[InoutT], OutputMixin, InputMixin):
    """
    Base for recipes that produce a single output file from a single input
    file.
    """

    def inout(self) -> Inout:
        return Inout(self.path, self.opath)


@dataclasses.dataclass(frozen=True)
class CopyRecipe(InoutRecipeBase):
    """
    Recipe to copy a file.
    """

    def build_impl(self, ctx: core.BuildContext) -> Inout:
        shutil.copy2(
            src=ctx.input(self.path),
            dst=ctx.output(self.opath),
        )
        return self.inout()

    @jinja_recipe_builder("copy")
    @staticmethod
    def jinja(
        path: str | PurePosixPath,
        out: str,
        *,
        __file__: Path,
    ) -> "CopyRecipe":
        return CopyRecipe(
            path=__file__.parent / path,
            out=out,
        )
