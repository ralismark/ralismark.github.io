from .. import core
from pathlib import Path
import hashlib


@core.recipe()
def CopyCaRecipe(ctx: core.BuildContext, path: Path, prefix: str = "/ca/") -> core.Inout:
    with open(ctx.input(path), "rb") as f:
        # I control the inputs so this is fine
        digest = hashlib.file_digest(f, "md5").hexdigest()

    return ctx.build(core.CopyRecipe(f"{prefix}{digest}/{path.name}", path))
