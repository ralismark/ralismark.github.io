import re

import mistune

from .utils import parse_nested_block
from .renderer import JinjaRenderer


class RSTDirective:
    NAME = "rst_directive"
    PATTERN = (
        r"\.\.\s+(?P<type>[a-zA-Z0-9_-]+)::[ \t]*(?P<title>[^\n]*)(?:\n|$)"
        r"(?P<options>(?:\t:[a-zA-Z0-9_-]+:[ \t]*[^\n]*(?:\n\t\t[^\n]*)*\n+)*)"
        r"\n*(?P<text>(?:\t[^\n]*\n+)*)"
    )

    def parse_options(self, text: str) -> list[tuple[str, str]]:
        opts: list[tuple[str, str]] = []
        for line in re.split(r"\n+", text):
            if not line.strip():
                continue
            line = line[2:]  # remove initial \t: or \t\t
            i = line.find(":")
            if i >= 0:
                opts.append((line[:i], line[i + 1 :].strip()))
            else:
                opts[-1] = (opts[-1][0], opts[-1][1] + "\n" + line)
        return opts

    def parse(
        self,
        block: mistune.BlockParser,
        m: re.Match,
        state: mistune.BlockState,
    ):
        content = "\n".join(line[1:] for line in m.group("text").splitlines())
        state.append_token(
            {
                "type": self.NAME,
                "children": parse_nested_block(block, content, state),
                "attrs": {
                    "directive": m.group("type"),
                    "title": m.group("title"),
                    "options": self.parse_options(m.group("options")),
                    "raw": content,
                },
            }
        )

        return m.end()

    def render_jinja(
        self,
        renderer: JinjaRenderer,
        text: str,
        *,
        directive: str,
        title: str,
        options: list[tuple[str, str]],
        raw: str,
    ) -> str:
        return renderer.load_template(f"layout/markdown/rst-{directive}.html").render(
            title=title,
            options=dict(options),
            content=text,
            content_raw=raw,
        )

    def __call__(self, md: mistune.Markdown):
        md.block.register(self.NAME, self.PATTERN, self.parse, before="paragraph")
        if isinstance(md.renderer, JinjaRenderer):
            md.renderer.register(self.NAME, self.render_jinja)
