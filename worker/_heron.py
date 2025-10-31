#!/usr/bin/env python3

import json
import subprocess
from pathlib import Path

import heron

here = Path(__file__).parent


@heron.FnRecipe
def main(ctx: heron.BuildContext) -> str:
    out = "_worker.js"
    opath = heron.canonicalise_opath(out)

    ctx.build(heron.CopyRecipe("/.assetsignore", here / "assetsignore"))

    args = [
        here / "../node_modules/.bin/esbuild",
        here / "./index.ts",
        f"--outfile={ctx.output(opath)}",
        # build for cf workers
        "--bundle",
        "--platform=neutral",
        "--format=esm",
        "--main-fields=module,main",
        # TODO using /dev/stdout like this is a bit cheeky, we probably wanna use a fifo or sth
        "--metafile=/dev/stdout",
    ]

    proc = subprocess.run(
        [str(x) for x in args if x],
        check=True,
        stdout=subprocess.PIPE,
    )
    meta = json.loads(proc.stdout)

    for input in meta["inputs"]:
        ctx.input(Path.cwd() / input)

    return heron.permalink(opath)


if __name__ == "__main__":
    drv = heron.Driver(Path.cwd())
    drv.build(main)
