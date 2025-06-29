"""
Basic types that everything else is built on.
"""

import contextvars
import dataclasses
import time
import typing as t
from pathlib import Path, PurePosixPath

__all__ = [
    "BuildContext",
    "BuildFailure",
    "Driver",
    "DriverWrapper",
    "Manifest",
    "Recipe",
    "current_ctx",
]


@t.runtime_checkable
class Recipe[R](t.Protocol):
    """
    Recipe represents a single build task.

    Implementations of this interface SHOULD have value semantics -- two
    objects of the same class constructed the same way SHOULD compare equal.
    This fact is used by the builder to deduplicate recipes.
    """

    def build_impl(self, ctx: "BuildContext") -> R:
        """
        Perform the build step.

        The behaviour of this MUST only depend on member variables and the
        outputs of various methods of `ctx`.
        """
        raise NotImplementedError()


@dataclasses.dataclass(frozen=True)
class Manifest[R]:
    """
    Manifest is a record of the details of a single build run, including
    information to allow for dependency tracking and other behaviour.
    """

    @dataclasses.dataclass(frozen=True)
    class Input:
        """
        A path that was read.
        """

        path: Path
        time: float = dataclasses.field(compare=False, default_factory=time.time)

    @dataclasses.dataclass(frozen=True)
    class Output:
        """
        A path that was written to.
        """

        path: Path

    @dataclasses.dataclass(frozen=True)
    class SubRecipe:
        """
        A sub-recipe that was built.
        """

        recipe: Recipe
        manifest: "Manifest"

    @dataclasses.dataclass(frozen=True)
    class Trace:
        """
        A debug log
        """

        data: t.Any = dataclasses.field(compare=False)

    Entry: t.ClassVar = t.Union[Input, Output, SubRecipe, Trace]

    # the actual dataclass content

    recipe: Recipe[R]  # the recipe that was built
    value: R  # the return value of the recipe's build_impl
    log: tuple[Entry, ...]  # events that ocurred during build

    def filter[E: Manifest.Entry](self, entry_type: t.Type[E]) -> t.Iterable[E]:
        """
        Get log entries of a specific type.
        """
        for entry in self.log:
            if isinstance(entry, entry_type):
                yield entry


class BuildFailure(Exception):
    """
    Recipe failed to build.

    This exception is used to omit the recursive build failures.
    """

    def __init__(self, recipe: "Recipe"):
        super().__init__()
        self.recipe = recipe

    def __repr__(self):
        return f"BuildFailure({self.recipe!r})"

    def __str__(self):
        return f"failed to build: {self.recipe!r}"


class Driver:
    """
    Mediator for builds.
    """

    def __init__(self, builddir: Path):
        self.builddir: Path = builddir
        self.prev_driver: Driver | None = None

    @property
    def outermost_driver(self):
        d = self
        while d.prev_driver is not None:
            d = d.prev_driver
        return d

    def build[R](self, recipe: Recipe[R]) -> Manifest[R]:
        """
        Turn a Recipe into its resulting Manifest.
        """
        # TODO the driver argument is a horrible hack to make composition work

        try:
            hash(recipe)
        except TypeError:
            # catch this early before we run into it later
            raise TypeError(f"unhashable recipe: {recipe!r}")

        ctx = BuildContext(self.outermost_driver)

        tok = BuildContext.Current.set(ctx)
        try:
            val = recipe.build_impl(ctx)
        except BuildFailure:
            raise
        except Exception as e:
            raise BuildFailure(recipe) from e
        finally:
            BuildContext.Current.reset(tok)

        return Manifest(
            recipe=recipe,
            value=val,
            log=tuple(ctx._log),
        )

    def input(self, path: Path) -> Path:
        """
        Transform input paths, if needed.
        """

        path = path.resolve()
        return path

    def output(self, opath: PurePosixPath) -> Path:
        """
        Resolve an output path to the concrete path, performing any additional
        operation as needed.
        """

        if opath.is_absolute():
            raise ValueError("output path must be relative")
        # TODO validate that opath doesn't have too many .. components?

        path = self.builddir / opath
        path.parent.mkdir(parents=True, exist_ok=True)
        return path


class DriverWrapper(Driver):
    """
    Helper class for creating drivers that extend other drivers.
    """

    def __init__(self, driver: Driver):
        super().__init__(driver.builddir)
        self.next_driver: Driver = driver

        assert driver.prev_driver is None, "Attempting to wrap already wrapped driver"
        driver.prev_driver = self

    def build[R](self, recipe: Recipe[R]) -> Manifest[R]:
        return self.next_driver.build(recipe)

    def input(self, path: Path) -> Path:
        return self.next_driver.input(path)

    def output(self, opath: PurePosixPath) -> Path:
        return self.next_driver.output(opath)


@dataclasses.dataclass
class BuildContext:
    """
    Recipes receive this to have controlled access to impurities.

    This should not be subclassed. Instead, to modify behaviour subclass
    Driver.
    """

    Current: t.ClassVar[contextvars.ContextVar[t.Self]] = contextvars.ContextVar(
        "BuildContext.Current"
    )

    _driver: Driver
    _log: list[Manifest.Entry] = dataclasses.field(default_factory=list)

    def build[R](self, recipe: Recipe[R]) -> R:
        """
        Build a sub-recipe.
        """
        mf = self._driver.build(recipe)
        self._log.append(Manifest.SubRecipe(recipe, mf))
        assert mf, f"{self._driver!r}"
        return mf.value

    def output(self, opath: PurePosixPath) -> Path:
        """
        Resolve a file for writing.
        """
        path = self._driver.output(opath)
        self._log.append(Manifest.Output(path))
        return path

    def input(self, path: Path) -> Path:
        """
        Mark a file as an input.
        """
        # TODO do we wanna Path.normalize this?
        path = self._driver.input(path)
        self._log.append(Manifest.Input(path))
        return path

    def trace(self, data: t.Any):
        """
        Emit a debug trace.
        """
        self._log.append(Manifest.Trace(data))


def current_ctx() -> BuildContext:
    """
    Get the current BuildContext
    """
    return BuildContext.Current.get()
