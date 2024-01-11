"""
Subclasses of jinja types to alter their behaviour.
"""

import typing as t
from pathlib import Path
import os
import warnings
import datetime as dt

import jinja2

from .. import core, util
from .recipes import RECIPE_FILTERS
from .utils import GetItemWrapper


class Template(jinja2.Template):
    """
    Template subclass to provide __file__ to the template.
    """

    __root_render_fn: t.Callable[[jinja2.runtime.Context], t.Iterator[str]]

    def mark_as_input(self):
        """
        Mark this template as an input to the current BuildContext.
        """
        ctx = core.BuildContext.Current.get(None)
        if ctx is not None:
            if self.filename is not None:
                ctx.input(Path(self.filename))
        else:
            warnings.warn("template rendered outside of build context")

    def alt_root_render_func(self, context: jinja2.runtime.Context):
        self.mark_as_input()

        assert self.filename is not None
        context.vars["__file__"] = Path(self.filename)
        yield from self.__root_render_fn(context)

    @property
    def root_render_func(self):
        return self.alt_root_render_func

    @root_render_func.setter
    def root_render_func(self, value):
        self.__root_render_fn = value

    def _get_default_module(
        self, ctx: t.Optional[jinja2.runtime.Context] = None
    ) -> jinja2.environment.TemplateModule:
        self.mark_as_input()
        return super()._get_default_module(ctx)

    async def _get_default_module_async(
        self, ctx: t.Optional[jinja2.runtime.Context] = None
    ) -> jinja2.environment.TemplateModule:
        self.mark_as_input()
        return await super()._get_default_module_async(ctx)


class Loader(jinja2.BaseLoader):
    # TODO have loader try diff file extensions as appropriate?

    def __init__(self, path: Path):
        self.path = path

    def get_source(self, environment: jinja2.Environment, template: str):
        path = self.path / template
        if not path.exists():
            raise jinja2.TemplateNotFound(template)
        mtime = path.stat().st_mtime
        with path.open() as f:
            return f.read(), str(path), lambda: mtime == path.stat().st_mtime


class Environment(jinja2.Environment):
    template_class = Template

    def join_path(self, template: str, parent: str) -> str:
        return os.path.normpath(os.path.join(os.path.dirname(parent), template))


# -----------------------------------------------------------------------------

base_env = Environment(
    autoescape=False,
    extensions=[
        "jinja2.ext.do",
        "jinja2.ext.loopcontrols",
        "jinja2.ext.debug",
    ],
)
base_env.globals["dt"] = dt
base_env.filters["repr"] = repr
base_env.tests["recipe"] = lambda v: isinstance(v, core.Recipe)


base_env.globals["recipe"] = GetItemWrapper(RECIPE_FILTERS)
for k, v in RECIPE_FILTERS.items():
    base_env.filters[f"recipe.{k}"] = v


@util.setitem(base_env.globals, "raise")
def jinja_raise(msg: str) -> str:
    raise Exception(msg)


@util.setitem(base_env.filters, "markdownify")
@jinja2.pass_context
def markdownify(ctx: jinja2.runtime.Context, content: str) -> str:
    from .. import md

    render = md.create_md(
        md.JinjaRenderer(
            lambda name: ctx.environment.get_template(
                name,
            )
        ),
    )
    return render(content)
