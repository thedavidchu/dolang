from enum import Enum, auto, unique
from typing import Dict, Tuple, Union, Optional


@unique
class TokenType(Enum):
    # Just for error checking!
    IMPLEMENTED = auto()
    NOT_YET_IMPLEMENTED = auto()
    WONT_BE_IMPLEMENTED = auto()

    # Parentheses, square brackets, and braces
    LPAREN = auto()  # (
    RPAREN = auto()  # )
    LSQB = auto()  # [
    RSQB = auto()  # ]
    LBRACE = auto()  # {
    RBRACE = auto()  # }

    # Separators
    DOT = auto()  # .
    COMMA = auto()  # ,
    EQUAL = auto()  # =
    COLON = auto()  # :
    SEMICOLON = auto()  # ;

    ARROW = auto()  # ->

    # Unimplemented in tokenizer
    EXCLAMATION = auto(), NOT_YET_IMPLEMENTED  # !
    AT = auto(), NOT_YET_IMPLEMENTED  # @
    PERCENT = auto(), NOT_YET_IMPLEMENTED  # %
    CIRCUMFLEX = auto(), NOT_YET_IMPLEMENTED  # ^
    AMPERSAND = auto(), NOT_YET_IMPLEMENTED  # &
    STAR = auto()  # *
    PLUS = auto()  # +
    MINUS = auto()  # -
    SLASH = auto()  # /

    QUESTION = auto(), NOT_YET_IMPLEMENTED  # ?
    VBAR = auto(), NOT_YET_IMPLEMENTED  # |

    GREATER = auto()  # >
    LESSER = auto()  # <

    # Doubled characters
    COLON_COLON = auto()  # ::
    RSHIFT = auto(), NOT_YET_IMPLEMENTED  # >>
    LSHIFT = auto(), NOT_YET_IMPLEMENTED  # <<
    GREATER_EQUAL = auto(), NOT_YET_IMPLEMENTED  # >=
    LESSER_EQUAL = auto(), NOT_YET_IMPLEMENTED  # <=
    EQUAL_EQUAL = auto(), NOT_YET_IMPLEMENTED  # ==
    NOT_EQUAL = auto(), NOT_YET_IMPLEMENTED  # !=

    # Unimplemented in tokenizer (no plan to implement these yet)
    STAR_STAR = auto(), WONT_BE_IMPLEMENTED  # **
    PLUS_PLUS = auto(), WONT_BE_IMPLEMENTED  # ++
    MINUS_MINUS = auto(), WONT_BE_IMPLEMENTED  # --
    SLASH_SLASH = auto(), WONT_BE_IMPLEMENTED  # //

    # COLON_EQUAL = auto()                    # :=
    # STAR_EQUAL = WONT_BE_IMPLEMENTED        # *=
    # PLUS_EQUAL = WONT_BE_IMPLEMENTED        # +=
    # MINUS_EQUAL = WONT_BE_IMPLEMENTED       # -=
    # SLASH_EQUAL = WONT_BE_IMPLEMENTED       # /=
    # RSHIFT_EQUAL = WONT_BE_IMPLEMENTED      # >>=
    # LSHIFT_EQUAL = WONT_BE_IMPLEMENTED      # <<=
    # PERCENT_EQUAL = WONT_BE_IMPLEMENTED     # %=
    # CIRCUMFLEX_EQUAL = WONT_BE_IMPLEMENTED  # ^=
    # AMPERSAND_EQUAL = WONT_BE_IMPLEMENTED   # &=
    # QUESTION_EQUAL = WONT_BE_IMPLEMENTED    # ?=
    # VBAR_EQUAL = WONT_BE_IMPLEMENTED        # |=
    # AT_EQUAL = WONT_BE_IMPLEMENTED          # @=
    # BSLASH = auto(), WONT_BE_IMPLEMENTED    # \


    # Multicharacter conglomerates
    IDENTIFIER = auto()  # [A-Za-z_][A-Za-z_0-9]
    STRING = auto()  # "[^"\n]*"
    INTEGER = auto()  # [1-9][0-9]*
    FLOAT = auto()
    COMMENT = auto()  # [/][*].*[*][/]

    # Keywords
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    FUNCTION = auto()
    RETURN = auto()
    LET = auto()
    NAMESPACE = auto()
    MODULE = auto()
    IMPORT = auto()
    BREAK = auto()
    CONTINUE = auto()
    AND = auto()
    OR = auto()
    NOT = auto()


