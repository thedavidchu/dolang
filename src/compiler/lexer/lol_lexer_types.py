from enum import Enum, auto, unique
from typing import Dict, Tuple, Union, Optional


@unique
class LolTokenType(Enum):
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
    EQUAL_EQUAL = auto()  # ==
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


# UNIMPLEMENTED_TOKEN_TYPES: set[LolTokenType] = {
#     # Unimplemented in tokenizer
#     EXCLAMATION,  # !
#     AT,  # @
#     PERCENT,  # %
#     CIRCUMFLEX,  # ^
#     AMPERSAND,  # &
#     QUESTION,  # ?
#     VBAR,  # |
#     # Doubled characters
#     RSHIFT,  # >>
#     LSHIFT,  # <<
#     GREATER_EQUAL,  # >=
#     LESSER_EQUAL,  # <=
#     EQUAL_EQUAL,  # ==
#     NOT_EQUAL,  # !=
#     # Unimplemented in tokenizer (no plan to implement these yet)
#     STAR_STAR,  # **
#     PLUS_PLUS,  # ++
#     MINUS_MINUS,  # --
#     SLASH_SLASH,  # //
#     # COLON_EQUAL = auto()                    # :=
#     # STAR_EQUAL = WONT_BE_IMPLEMENTED        # *=
#     # PLUS_EQUAL = WONT_BE_IMPLEMENTED        # +=
#     # MINUS_EQUAL = WONT_BE_IMPLEMENTED       # -=
#     # SLASH_EQUAL = WONT_BE_IMPLEMENTED       # /=
#     # RSHIFT_EQUAL = WONT_BE_IMPLEMENTED      # >>=
#     # LSHIFT_EQUAL = WONT_BE_IMPLEMENTED      # <<=
#     # PERCENT_EQUAL = WONT_BE_IMPLEMENTED     # %=
#     # CIRCUMFLEX_EQUAL = WONT_BE_IMPLEMENTED  # ^=
#     # AMPERSAND_EQUAL = WONT_BE_IMPLEMENTED   # &=
#     # QUESTION_EQUAL = WONT_BE_IMPLEMENTED    # ?=
#     # VBAR_EQUAL = WONT_BE_IMPLEMENTED        # |=
#     # AT_EQUAL = WONT_BE_IMPLEMENTED          # @=
#     # BSLASH = auto(), WONT_BE_IMPLEMENTED    # \
# }


SYMBOL_CONTROL: Dict[Optional[str], Union[Dict, LolTokenType]] = {
    "(": {None: LolTokenType.LPAREN},
    ")": {None: LolTokenType.RPAREN},
    "[": {None: LolTokenType.LSQB},
    "]": {None: LolTokenType.RSQB},
    "{": {None: LolTokenType.LBRACE},
    "}": {None: LolTokenType.RBRACE},
    ",": {None: LolTokenType.COMMA},
    ".": {None: LolTokenType.DOT},
    ";": {None: LolTokenType.SEMICOLON},
    "?": {None: LolTokenType.QUESTION},
    "|": {None: LolTokenType.VBAR},
    "&": {None: LolTokenType.AMPERSAND},
    "^": {None: LolTokenType.CIRCUMFLEX},
    "@": {None: LolTokenType.AT},
    ":": {
        ":": LolTokenType.COLON_COLON,
        None: LolTokenType.COLON,
    },
    "=": {
        "=": LolTokenType.EQUAL_EQUAL,
        None: LolTokenType.EQUAL,
    },
    ">": {
        ">": LolTokenType.RSHIFT,
        "=": LolTokenType.GREATER_EQUAL,
        None: LolTokenType.GREATER,
    },
    "<": {
        "<": LolTokenType.LSHIFT,
        "=": LolTokenType.LESSER_EQUAL,
        None: LolTokenType.LESSER,
    },
    "!": {
        "=": LolTokenType.NOT_EQUAL,
        None: LolTokenType.NOT,
    },
    "+": {
        "+": LolTokenType.PLUS_PLUS,
        None: LolTokenType.PLUS,
    },
    "*": {
        "*": LolTokenType.STAR_STAR,
        None: LolTokenType.STAR,
    },
    "-": {
        "-": LolTokenType.MINUS,
        ">": LolTokenType.ARROW,
        None: LolTokenType.MINUS,
    },
    "/": {
        "/": LolTokenType.SLASH_SLASH,
        None: LolTokenType.SLASH,
    },
}


class LolToken:
    def __init__(
        self,
        lexeme: str,
        token_type: LolTokenType,
        *,
        start_position: Optional[int] = None,
        full_text: Optional[str] = None,
    ):
        self.lexeme = lexeme
        self.token_type = token_type

        self.start_position = start_position
        self.full_text = full_text

    def is_type(self, token_type: LolTokenType) -> bool:
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
        return f"LolToken(lexeme={repr(self.lexeme)}, token_type={self.get_token_type_as_str()}, start_idx={self.start_position}, full_text?={isinstance(self.full_text, str)})"

    def get_line_and_column_numbers(self) -> Optional[Tuple[int, int]]:
        if self.start_position is None or self.full_text is None:
            return None
        line_no = self.full_text[: self.start_position].count("\n") + 1
        lines = self.full_text.split("\n")
        col_no = self.start_position - sum(
            len(line) for line in lines[:line_no]
        )
        return line_no, col_no

    def to_dict(self) -> Dict[str, Union[LolTokenType, int, str]]:
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

    def get_text_after(self):
        return self.text[self.idx :]

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

    def get_pos(self) -> int:
        """Get the current character position in a (absolute_index, line_number,
        column_number) tuple"""
        return self.idx
