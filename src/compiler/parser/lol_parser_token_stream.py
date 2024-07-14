from typing import List, Optional

from compiler.lexer.lol_lexer import LolToken


class TokenStream:
    """Semantics taken from CharacterStream"""

    def __init__(self, tokens: List[LolToken]) -> None:
        self.tokens = tokens
        self.position = 0

    def get_token(self, *, offset: int = 0) -> Optional[LolToken]:
        """
        Get the current token or return None if at the end.

        N.B. Does NOT advance the token!
        """
        if self.position + offset >= len(self.tokens):
            return None
        return self.tokens[self.position + offset]

    def next_token(self):
        """Advance to the next token."""
        t = self.get_token()
        if t is None:
            return
        self.position += 1