SYMBOL_CONTROL: Dict[Optional[str], Union[Dict, TokenType]] = {
    "(": {None: TokenType.LPAREN},
    ")": {None: TokenType.RPAREN},
    "[": {None: TokenType.LSQB},
    "]": {None: TokenType.RSQB},
    "{": {None: TokenType.LBRACE},
    "}": {None: TokenType.RBRACE},
    ",": {None: TokenType.COMMA},
    ".": {None: TokenType.DOT},
    ";": {None: TokenType.SEMICOLON},
    "?": {None: TokenType.QUESTION},
    "|": {None: TokenType.QUESTION},
    "&": {None: TokenType.AMPERSAND},
    "^": {None: TokenType.CIRCUMFLEX},
    "@": {None: TokenType.AT},
    ":": {
        ":": TokenType.COLON_COLON,
        None: TokenType.COLON,
    },
    "=": {
        "=": TokenType.EQUAL_EQUAL,
        None: TokenType.EQUAL,
    },
    ">": {
        ">": TokenType.RSHIFT,
        "=": TokenType.GREATER_EQUAL,
        None: TokenType.GREATER,
    },
    "<": {
        "<": TokenType.LSHIFT,
        "=": TokenType.LESSER_EQUAL,
        None: TokenType.LESSER,
    },
    "!": {
        "=": TokenType.NOT_EQUAL,
        None: TokenType.NOT,
    },
    "+": {
        "+": TokenType.PLUS_PLUS,
        None: TokenType.PLUS,
    },
    "*": {
        "*": TokenType.STAR_STAR,
        None: TokenType.STAR,
    },
    "-": {
        "-": TokenType.MINUS,
        ">": TokenType.ARROW,
        None: TokenType.MINUS,
    },
    "/": {
        "/": TokenType.SLASH_SLASH,
        None: TokenType.SLASH,
    },
}


class Token:
    def __init__(
        self,
        lexeme: str,
        token_type: TokenType,
        *,
        start_position: Optional[int] = None,
        full_text: Optional[str] = None,
    ):
        self.lexeme = lexeme
        self.token_type = token_type

        self.start_position = start_position
        self.full_text = full_text

    def is_type(self, token_type: TokenType) -> bool:
        return self.token_type == token_type

    def as_str(self):
        return self.lexeme

    def get_token_type(self):
        return self.token_type

    def get_token_type_as_str(self):
        return self.token_type.name

    def __repr__(self):
        """Pretty print the token. This is NOT for serialization, because the
        token type should be an integer id so that it's easier to parse."""
        return (
            f"Token(lexeme={repr(self.lexeme)}, token_type={self.get_token_type_as_str()}, start_idx={self.start_position}, full_text?={isinstance(self.full_text, str)})"
        )

    def get_line_and_column_numbers(self) -> Optional[Tuple[int, int]]:
        if self.start_position is None or self.full_text is None:
            return None
        line_no = self.full_text[:self.start_position].count("\n") + 1
        lines = self.full_text.split("\n")
        col_no = self.start_position - sum(len(line) for line in lines[:line_no])
        return line_no, col_no

    def to_dict(self) -> Dict[str, Union[TokenType, int, str]]:
        """
        Pretty print the serialized token.

        To make this purely functional, we would print the token type ID,
        the start position, and the lexeme. Everything else is superfluous."""
        return dict(
            metatype=self.__class__.__name__,
            lexeme=repr(self.lexeme),
            token_type=self.get_token_type_as_str(),
            start_position=self.start_position,
        )


class CharacterStream:
    def __init__(self, text: str):
        self.text = text
        self.idx = 0
        self.line_number = 1
        self.column_number = 1

    def get_text_after(self):
        return self.text[self.idx:]

    def get_text(self) -> str:
        return self.text

    def get_char(self, *, offset: Optional[int] = 0) -> Optional[str]:
        """Get the current character or return None"""
        if self.idx + offset >= len(self.text):
            return None
        return self.text[self.idx + offset]

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

    def get_pos(self) -> int:
        """Get the current character position in a (absolute_index, line_number,
        column_number) tuple"""
        return self.idx
