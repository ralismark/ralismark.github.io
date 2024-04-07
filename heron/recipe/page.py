import dataclasses
import typing as t
from pathlib import Path, PurePosixPath

import jinja2
from frozendict import frozendict

from .. import core, util
from ..jinja.registry import RECIPE_FILTERS, jinja_recipe_builder
from . import inout


def main_file(ctx: core.BuildContext, path: Path) -> Path:
    path = ctx.input(path)
    if path.is_dir():
        # look for index
        candidates = list(path.glob("index.*"))
        if not candidates:
            raise RuntimeError(f"{path} does not contain index page")
        if len(candidates) > 1:
            raise RuntimeError(
                f"{path} has too many index pages: {[c.name for c in candidates]}"
            )
        path = ctx.input(candidates[0])

    return path


@dataclasses.dataclass(frozen=True)
class PageInout(inout.Inout):
    props: frozendict[str, t.Hashable]
    recipe_props: frozendict[str, t.Hashable]
    content: t.Optional[str]

    def __getitem__(self, name: str) -> t.Hashable:
        return self.recipe_props[name]


@dataclasses.dataclass(frozen=True)
class PageMetaRecipe(inout.InoutRecipeBase[PageInout]):
    props: frozendict[str, t.Hashable] = frozendict()

    def build_impl(self, ctx: core.BuildContext) -> PageInout:
        path = main_file(ctx, self.path)
        with path.open("rt") as f:
            content = f.read()

        # 1. preamble
        preamble = util.Preamble.parse(content)
        content = preamble.content
        props = preamble.preamble_or(dict())

        return PageInout(
            path=self.path,
            opath=self.opath,
            props=t.cast(frozendict, util.freeze(props)),
            recipe_props=self.props,
            content=None,
        )


@dataclasses.dataclass(frozen=True)
class JinjaStage(core.Recipe[str]):
    content: str
    filename: str
    jenv: jinja2.Environment
    vars: frozendict

    def build_impl(self, ctx: core.BuildContext) -> str:
        # manually instantiating using from_code allows us to specify the
        # filename
        return self.jenv.template_class.from_code(
            self.jenv,
            self.jenv.compile(
                self.content,
                name=self.filename,
                filename=self.filename,
            ),
            self.jenv.make_globals(None),
            None,
        ).render(self.vars)


@dataclasses.dataclass(frozen=True)
class JMarkdownStage(core.Recipe[str]):
    content: str
    filename: str
    jenv: jinja2.Environment

    def build_impl(self, ctx: core.BuildContext) -> str:
        from .. import md

        renderer = md.create_md(
            md.JinjaRenderer(
                lambda name: self.jenv.get_template(name),
                self.filename,
            )
        )
        return renderer(self.content)


@dataclasses.dataclass(frozen=True)
class PageRecipe(inout.InoutRecipeBase[PageInout]):
    jenv: jinja2.Environment
    ext: t.Optional[str] = None
    props: frozendict[str, t.Hashable] = frozendict()

    @property
    def meta(self) -> PageMetaRecipe:
        return PageMetaRecipe(
            path=self.path,
            out=self.opath,
            props=self.props,
        )

    def extend_props(self, **kwargs: t.Hashable):
        return dataclasses.replace(
            self,
            out=self.opath,
            props=frozendict(**self.props, **kwargs),
        )

    def build_impl(self, ctx: core.BuildContext) -> PageInout:
        path = main_file(ctx, self.path)
        with path.open("rt") as f:
            content = f.read()

        # 1. preamble
        preamble = util.Preamble.parse(content)
        content = preamble.content
        props = preamble.preamble_or(dict())

        # 2. jinja
        jinja_vars = frozendict(
            **self.props,
            page=frozendict(
                **dataclasses.asdict(super().inout()),
                props=frozendict(props),
            ),
        )

        content = ctx.build(
            JinjaStage(
                content="\n" * preamble.line_offset + content,  # fix up line numbers
                filename=str(path),
                jenv=self.jenv,
                vars=jinja_vars,
            )
        )

        # 3. render
        ext = self.ext or path.suffix.lstrip(".")
        if ext == "md":
            content = ctx.build(
                JMarkdownStage(
                    content=content,
                    filename=str(path),
                    jenv=self.jenv,
                )
            )
        elif ext == "html":
            pass  # don't need to do anything
        else:
            pass
            # warnings.warn_explicit(
            #     f"no processor for extension {ext!r}",
            #     UserWarning,
            #     str(path),
            #     0,
            # )

        pre_layout_content = content

        # 4. layout
        layout = props.get("layout")
        if layout:
            if not isinstance(layout, str):
                raise TypeError(f"expected str for layout prop but got {type(layout)}")

            layout_template = self.jenv.get_template(f"layout/{layout}.html")
            if layout_template.filename:
                ctx.input(Path(layout_template.filename))
            content = layout_template.render(
                jinja_vars,
                content=content,
            )

        with ctx.output(self.opath).open("wt") as f:
            f.write(content)

        return PageInout(
            path=self.path,
            opath=self.opath,
            props=t.cast(frozendict, util.freeze(props)),
            recipe_props=self.props,
            content=pre_layout_content,
        )

    @jinja_recipe_builder("page")
    @jinja2.pass_context
    @staticmethod
    def jinja(
        ctx: jinja2.runtime.Context,
        path: str | PurePosixPath,
        out: str,
        *,
        ext: str | None = None,
        props: t.Mapping[str, util.Freezable] = dict(),
        inherit: t.Iterable[str] = tuple(),
        __file__: Path,
    ) -> "PageRecipe":
        child_props = {**props, **{k: ctx[k] for k in inherit}}

        return PageRecipe(
            path=__file__.parent / path,
            out=out,
            jenv=ctx.environment,
            ext=ext,
            props=t.cast(t.Any, util.freeze(child_props)),
        )
