import typing as t


class TokenUnit(t.TypedDict):
    type: str
    attrs: t.NotRequired[dict[str, t.Any]]


class TokenRaw(TokenUnit):
    raw: str


class TokenChildren(TokenUnit):
    children: list["Token"]


Token = t.Union[TokenUnit, TokenRaw, TokenChildren]


class TokenChildrenB(TokenUnit):
    children: list["BlockToken"]


class TokenText(TokenUnit):
    text: str


BlockToken = t.Union[TokenChildren, TokenText]
