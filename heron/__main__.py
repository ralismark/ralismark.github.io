#!/usr/bin/env python3

import argparse
import logging
from pathlib import Path
import shutil

from . import core, dev

logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(
    prog="heron",
    description="Temmie's awful static site build system",
)
subparser = parser.add_subparsers(
    title="Available commands", required=True, metavar="<command>"
)


def register_func(p: argparse.ArgumentParser):
    return lambda func: p.set_defaults(func=func)


def load_recipe(recipe: tuple[Path, str]):
    path, name = recipe

    ns: dict = {
        "__file__": str(path),
        "__name__": "__heron_main__",  # intentionally not __main__ to allow scripts to keep working
    }
    with path.open("rb") as f:
        code = compile(f.read(), path, "exec")
        exec(code, ns)

    if name not in ns:
        raise KeyError(f"nothing named {name!r} in {path}")
    recipe = ns[name]
    if not isinstance(recipe, core.Recipe):
        raise TypeError(f"{name!r} is not a heron.core.Recipe")
    return recipe


def add_driver_args(parser: argparse.ArgumentParser):
    def parse_outdir(path: str) -> Path:
        p = Path(path)
        if not p.is_dir() if p.exists() else not p.parent.is_dir():
            raise ValueError(f"invalid directory name: {path}")
        return p

    parser.add_argument(
        "--out",
        "-o",
        metavar="DIR",
        help="Write output into DIR",
        type=parse_outdir,
        required=True,  # TODO pick a default at some point
    )

    parser.add_argument(
        "--rm",
        help="Clear output director before building",
        action="store_true",
    )

    def parse_recipe(path: str) -> tuple[Path, str]:
        name = "main"
        if ".py:" in path:
            path, name = path.rsplit(":", 1)
        return Path(path), name

    parser.add_argument(
        "recipe",
        type=parse_recipe,
    )


# -----------------------------------------------------------------------------


class LoggingDriver(core.Driver):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.cache: dict[core.Recipe, core.Manifest] = dict()

    def build(self, recipe):
        mf = self.cache.get(recipe)
        if mf is not None:
            return mf
        self.cache[recipe] = mf = super().build(recipe)

        for o in mf.filter(core.Manifest.Output):
            logger.info("wrote %s", o.path.relative_to(self.builddir))
        return mf


parser_build = subparser.add_parser("build", help="Build site")
add_driver_args(parser_build)


@register_func(parser_build)
def cmd_build(args: argparse.Namespace):
    if args.rm:
        shutil.rmtree(args.out)
    driver = LoggingDriver(args.out)
    print("building...", end="\r")
    driver.build(load_recipe(args.recipe))
    print("built successfully")


# -----------------------------------------------------------------------------

parser_dev = subparser.add_parser("dev", help="Dev")
add_driver_args(parser_dev)
parser_dev.add_argument(
    "--port", "-p",
    help="port to serve files on",
    type=int,
    default=80,
)


@register_func(parser_dev)
def cmd_dev(args: argparse.Namespace):
    if args.rm:
        shutil.rmtree(args.out)
    driver = dev.IncrementalDriver(args.out)

    def run_build():
        # print("\033c\033[3J", end="")
        print("building...", end="\r")
        try:
            driver.build(load_recipe(args.recipe))
        except core.BuildFailure as e:
            logger.exception("Failed to build %s", e.recipe, exc_info=e.__context__)
        except Exception:
            logger.exception("error")
        else:
            print("built successfully")
        driver.finish()

    run_build()

    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer
    import time

    class Handler(FileSystemEventHandler):
        def __init__(self):
            self.last_time = 0

        def on_any_event(self, event):
            if event.event_type == "opened":
                return
            if time.time() - self.last_time < 0.1:
                return
            if Path(event.src_path).is_relative_to(driver.builddir):
                return

            time.sleep(0.1)
            run_build()
            self.last_time = time.time()

    observer = Observer(0.1)
    observer.schedule(Handler(), path=args.recipe[0].parent, recursive=True)
    observer.start()

    try:
        dev.serve_http(args.out, port=args.port)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


# -----------------------------------------------------------------------------

args = parser.parse_args()

logging.basicConfig(
    format="%(asctime)s.%(msecs)03d [%(levelname)s] [%(name)s:%(lineno)d] %(message)s",
    datefmt="%Y%m%d:%H:%M:%S",
    level=logging.INFO,
)

args.func(args)
