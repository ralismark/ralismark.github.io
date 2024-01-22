import typing as t
import re
import warnings

import jinja2
import mistune
import mistune.plugins.formatting
import mistune.plugins.footnotes
import mistune.plugins.table
import mistune.plugins.math

from .codeblock import render_block_code
from .katex import KatexRecipe
from .. import core


def basic_generate_id(text: str) -> str:
    """
    Basic conversion of header name to an ID, without special handling of
    empty/unique IDs.

    See <https://github.com/gettalong/kramdown/blob/bd678ecb59f70778fdb3b08bdcd39e2ab7379b45/lib/kramdown/converter/base.rb#L237>.
    """
    text = re.sub(r"[^a-zA-Z0-9 -]", "", text)
    text = re.sub(r" ", "-", text)
    text = text.lower()
    return text


class JinjaRenderer(mistune.renderers.html.HTMLRenderer):
    def __init__(
        self,
        load_template: t.Callable[[str], jinja2.Template],
        filename: str = "<string>",
    ):
        super().__init__(escape=False)
        self.load_template = load_template
        self.filename = filename

    def text(self, text: str) -> str:
        text = (
            text.replace("---", "&mdash;")
            .replace("--", "&ndash;")
            .replace("...", "&hellip;")
        )
        return super().text(text)

    def heading(self, text: str, level: int, **attrs) -> str:
        # deepen headers
        level = min(6, level + 1)

        heading_id = attrs.get("id")
        if not heading_id:
            heading_id = basic_generate_id(text)
        return f'<h{level} id="{heading_id}"><a href="#{heading_id}">{text}</a></h{level}>\n'

    def block_code(self, text: str, info=None) -> str:
        # TODO rip no line numbers
        return render_block_code(text, info=info, location=(self.filename, 0))

    def block_math(self, text: str) -> str:
        r = KatexRecipe(text, True)
        return core.current_ctx().build(r)

    def inline_math(self, text: str) -> str:
        r = KatexRecipe(text, False)
        return core.current_ctx().build(r)

    def image(self, alt: str, url: str, title: t.Optional[str] = None) -> str:
        warnings.warn_explicit(
            "use of raw image tags are deprecated; use `.. figure::` instead",
            DeprecationWarning,
            self.filename,
            0,
        )
        return self.load_template("layout/markdown/img.html").render(
            alt=alt,
            url=url,
            title=title,
        )
