from typing import List, Optional

from compiler.lexer.lol_lexer import Token


class TokenStream:
    """Semantics taken from CharacterStream"""

    def __init__(self, src: List[Token], text: str = None) -> None:
        self.text = text
        self.src = src
        self.idx = 0

    def get_text(self) -> str:
        return self.text

    def get_token(self, *, offset: int = 0) -> Optional[Token]:
        """
        Get the current token or return None if at the end.

        N.B. Does NOT advance the token!
        """
        if self.idx + offset >= len(self.src):
            return None
        return self.src[self.idx + offset]

    def next_token(self):
        """Advance to the next token."""
        t = self.get_token()
        if t is None:
            return
        self.idx += 1

    def get_pos(self):
        return self.idx
