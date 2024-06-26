"""
Various basic recipe types
"""

import dataclasses
import typing as t
from pathlib import Path, PurePosixPath

from .. import core, util
from ..jinja.registry import jinja_recipe_builder


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


_R = t.TypeVar("_R")


@dataclasses.dataclass(frozen=True)
class FnRecipe(core.Recipe[_R]):
    """
    Decorator to generate a recipe from a function.
    """

    fn: t.Callable[[core.BuildContext], _R]

    def build_impl(self, ctx: core.BuildContext) -> _R:
        return self.fn(ctx)


@dataclasses.dataclass(frozen=True)
class ReadTextRecipe(core.Recipe[str], InputMixin):
    """
    Read the contents of a file, as a string.
    """

    def build_impl(self, ctx: core.BuildContext) -> str:
        with ctx.input(self.path).open("rt") as f:
            return f.read()

    @jinja_recipe_builder("read")
    @staticmethod
    def jinja(
        path: str | PurePosixPath,
        *,
        __file__: Path,
    ) -> "ReadTextRecipe":
        return ReadTextRecipe(
            path=__file__.parent / path,
        )


@dataclasses.dataclass(frozen=True)
class ReadBinaryRecipe(core.Recipe[bytes], InputMixin):
    """
    Read the contents of a file, as bytes.
    """

    def build_impl(self, ctx: core.BuildContext) -> bytes:
        with ctx.input(self.path).open("rb") as f:
            return f.read()

    @jinja_recipe_builder("readb")
    @staticmethod
    def jinja(
        path: str | PurePosixPath,
        *,
        __file__: Path,
    ) -> "ReadBinaryRecipe":
        return ReadBinaryRecipe(
            path=__file__.parent / path,
        )


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

    @jinja_recipe_builder("write")
    @staticmethod
    def jinja(
        content: str | bytes,
        out: str,
    ) -> "WriteRecipe":
        return WriteRecipe(
            out=util.canonicalise_opath(out),
            content=content,
        )


@dataclasses.dataclass(frozen=True)
class ReadDirRecipe(core.Recipe[tuple[Path, ...]], InputMixin):
    """
    List files in a directory.
    """

    def build_impl(self, ctx: core.BuildContext) -> tuple[Path, ...]:
        return tuple(ctx.input(self.path).iterdir())

    @jinja_recipe_builder("readdir")
    @staticmethod
    def jinja(
        path: str | PurePosixPath,
        *,
        __file__: Path,
    ) -> "ReadDirRecipe":
        return ReadDirRecipe(
            path=__file__.parent / path,
        )
