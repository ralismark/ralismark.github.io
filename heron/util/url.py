"""
Path handling utilities.

There's two kinds of strings being passed around.

1.  An _output path_ is a relative path that describes the file that is written
    to by a recipe. Recipes pass these to the driver, which hands back the
    absolute path to write.

2.  A _permalink_ is the link used to visit a page. This can be obtained from the output path by:

    1. If the filename is "index.html", removing that but keeping a trailing slash.
    2. Removing ".html" extensions.
    3. Adding in the baseurl if relevant.
"""

import typing as t
import os
from pathlib import PurePosixPath

Pathish = t.Union[str, os.PathLike[str]]


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
