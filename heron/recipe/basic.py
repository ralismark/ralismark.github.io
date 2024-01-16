"""
Various basic recipe types
"""

import typing as t
import dataclasses
from pathlib import Path, PurePosixPath

from .. import core, util


@dataclasses.dataclass(frozen=True)
class InputMixin:
    """
    Helper base class to unify input specification.
    """

    path: Path


@dataclasses.dataclass(frozen=True)
class OutputMixin:
    """
    Helper base class to unify output specification, and handle
    canonicalisation.
    """

    # i don't like that dataclasses works this way

    opath: PurePosixPath = dataclasses.field(init=False)
    out: dataclasses.InitVar[util.Pathish]

    def __post_init__(self, out: util.Pathish):
        object.__setattr__(self, "opath", util.canonicalise_opath(out))


R = t.TypeVar("R")


@dataclasses.dataclass(frozen=True)
class FnRecipe(core.Recipe[R]):
    """
    Decorator to generate a recipe from a function.
    """

    fn: t.Callable[[core.BuildContext], R]

    def build_impl(self, ctx: core.BuildContext) -> R:
        return self.fn(ctx)


@dataclasses.dataclass(frozen=True)
class ReadTextRecipe(core.Recipe[str], InputMixin):
    """
    Read the contents of a file, as a string.
    """

    def build_impl(self, ctx: core.BuildContext) -> str:
        with ctx.input(self.path).open("rt") as f:
            return f.read()


@dataclasses.dataclass(frozen=True)
class ReadBinaryRecipe(core.Recipe[bytes], InputMixin):
    """
    Read the contents of a file, as bytes.
    """

    def build_impl(self, ctx: core.BuildContext) -> bytes:
        with ctx.input(self.path).open("rb") as f:
            return f.read()


@dataclasses.dataclass(frozen=True)
class WriteRecipe(core.Recipe[str], OutputMixin):
    """
    Write to a file.
    """

    content: t.Union[str, bytes]

    def build_impl(self, ctx: core.BuildContext) -> str:
        mode = "wb" if isinstance(self.content, bytes) else "wt"
        with ctx.output(self.opath).open(mode) as f:
            f.write(self.content)
        return util.permalink(self.opath)


@dataclasses.dataclass(frozen=True)
class ReadDirRecipe(core.Recipe[tuple[Path, ...]], InputMixin):
    """
    List files in a directory.
    """

    def build_impl(self, ctx: core.BuildContext) -> tuple[Path, ...]:
        return tuple(ctx.input(self.path).iterdir())
