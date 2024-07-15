from typing import List, Optional
from pathlib import Path

from compiler.lexer.lol_lexer import LolToken


class TokenStream:
    """Semantics taken from CharacterStream"""

    def __init__(self, path: Path, tokens: List[LolToken]) -> None:
        self.path = path
        self.tokens = tokens
        self.position = 0

    def get_token(self, *, offset: int = 0) -> Optional[LolToken]:
        """
        Get the current token or return None if at the end.

        N.B. Does NOT advance the token!
        """
        if self.position + offset not in range(len(self.tokens)):
            return None
        return self.tokens[self.position + offset]

    def next_token(self):
        """Advance to the next token."""
        t = self.get_token()
        if t is None:
            return
        self.position += 1
