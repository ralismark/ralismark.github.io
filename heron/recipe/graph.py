import dataclasses
import subprocess
from pathlib import Path, PurePosixPath

from .. import core
from ..jinja.registry import jinja_recipe_builder
from . import inout

FG_SUBST = "#fffff2"


@dataclasses.dataclass(frozen=True)
class GraphvizRecipe(inout.InoutRecipeBase):
    engine: str

    def svg_args(self) -> tuple[str, ...]:
        graph_opts: dict[str, str] = {
            "fontcolor": FG_SUBST,
            "color": FG_SUBST,
            "bgcolor": "none",
        }
        node_opts: dict[str, str] = {
            "fontcolor": FG_SUBST,
            "color": FG_SUBST,
        }
        edge_opts: dict[str, str] = {
            "fontcolor": FG_SUBST,
            "color": FG_SUBST,
        }
        return (
            *(f"-G{k}={v}" for k, v in graph_opts.items()),
            *(f"-N{k}={v}" for k, v in node_opts.items()),
            *(f"-E{k}={v}" for k, v in edge_opts.items()),
        )

    def cleanup_svg(self, svg: str) -> str:
        svg = svg.replace(FG_SUBST, "currentColor")
        svg = svg.replace("</svg>", """
            <style>:root { color-scheme: light dark; }</style>
            </svg>
        """)
        return svg

    def build_impl(self, ctx: core.BuildContext) -> inout.Inout:
        outfmt = self.opath.suffix.lstrip(".")
        if outfmt == "":
            raise ValueError(f"opath {self.opath} not valid")

        try:
            if outfmt == "svg":
                svg = subprocess.run(
                    [
                        "dot",
                        f"-K{self.engine}",
                        f"-T{outfmt}",
                        *self.svg_args(),
                        str(ctx.input(self.path)),
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout
                svg = self.cleanup_svg(svg)

                with ctx.output(self.opath).open("w") as f:
                    f.write(svg)
            else:
                subprocess.run(
                    [
                        "dot",
                        f"-K{self.engine}",
                        f"-T{outfmt}",
                        f"-o{ctx.output(self.opath)}",
                        str(ctx.input(self.path)),
                    ],
                    check=True,
                )
        except subprocess.CalledProcessError as e:
            print(e.stderr)
            raise

        return self.inout()

    @jinja_recipe_builder("graphviz")
    @staticmethod
    def jinja(
        path: str | PurePosixPath,
        out: str,
        layout: str = "dot",
        *,
        __file__: Path,
    ) -> "GraphvizRecipe":
        return GraphvizRecipe(
            path=__file__.parent / path,
            out=out,
            engine=layout,
        )
