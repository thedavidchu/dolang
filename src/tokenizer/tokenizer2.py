"""
Tokenizer
=========

Definitions
-----------

Let '\n' denote the newline character. To denote the literal string of a single
backslash followed by an 'n', we will use: '\\n'.  

Limitations
-----------

### Whitespace
* Indentation is not stored by the tokenizer (yet). The tokenizer may store
information about indentation, but it shall not store information about any
other whitespace (unless we add the ability to add arbitrary operators).

### Comments
* '#' ends with either '\n' or EOF
* '//' ends with either '\n' or EOF
* '/*' ends with '*/'.
    * It does not nest yet.

### Strings
* Strings begin and end with '"'. A '\n' (not literal) or EOF before termination
is an error.
    * Variables may be inserted into strings with braces, but not yet.
    * Raw strings (e.g. Python's r"") are not added yet.
    * Multiline strings are not supported yet (e.g. Python's """ """)
    * Nesting strings are not supported yet (e.g. 
    """ "" """Inner string: "Inner Inner String" """ """"")

### Literals
* 
"""


import argparse
from enum import Enum
from typing import List, Tuple
from typing_extensions import Self


EOF: str = None


class TokenType(str, Enum):
    WHITESPACE = "WHITESPACE"  # Indent vs non-indent
    COMMENT = "COMMENT"  # Multi-line vs non-multiline, nesting
    STRING = "STRING"  # Multi-quotes, single-vs-double quote
    LITERAL = "LITERAL"  # Keyword, non-keyword
    NUMBER = "NUMBER"  # Float, int, complex
    PUNCTUATION = "PUNCTUATION"  # Stand-alone, non-standalone


class Position:
    def __init__(self, idx: int, line: int, col: int):
        # Note: this should be immutable
        self._idx: int = idx
        self._line: int = line
        self._col: int = col

    def __repr__(self) -> str:
        return f"idx: {self._idx}, line: {self._line}, col: {self._col}"

    def new_line(self) -> Self:  # Assuming "Self" refers to its own type
        return Position(idx=self._idx + 1, line=self._line + 1, col=0)

    def new_col(self) -> Self:  # Assuming "Self" refers to its own type
        return Position(idx=self._idx + 1, line=self._line, col=self._col + 1)


class Text:
    def __init__(self, text: str):
        self.text: str = text
        self.position: Position = Position(0, 1, 0)

    def __next__(self) -> str:
        c: str = self.text[self.position._idx]
        if c == "\n":
            self.position = self.position.new_line()
        else:
            self.position = self.position.new_col()
        return self.text[self.position._idx]

    def getoffset(self, idx: int) -> str:
        if len(self.text) > self.position._idx + idx:
            return self.text[self.position._idx : self.position._idx + idx]
        else:
            return EOF

    def getpos(self) -> Position:
        return self.position


class Token:
    def __init__(
        self,
        strtoken: str,
        ttype: TokenType,
        startpos: Position,
        endpos: Position,
    ):
        self.strtoken: str = strtoken
        self.token_type: TokenType = ttype
        self.startpos: Position = startpos
        self.endpos: Position = endpos

    def __repr__(self) -> str:
        start_line, start_col = self.startpos._line, self.startpos._col
        end_line, end_col = self.endpos._line, self.endpos._col
        return f"{start_line}:{start_col}-{end_line}:{end_col}:\t{self.token_type}\t{self.strtoken}"


"""
Steps
-----

1. Identify if it _could_ be a certain class.
2. Try to capture the token. If it is the correct class, we return a Token
object. Otherwise, we will return None.
"""


################################################################################
########## START IDENTIFICATION FUNCTIONS ######################################
################################################################################
def is_whitespace_start(text: Text) -> bool:  # [ \n\t\v\r]+
    """Note: the word "_start" in the function name is unnecessary. It is the
    start, the middle, and the end, because all characters fall into the same
    group."""
    c = text.getoffset(0)
    assert c != EOF
    return c.whitespace()


