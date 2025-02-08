import subprocess
import dataclasses

from .. import core


@dataclasses.dataclass(frozen=True)
class KatexRecipe(core.Recipe[str]):
    content: str
    display: bool

    def build_impl(self, ctx=None) -> str:
        # see <https://katex.org/docs/cli>
        args = [
            "katex",
            "--no-throw-on-error",
            "--trust",
        ]
        if self.display:
            args.append("--display-mode")

        # TODO spawning a process each time is kinda slow, is there a way to make it faster?
        proc = subprocess.run(
            args,
            check=True,
            text=True,
            input=self.content,
            capture_output=True,
        )
        return proc.stdout.strip()
