from typing import Dict, Tuple, Union
from enum import Enum, auto, unique


@unique
class TokenType(Enum):
    LPAREN = auto()  # (
    RPAREN = auto()  # )
    LSQB = auto()  # [
    RSQB = auto()  # ]
    LBRACE = auto()  # {
    RBRACE = auto()  # }

    DOT = auto()  # .
    COMMA = auto()  # ,
    EQUAL = auto()  # =
    COLON = auto()  # :
    SEMICOLON = auto()  # ;

    ARROW = auto()  # ->

    # Unimplemented in tokenizer
    COLON_COLON = auto()  # ::
    EXCLAMATION = auto()  # !
    AT = auto()  # @
    PERCENT = auto()  # %
    CIRCUMFLEX = auto()  # ^
    AMPERSAND = auto()  # &
    STAR = auto()  # *
    PLUS = auto()  # +
    MINUS = auto()  # -
    SLASH = auto()  # /

    RSHIFT = auto()  # >>
    LSHIFT = auto()  # <<
    QUESTION = auto()  # ?
    VBAR = auto()  # |
    BSLASH = auto()  # \

    EQUAL_EQUAL = auto()  # ==
    NOT_EQUAL = auto()  # !=
    GREATER = auto()  # >
    LESSER = auto()  # <
    GREATER_EQUAL = auto()  # >=
    LESSER_EQUAL = auto()  # <=

    # Unimplemented in tokenizer (no plan to implement these yet)
    STAR_STAR = auto()  # **
    PLUS_PLUS = auto()  # ++
    MINUS_MINUS = auto()  # --
    SLASH_SLASH = auto()  # //

    # DEPRECATED
    NEWLINE = auto()  # \n

    # Multicharacter conglomerates
    IDENTIFIER = auto()  # [A-Za-z_][A-Za-z_0-9]
    STRING = auto()  # "[^"\n]*"
    DEC = auto()  # [1-9][0-9]*
    COMMENT = auto()  # #.*

    # Keywords
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FUNCTION = auto()
    RETURN = auto()
    LET = auto()
    NAMESPACE = auto()
    MODULE = auto()
    IMPORT = auto()
    PRINT = auto()


class Token:
    def __init__(
        self,
        idx: int,
        line_number: int,
        column_number: int,
        token_type: TokenType,
        lexeme: str,
    ):
        self.idx = idx
        self.line_number = line_number
        self.column_number = column_number
        self.token_type = token_type
        self.lexeme = lexeme

    def type(self):
        return self.token_type

    def type_name(self):
        return self.token_type.name

    def __str__(self):
        """Serialize the token."""
        return f"{self.idx},{self.line_number},{self.column_number},{self.token_type.value},{self.lexeme}"

    def __repr__(self):
        """Pretty print the token. This is NOT for serialization, because the
        token type should be an integer id so that it's easier to parse."""
        return f"{self.idx},{self.line_number},{self.column_number},{self.token_type},{self.lexeme}"

    def to_dict(self) -> Dict[str, Union[TokenType, int, str]]:
        return dict(
            TokenType=self.token_type.name,
            StartPosition=self.idx,
            LineNumber=self.line_number,
            ColumnNumber=self.column_number,
            LexemeLength=len(self.lexeme),
            Lexeme=self.lexeme,
        )


class CharacterStream:
    def __init__(self, text: str):
        self.text = text
        self.idx = 0
        self.line_number = 1
        self.column_number = 1

    def get_text(self) -> str:
        return self.text

    def get_char(self) -> str:
        """Get the current character or return None"""
        if self.idx >= len(self.text):
            return None
        return self.text[self.idx]

    def next_char(self):
        """Advance to the next character or return early if we are at the last character."""
        c = self.get_char()
        if c is None:
            return
        self.idx += 1
        if c == "\n":
            self.line_number += 1
            self.column_number = 1
        else:
            self.column_number += 1

    def get_pos(self) -> Tuple[int, int, int]:
        """Get the current character position in a (absolute_index, line_number,
        column_number) tuple"""
        return (self.idx, self.line_number, self.column_number)