def is_comment_start(text: Text) -> bool:
    c = text.getoffset(0)
    next_c = text.getoffset(1)
    assert c != EOF
    if c == "#":
        return True
    elif c == "/" and (next_c == "*" or next_c == "/"):
        return True
    return False


def is_string_start(text: Text) -> bool:
    """We will only support strings surrounded by single double quotes for now."""
    c = text.getoffset(0)
    assert c != EOF
    return c == '"'


def is_number_start(text: Text) -> bool:
    """We will not support 0. or .0 numbers for now. + 10 is also not a single number."""
    c = text.getoffset(0)
    next_c = text.getoffset(1)
    assert c != EOF
    if c.isdecimal():
        return True
    elif c == "+" or c == "-":
        # Assuming next_c is not EOF... not that it would matter.
        return next_c.isdecimal()  # [0-9]
    return False


def is_literal_start(text: Text) -> bool:  # [A-Za-z_][A-Za-z0-9_]*
    c = text.getoffset(0)
    assert c != EOF
    return c.isalpha() or c == "_"


def is_standalone_punctuation_start(text: Text) -> bool:  # [()[]{},;]
    """Note: the word "_start" in the function name is unnecessary. It is the
    start, the middle, and the end, because this is only one character."""
    c = text.getoffset(0)
    assert c != EOF
    return c in {"(", ")", "[", "]", "{", "}", ";", ","}


def is_groupable_punctuation_start(text: Text) -> bool:
    """The punctuation characters _can_ be grouped, e.g. +=, **=, etc."""
    c = text.getoffset(0)
    assert c != EOF
    if c in "~!@$%^&*-+=|:<>./?":
        return True
    return False


################################################################################
########## EXTRACTION FUNCTIONS ################################################
################################################################################
def capture_whitespace(text: Text) -> "Token | None":
    c = text.getoffset(0)
    assert c != EOF

    startpos = text.getpos()
    i = 0
    while c.whitespace():
        i += 1
        c = text.getoffset(i)

    strtoken = text.text[text.current_idx : text.current_idx + i]
    for _ in range(i):
        next(text)
    endpos = text.getpos()

    token = Token(
        strtoken=strtoken,
        ttype=TokenType.WHITESPACE,
        startpos=startpos,
        endpos=endpos,
    )
    return token


def capture_comment(text: Text) -> "Token | None":
    """Types of comments:
    # This ends in \n or EOF.
    // This ends in \n or EOF.
    /* This can next but cannot end without its ending, which is */.
    """
    c = text.getoffset(0)
    next_c = text.getoffset(1)
    assert c != EOF

    startpos = text.getpos()
    if c == "#":
        start_comment = "#"
    elif c == "/" and next_c == "/":
        start_comment = "//"
    elif c == "/" and next_c == "*":
        start_comment = "/*"
    else:
        raise ValueError("unexpected comment starter")

    raise NotImplemented()


################################################################################
########## MAIN FUNCTIONS ######################################################
################################################################################
def get_text():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-file", type=str, default="./program.txt")
    args = parser.parse_args()

    with open(args.input_file) as f:
        text = f.read()

    return text


def get_tokens(text: str) -> List[Token]:
    tokens = []
    c = text.getoffset(0)
    while c != EOF:
        if is_whitespace_start(c):
            t = capture_whitespace(text)
            if t is not None:
                tokens.append(t)
                # Run this after every iteration
                c = next(text)
                continue
            # Otherwise, failure to capture whitespace
        if is_comment_start(c):
            t = capture_comment(text)
            if t is not None:
                tokens.append(t)
                # Run this after every iteration
                c = next(text)
                continue
            # Otherwise, failure to capture comment
        # Run this after every iteration
        c = next(text)
        continue


def main():
    text = get_text()
    tokens = get_tokens(text)

    for i, t in enumerate(tokens):
        print(f"Token {i}: {t}")


if __name__ == "__main__":
    main()
