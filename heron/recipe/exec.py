import typing as t
import dataclasses

from .. import core
from .basic import InputMixin

_F = t.TypeVar("_F")


@dataclasses.dataclass(frozen=True)
class LoadRecipe(core.Recipe[_F], InputMixin):
    """
    Load a recipe from a file.

    Having this as a recipe, rather than handled outside the driver, allows
    us to leverage the caching/etc of driver implementations.
    """

    name: str = "main"

    def build_impl(self, ctx: core.BuildContext) -> _F:
        ns: dict = {
            "__file__": str(self.path),
            "__name__": "__heron_main__",  # intentionally not __main__ to allow scripts to keep working
        }
        with ctx.input(self.path).open("rb") as f:
            code = compile(f.read(), self.path, "exec")
            exec(code, ns)

        if self.name not in ns:
            raise KeyError(f"nothing named {self.name!r} in {self.path}")
        return ns[self.name]
