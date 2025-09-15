#!/usr/bin/env python3

import argparse
import logging
from pathlib import Path
import shutil
import http.server

import heron

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


parser_build = subparser.add_parser("build", help="Build site")
add_driver_args(parser_build)


@register_func(parser_build)
def cmd_build(args: argparse.Namespace):
    if args.rm:
        shutil.rmtree(args.out)
    driver = heron.CachingDriver(
        heron.LoggingDriver(
            heron.Driver(args.out),
            outputs=True,
        )
    )

    r = heron.FnRecipe(lambda ctx: ctx.build(ctx.build(heron.LoadRecipe(*args.recipe))))

    print("building...", end="\r")
    driver.build(r)
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
    driver = heron.GenerationalDriver(
        heron.LoggingDriver(
            heron.Driver(args.out),
            outputs=True,
            recipes="type",
        )
    )

    r = heron.FnRecipe(lambda ctx: ctx.build(ctx.build(heron.LoadRecipe(*args.recipe))))

    def run_build():
        successful = False
        # print("\033c\033[3J", end="")
        print("building...", end="\r")
        try:
            driver.build(r)
        except heron.BuildFailure as e:
            logger.exception("Failed to build %s", e.recipe, exc_info=e.__context__)
        except Exception:
            logger.exception("error")
        else:
            successful = True
            print("built successfully")
        driver.finish(flush=successful)

    run_build()

    class DevRequestHandler(heron.HTTPRequestHandler):
        def __init__(self, *args, driver: heron.GenerationalDriver, **kwargs):
            self.driver = driver
            super().__init__(*args, **kwargs)

        def do_response(self, send_content: bool):
            if not self.path.startswith("/$"):
                super().do_response(send_content)
                return

            if self.path == "/$":
                self.send_response(http.HTTPStatus.OK)
                self.send_header("Content-Type", "text/html")
                self.end_headers()

                for part in self.gen_index():
                    self.wfile.write(part.encode())
            else:
                self.send_response(http.HTTPStatus.NOT_FOUND)
                self.end_headers()
                self.wfile.write("Not a valid debug endpoint".encode())

        def gen_index(self):
            yield f"""<!doctype html>
                <head>
                <style>
                .summary {{ background: lightgrey; }}
                .summary:target {{ background: skyblue; }}
                .manifest {{ margin: 0 2rem; }}
                </style>
                <body>

                <h1>Heron</h1>

                <a href="#{hash(r)}">Root Recipe</a>

                <hr>
            """

            def rcp_name(rcp: heron.Recipe):
                name = type(rcp).__name__
                if isinstance(rcp, heron.InputMixin):
                    name += f' from <tt>{rcp.path}</tt>'
                if isinstance(rcp, heron.OutputMixin):
                    name += f' to <tt>{rcp.opath}</tt>'
                return name

            for rcp, mf in self.driver.cache.items():
                yield f"""
                <div class="summary" id="{hash(rcp)}">
                    <a href="#{hash(rcp)}">{rcp_name(rcp)}</a>
                </div>
                <div class="manifest">
                    """
                if isinstance(rcp, heron.OutputMixin):
                    live_path = str(rcp.opath)
                    if live_path.endswith(".html"):
                        live_path = live_path[:-5]
                    if live_path.endswith("index"):
                        live_path = live_path[:-5]
                    yield f'&rarr; <a href="/{live_path}">{live_path}</a><br>'
                yield """
                    <table>
                    <tbody>
                """

                for log in mf.log:
                    yield f"\n<tr><tr><td>{type(log).__name__}</td><td>"
                    if isinstance(log, heron.Manifest.Input):
                        yield f"<tt>{log.path}</tt>"
                    elif isinstance(log, heron.Manifest.Output):
                        yield f"<tt>{log.path}</tt>"
                    elif isinstance(log, heron.Manifest.SubRecipe):
                        yield f'''
                            <a href="#{hash(log.recipe)}">{rcp_name(log.recipe)}</a>
                        '''
                    elif isinstance(log, heron.Manifest.Trace):
                        yield f"{log.data}"
                    else:
                        yield "?"

                yield """
                    </table>
                </div>
                """

    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer
    import time

    observe_base = Path.cwd()

    class Handler(FileSystemEventHandler):
        def __init__(self):
            self.last_time = 0

        def on_any_event(self, event):
            if event.event_type in ("opened", "closed", "closed_no_write"):
                return
            if time.time() - self.last_time < 0.1:
                return
            path = Path(event.src_path)
            rel = path.relative_to(observe_base)
            if path.is_relative_to(driver.builddir):
                return
            if any(part.startswith(".") for part in rel.parts):
                return

            time.sleep(0.1)
            run_build()
            self.last_time = time.time()

    observer = Observer(timeout=0.1)
    observer.schedule(Handler(), path=str(observe_base), recursive=True)
    observer.start()

    try:
        directory = args.out
        with http.server.HTTPServer(
            ("", args.port),
            lambda *args, **kwargs: DevRequestHandler(*args, **kwargs, directory=directory, driver=driver),
        ) as srv:
            actual_host, actual_port = srv.server_address
            print(f"Serving {directory} on {actual_host}:{actual_port}")
            srv.serve_forever()
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
