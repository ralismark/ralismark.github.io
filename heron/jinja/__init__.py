"""
Jinja templating.

In the context of heron, there are a few special variables that are always
available:

- `__file__: Path | None`, the path of the actual current
  file. This is not the top-level file being rendered, i.e.
  __file__ in an inherited template is the template that is
  being inherited from, rather than the template using it.

  This is useful for resolving relative paths.
"""

from .utils import pass_heron
from .environment import (
    Template,
    Environment,
    Loader,
    base_env,
)
