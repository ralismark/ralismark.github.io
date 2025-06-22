#!/usr/bin/env python3

import json
import subprocess
from pathlib import Path

import heron

here = Path(__file__).parent


@heron.recipe()
def main(ctx: heron.BuildContext, out: str) -> str:
    opath = heron.canonicalise_opath(out)

    proc = subprocess.run(
        [
            here / "../node_modules/.bin/esbuild",
            here / "./index.tsx",
            f"--outfile={ctx.output(opath)}",
            "--bundle",
            # TODO using /dev/stdout like this is a bit cheeky, we probably wanna use a fifo or sth
            "--metafile=/dev/stdout",
            "--loader:.css=text",
        ],
        check=True,
        stdout=subprocess.PIPE,
    )
    meta = json.loads(proc.stdout)

    for input in meta["inputs"]:
        ctx.input(Path.cwd() / input)

    return heron.permalink(opath)


if __name__ == "__main__":
    drv = heron.Driver(Path.cwd())
    drv.build(main(out="visual-feedback.js"))
