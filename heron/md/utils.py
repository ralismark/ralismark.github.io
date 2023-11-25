import mistune


def parse_nested_block(
    block: mistune.BlockParser,
    text: str,
    state: mistune.BlockState,
):
    child = state.child_state(text)
    block.parse(child, block.rules)
    return child.tokens
