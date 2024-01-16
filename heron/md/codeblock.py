import typing as t
import warnings

import mistune
import pygments
import pygments.lexer
import pygments.lexers
import pygments.token as tok
import pygments.util
import pygments.formatters.html

Ignore = tok.Token.Ignore


class EscapeLexer(pygments.lexer.RegexLexer):
    name = "Escape"
    aliases = ["escape"]
    filenames: list[str] = []

    tokens = {
        "root": [
            (r"(<!)(.*?)(!>)", pygments.lexer.bygroups(Ignore, tok.Escape, Ignore)),
            (r"<!", tok.Error),
            (r".", tok.Other),
        ],
    }


class Formatter(pygments.formatter.Formatter):
    def _ttype_class(self, ttype: t.Optional[tok.Token]):
        while ttype is not None:
            shortname = tok.STANDARD_TYPES.get(ttype)
            if shortname:
                yield shortname
            ttype = ttype.parent

    def format(self, tokensource, outfile):
        for ttype, value in tokensource:
            if ttype == Ignore:
                continue
            elif ttype == tok.Escape:
                outfile.write(value)
            else:
                classes = " ".join(self._ttype_class(ttype))
                if not classes:
                    outfile.write(mistune.escape(value))
                else:
                    outfile.write(f'<span class="{classes}">{mistune.escape(value)}</span>')


_plaintext_lexer = pygments.lexers.get_lexer_by_name("text")


def render_block_code(
    text: str,
    info: t.Optional[str] = None,
    location: tuple[str, int] = ("<source>", 0),
) -> str:
    if not info:
        info = ""

    def get_lexer(info: str):
        info = info.strip()
        if info == "":
            return _plaintext_lexer
        if info.startswith("escape"):
            info = info[len("escape") :]
            return pygments.lexer.DelegatingLexer(
                lambda: get_lexer(info),
                EscapeLexer,
            )
        try:
            return pygments.lexers.get_lexer_by_name(info)
        except pygments.util.ClassNotFound:
            warnings.warn_explicit(
                f"no lexer with name {info!r}",
                UserWarning,
                location[0],
                location[1],
            )
            return _plaintext_lexer

    content = None

    content = pygments.highlight(
        text,
        get_lexer(info),
        Formatter(),
    )

    return f'<pre data-lang="{mistune.escape(info)}"><code>{content}</code></pre>\n'
