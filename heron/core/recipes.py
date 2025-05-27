"""
Basic recipe and helpers for making recipes.
"""

import dataclasses
import inspect
import os
import shutil
import typing as t
from collections.abc import Callable
from pathlib import Path, PurePosixPath

from frozendict import frozendict

from .kernel import BuildContext, Recipe

__all__ = [
    "RecipeFromDecorator",
    "RECIPES_FROM_DECORATION",
    "recipe",
    "Pathish",
    "canonicalise_opath",
    "InputMixin",
    "OutputMixin",
    "permalink",
    "Inout",
    "InoutMixin",
    "NullRecipe",
    "null_recipe",
    "LoadRecipe",
    "FnRecipe",
    "ReadRecipe",
    "WriteRecipe",
    "ReaddirRecipe",
    "CopyRecipe",
]


class RecipeFromDecorator[**P, R](Recipe[R]):
    inner: t.ClassVar[Callable]

    def __init__(self, *args: P.args, **kwargs: P.kwargs): ...


RECIPES_FROM_DECORATION: list[type[Recipe]] = list()


def recipe[**P, R]() -> (
    Callable[
        [Callable[t.Concatenate[BuildContext, P], R]], type[RecipeFromDecorator[P, R]]
    ]
):
    """
    Decorator to turn functions into recipes
    """

    # `recipe` is a function to allow addition of arguments :)

    def decorate(
        fn: Callable[t.Concatenate[BuildContext, P], R],
    ) -> type[RecipeFromDecorator[P, R]]:
        sig = inspect.signature(fn)

        sig_without_ctx = sig.replace(
            parameters=list(sig.parameters.values())[1:],
        )

        class recipetype(RecipeFromDecorator[P, R]):
            inner: t.ClassVar = fn

            _args: frozendict

            def __init__(self, *args: P.args, **kwargs: P.kwargs):
                arguments = sig_without_ctx.bind(*args, **kwargs)
                arguments.apply_defaults()
                object.__setattr__(self, "_args", frozendict(arguments.arguments))

            def build_impl(self, ctx: BuildContext) -> R:
                arguments = inspect.BoundArguments(sig_without_ctx, self._args)
                return fn(ctx, *arguments.args, **arguments.kwargs)

            def __setattr__(self, name, value):
                raise TypeError(f"'{self.__class__.__name__}' object is read-only")

            def __hash__(self):
                return hash(self._args)

            def __eq__(self, other):
                return type(self) is type(other) and self._args == other._args

            def __repr__(self) -> str:
                return (
                    self.__class__.__name__
                    + "("
                    + ", ".join(f"{k}={v!r}" for k, v in self._args.items())
                    + ")"
                )

        # patch the name
        recipetype.__name__ = fn.__name__
        recipetype.__qualname__ = fn.__qualname__
        recipetype.__module__ = fn.__module__
        recipetype.__doc__ = fn.__doc__

        # patch init signature
        params = list(sig.parameters.values())
        # replace ctx with self
        params[0] = inspect.signature(recipetype.__init__).parameters["self"]
        recipetype.__init__.__signature__ = sig.replace(parameters=params, return_annotation=inspect.Signature.empty)  # type: ignore[attr-defined]

        RECIPES_FROM_DECORATION.append(recipetype)
        return recipetype

    return decorate


# -----------------------------------------------------------------------------


Pathish = str | os.PathLike[str]


def canonicalise_opath(url: Pathish) -> PurePosixPath:
    """
    Parse an output path into a PurePosixPath.
    """
    url = os.fspath(url)

    if url.endswith("/"):
        raise ValueError("output path cannot end in /")

    # handle . and .. and empty components
    parts: list[str] = []
    for part in url.split("/"):
        if part == "..":
            if not parts:
                raise ValueError("output path has too many .. components")
            parts.pop()
        elif part not in ("", "."):
            parts.append(part)

    return PurePosixPath(*parts)


@dataclasses.dataclass(frozen=True)
class InputMixin:
    """
    Helper base class to unify input specification.

    When combining with InputMixin, specify OutputMixin first.
    """

    path: Path


@dataclasses.dataclass(frozen=True)
class OutputMixin:
    """
    Helper base class to unify output specification, and handle
    canonicalisation.

    When combining with InputMixin, specify OutputMixin first.
    """

    # i don't like that dataclasses works this way

    opath: PurePosixPath = dataclasses.field(init=False)
    out: dataclasses.InitVar[Pathish]

    def __post_init__(self, out: Pathish):
        object.__setattr__(self, "opath", canonicalise_opath(out))


def permalink(path: PurePosixPath) -> str:
    """
    Get the permalink for an output path.
    """
    path = "/" / path  # TODO support alternate baseurls
    if path.name == "index.html":
        if path.parent == PurePosixPath("/"):
            return "/"
        return f"{path.parent}/"
    if path.suffix == ".html":
        path = path.with_suffix("")
    return str(path)


@dataclasses.dataclass(frozen=True)
class Inout:
    """
    Result type for recipes producing a single file from a single file.
    """

    path: Path
    opath: PurePosixPath
    url: str = dataclasses.field(init=False)

    def __post_init__(self):
        object.__setattr__(self, "url", permalink(self.opath))

    def __str__(self):
        return self.url


@dataclasses.dataclass(frozen=True)
class InoutMixin[T: Inout](Recipe[Inout], OutputMixin, InputMixin):
    """
    Base for recipes that produce a single output file from a single input
    file.
    """

    def inout(self) -> Inout:
        return Inout(self.path, self.opath)


# -----------------------------------------------------------------------------


@recipe()
def NullRecipe(ctx: BuildContext) -> None:
    """
    Recipe that does nothing.

    Useful for examples/etc.
    """
    return None


null_recipe = NullRecipe()


@recipe()
def LoadRecipe(ctx: BuildContext, path: Path, name: str = "main") -> t.Any:
    """
    Load the variable `name` from python file at `path`.
    """

    ns: dict = {
        "__file__": str(path),
        "__name__": "__heron_main__",  # intentionally not __main__ to allow scripts to keep working
    }
    with ctx.input(path).open("rb") as f:
        code = compile(f.read(), path, "exec")
        exec(code, ns)

    if name not in ns:
        raise KeyError(f"nothing named {name!r} in {path}")
    return ns[name]


@recipe()
def FnRecipe[R](ctx: BuildContext, fn: Callable[[BuildContext], R]) -> R:
    """
    Adaptor, for use with lambdas etc.
    """
    return fn(ctx)


@recipe()
def ReadRecipe(ctx: BuildContext, path: Path, binary: bool = False) -> str:
    with ctx.input(path).open("rb" if binary else "rt") as f:
        return f.read()


@recipe()
def WriteRecipe(ctx: BuildContext, out: Pathish, content: str | bytes) -> str:
    opath = canonicalise_opath(out)

    mode = "wb" if isinstance(content, bytes) else "wt"
    with ctx.output(opath).open(mode) as f:
        f.write(content)
    return permalink(opath)


@recipe()
def ReaddirRecipe(ctx: BuildContext, path: Path) -> tuple[Path, ...]:
    return tuple(ctx.input(path).iterdir())


@recipe()
def CopyRecipe(ctx: BuildContext, out: Pathish, path: Path) -> Inout:
    opath = canonicalise_opath(out)

    shutil.copy2(
        src=ctx.input(path),
        dst=ctx.output(opath),
    )
    return Inout(path, opath)
