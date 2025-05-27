#!/usr/bin/env python3

import http
import http.server
import shutil
import urllib.parse
from pathlib import Path, PurePosixPath

__all__ = [
    "HTTPRequestHandler",
    "http_serve",
]


class HTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    NOT_FOUND_MSG = "404 Not Found."

    MIME_FOR_SUFFIX = {
        ".htm": "text/html",
        ".html": "text/html",
        ".css": "text/css",
        ".js": "text/javascript",
        ".mjs": "text/javascript",
        ".svg": "image/svg+xml",
    }

    def __init__(self, *args, directory: Path, **kwargs):
        self.directory = directory
        super().__init__(*args, **kwargs)

    def do_GET(self):
        return self.do_response(True)

    def do_HEAD(self):
        return self.do_response(False)

    def log_request(self, code="-", size="-"):
        pass

    def do_response(self, send_content: bool):
        # figure out the file to use
        rel, trailing_slash = self.parse_path(self.path)
        if trailing_slash:
            path = self.directory / rel / "index.html"
            if path.is_file():
                self.send_response(http.HTTPStatus.OK)
                return self.sendfile(path, send_content)
        else:
            path = self.directory / rel
            if path.is_file():
                self.send_response(http.HTTPStatus.OK)
                return self.sendfile(path, send_content)
            path = path.with_name(path.name + ".html")
            if path.is_file():
                self.send_response(http.HTTPStatus.OK)
                return self.sendfile(path, send_content)

        # 404
        self.send_response(http.HTTPStatus.NOT_FOUND)

        fallback = self.directory / "404.html"
        if fallback.is_file():
            return self.sendfile(fallback, send_content)

        self.send_header("Content-Length", str(len(self.NOT_FOUND_MSG)))
        self.end_headers()
        self.wfile.write(self.NOT_FOUND_MSG.encode())

    def sendfile(self, path: Path, send_content: bool):
        self.send_header("Content-Length", str(path.stat().st_size))

        if mime := self.MIME_FOR_SUFFIX.get(path.suffix):
            self.send_header("Content-Type", mime)

        self.end_headers()

        if send_content:
            with path.open("rb") as f:
                shutil.copyfileobj(f, self.wfile)

    def parse_path(self, path: str) -> tuple[PurePosixPath, bool]:
        # abandon query parameters
        path = path.split("?", 1)[0]
        path = path.split("#", 1)[0]

        trailing_slash = path.rstrip().endswith("/")
        # unquote
        path = urllib.parse.unquote(path)

        # TODO this is insecure

        p = PurePosixPath(path)
        if p.is_absolute():
            p = p.relative_to(p.anchor)

        return p, trailing_slash


def http_serve(
    directory: Path,
    host: str = "",
    port: int = 0,
):
    with http.server.HTTPServer(
        (host, port),
        lambda *args, **kwargs: HTTPRequestHandler(
            *args, **kwargs, directory=directory
        ),
    ) as srv:
        actual_host, actual_port = srv.server_address
        print(f"Serving {directory} on {str(actual_host)}:{actual_port}")
        srv.serve_forever()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Serve files over HTTP",
    )
    parser.add_argument(
        "--port",
        "-p",
        help="specify alternate port",
        type=int,
        default=0,
    )
    parser.add_argument(
        "path",
        nargs="?",
        type=Path,
        default=Path.cwd(),
    )
    args = parser.parse_args()

    http_serve(args.path, port=args.port)
