import typing as t
import dataclasses
import re
import yaml


@dataclasses.dataclass
class Preamble:
    RE_YAML = re.compile(r"^---\n(.*?)^---\n", re.MULTILINE | re.DOTALL)

    content: str
    preamble: t.Optional[dict]
    line_offset: int

    def preamble_or(self, default):
        if self.preamble is None:
            return default
        return self.preamble

    @classmethod
    def parse(cls, content: str) -> t.Self:
        """
        Remove and parse the preamble of a document, if it has one.
        """
        if content.startswith("---\n"):
            # yaml frontmatter
            m = cls.RE_YAML.match(content)
            if not m:
                raise ValueError("Unterminated YAML preamble")
            preamble = yaml.safe_load(m.group(1))
            if not isinstance(preamble, dict):
                raise TypeError("YAML preamble is not an object")

            return cls(
                content=content[m.end() :],
                preamble=preamble,
                line_offset=content.count("\n", *m.span()),
            )
        else:
            return cls(
                content=content,
                preamble=None,
                line_offset=0,
            )
