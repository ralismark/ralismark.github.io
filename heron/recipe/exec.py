import typing as t
import dataclasses

from .. import core
from .basic import InputMixin

_R = t.TypeVar("_R")


@dataclasses.dataclass(frozen=True)
class Join(core.Recipe[_R]):
    """
    Monadic join, for processing recipes that produce a recipe.
    """

    recipe: core.Recipe[core.Recipe[_R]]

    def build_impl(self, ctx: core.BuildContext) -> _R:
        return ctx.build(ctx.build(self.recipe))


@dataclasses.dataclass(frozen=True)
class LoadRecipe(core.Recipe[core.Recipe], InputMixin):
    """
    Load a recipe from a file.

    Having this as a recipe, rather than handled outside the driver, allows
    us to leverage the caching/etc of driver implementations.
    """

    name: str = "main"

    def build_impl(self, ctx: core.BuildContext) -> core.Recipe:
        ns: dict = {
            "__file__": str(self.path),
            "__name__": "__heron_main__",  # intentionally not __main__ to allow scripts to keep working
        }
        with ctx.input(self.path).open("rb") as f:
            code = compile(f.read(), self.path, "exec")
            exec(code, ns)

        if self.name not in ns:
            raise KeyError(f"nothing named {self.name!r} in {self.path}")
        recipe = ns[self.name]
        if not isinstance(recipe, core.Recipe):
            raise TypeError(f"{self.name!r} is not a heron.core.Recipe")
        return recipe

    def join(self) -> core.Recipe:
        return Join(self)
