from .renderer import JinjaRenderer


def create_md(renderer):
    import mistune

    from .rst_directive import RSTDirective
    from .table import Table

    # HACK make foootnotes support tab indent
    mistune.plugins.footnotes.REF_FOOTNOTE = (
        r'^(?P<footnote_lead> {0,3})'
        r'\[\^(?P<footnote_key>' + mistune.helpers.LINK_LABEL + r')]:[ \t]?'
        r'(?P<footnote_text>[^\n]*(?:\n+|$)'
        r'(?:(?P=footnote_lead)[ \t]+[^\n]*\n+)*'
        r')'
    )

    return mistune.Markdown(
        renderer=renderer,
        plugins=[
            mistune.plugins.formatting.strikethrough,
            mistune.plugins.footnotes.footnotes,
            mistune.plugins.table.table,
            mistune.plugins.math.math,
            RSTDirective(),
            Table()
        ],
    )
