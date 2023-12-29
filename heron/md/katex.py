import subprocess


def render_katex(
    content: str,
    display: bool = False,
) -> str:
    """
    Renders math using KaTeX.
    """

    # see <https://katex.org/docs/cli>

    args = [
        "katex",
        "--no-throw-on-error",
        "--trust",
    ]
    if display:
        args.append("--display-mode")

    # TODO spawning a process each time is kinda slow, is there a way to make it faster?
    proc = subprocess.run(
        args,
        check=True,
        text=True,
        input=content,
        capture_output=True,
    )
    return proc.stdout
