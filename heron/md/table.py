import re

import mistune


class Table:
    NAME = "table"
    PATTERN = r"(?:\|.+(?:\n|$))+"

    SEPARATOR_RE = re.compile(r"\s*-+\s*")

    def token_from_group(
        self,
        rows: list[list[str]],
        kind: str,
    ):
        return {
            "type": f"{self.NAME}_group",
            "attrs": {
                "kind": kind,
            },
            "children": [
                {
                    "type": f"{self.NAME}_row",
                    "children": [
                        {
                            "type": f"{self.NAME}_cell",
                            "text": cell.strip(),
                            "attrs": {"kind": kind},
                        }
                        for cell in row
                    ],
                }
                for row in rows
            ],
        }

    def parse(
        self,
        block: mistune.BlockParser,
        m: re.Match,
        state: mistune.BlockState,
    ):
        table: list[list[list[str]]] = [[]]

        for row in m.group().split("\n"):
            if not row:
                continue
            row = row.strip().strip("|")
            cells = row.split("|")
            if all(self.SEPARATOR_RE.fullmatch(cell) for cell in cells):
                table.append([])
            else:
                table[-1].append(cells)

        # pad rows to full width
        table_width = max(len(row) for group in table for row in group)
        for group in table:
            for row in group:
                while len(row) < table_width:
                    row.append("")

        # extract header and footer
        thead: list[list[str]] = []
        tfoot: list[list[str]] = []

        if len(table) > 1:
            thead = table[0]
            table = table[1:]
        if len(table) > 1:
            tfoot = table[-1]
            table = table[:-1]

        children = []
        if thead:
            children.append(self.token_from_group(thead, "head"))
        for tbody in table:
            if tbody:
                children.append(self.token_from_group(tbody, "body"))
        if tfoot:
            children.append(self.token_from_group(tfoot, "foot"))

        state.append_token(
            {
                "type": self.NAME,
                "children": children,
            }
        )

        return m.end()

    def render_table(self, renderer: mistune.BaseRenderer, text: str) -> str:
        return f"<table>\n{text}</table>\n"

    def render_group(self, renderer: mistune.BaseRenderer, text: str, kind: str) -> str:
        return f"<t{kind}>\n{text}</t{kind}>\n"

    def render_row(self, renderer: mistune.BaseRenderer, text: str) -> str:
        return f"<tr>\n{text}</tr>\n"

    def render_cell(self, renderer: mistune.BaseRenderer, text: str, kind: str) -> str:
        tag = "th" if kind == "head" else "td"
        return f"<{tag}>{text}</{tag}>\n"

    def __call__(self, md: mistune.Markdown):
        md.block.register(self.NAME, self.PATTERN, self.parse, before="paragraph")

        if md.renderer and md.renderer.NAME == "html":
            md.renderer.register(f"{self.NAME}", self.render_table)
            md.renderer.register(f"{self.NAME}_group", self.render_group)
            md.renderer.register(f"{self.NAME}_row", self.render_row)
            md.renderer.register(f"{self.NAME}_cell", self.render_cell)
