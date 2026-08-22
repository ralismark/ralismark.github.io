import dataclasses
import requests

from .. import core


@core.recipe()
def FetchRecipe(
    ctx: core.BuildContext,
    url: str,
) -> bytes:
    r = requests.get(url, timeout=5)
    r.raise_for_status()
    return r.content
