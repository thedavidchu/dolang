# DEPRECATED!
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
from lib2to3.pgen2 import token
from multiprocessing.sharedctypes import Value
from typing import List
from typing_extensions import Self


EOF: str = None


class TokenType(str, Enum):
    WHITESPACE = "WHITESPACE"  # Indent vs non-indent
    COMMENT = "COMMENT"  # Multi-line vs non-multiline, nesting
    STRING = "STRING"  # Multi-quotes, single-vs-double quote
    IDENTIFIER = "LITERAL"  # Keyword, non-keyword
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

        sanitized_strtoken = repr(self.strtoken)
        return f"{start_line}:{start_col}-{end_line}:{end_col}:\t{self.token_type}\t{sanitized_strtoken}"


class Text:
    def __init__(self, text: str):
        self.text: str = text
        self.position: Position = Position(0, 1, 0)

    def viewnext(self, offset: int) -> str:
        if offset < 0:
            raise ValueError("idx must be non-zero!")
        if self.position._idx + offset >= len(self.text):
            return EOF
        return self.text[self.position._idx + offset]

    def __next__(self) -> str:
        if self.position._idx + 1 > len(self.text):
            return EOF

        c: str = self.viewnext(0)
        if c == "\n":
            self.position = self.position.new_line()
        else:
            self.position = self.position.new_col()
        return self.viewnext(0)

    def is_eof(self) -> bool:
        return self.viewnext(0) == EOF

    def viewnext(self, offset: int) -> str:
        if offset < 0:
            raise ValueError("idx must be non-zero!")
        if self.position._idx + offset >= len(self.text):
            return EOF
        return self.text[self.position._idx + offset]

    def getpos(self) -> Position:
        return self.position

    def fastforward(self, num: int) -> None:
        for _ in range(num):
            next(self)

    def capturetoken(self, offset: int, token_type: TokenType) -> Token:
        if offset < 0:
            raise ValueError("offset must be non-zero!")
        if self.position._idx + offset > len(self.text):
            return None
        strtoken = self.text[self.position._idx : self.position._idx + offset]
        startpos: Position = self.getpos()
        self.fastforward(offset)
        endpos: Position = self.getpos()
        token = Token(
            strtoken=strtoken,
            ttype=token_type,
            startpos=startpos,
            endpos=endpos,
        )
        return token


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
    c = text.viewnext(0)
    assert c != EOF
    return c.isspace()


def is_comment_start(text: Text) -> bool:
    c = text.viewnext(0)
    assert c != EOF
    if c == "#":
        return True
    next_c = text.viewnext(1)
    if c == "/" and (next_c == "*" or next_c == "/"):
        return True
    return False


def is_string_start(text: Text) -> bool:
    """We will only support strings surrounded by single double quotes for now."""
    c = text.viewnext(0)
    assert c != EOF
    return c == '"'


def is_number_start(text: Text) -> bool:
    """We will not support 0. or .0 numbers for now. + 10 is also not a single
    number."""
    c = text.viewnext(0)
    assert c != EOF
    if c.isdecimal():
        return True
    elif c == "+" or c == "-":
        next_c = text.viewnext(1)
        # We test if next_c is EOF, because a string method will not work on a
        # non-string type.
        if next_c == EOF:
            return False
        return next_c.isdecimal()  # [0-9]
    return False


def is_identifier_start(text: Text) -> bool:  # [A-Za-z_][A-Za-z0-9_]*
    c = text.viewnext(0)
    assert c != EOF
    return c.isalpha() or c == "_"


def is_standalone_punctuation_start(text: Text) -> bool:  # [()[]{},;]
    """Note: the word "_start" in the function name is unnecessary. It is the
    start, the middle, and the end, because this is only one character."""
    c = text.viewnext(0)
    assert c != EOF
    return c in {"(", ")", "[", "]", "{", "}", ";", ","}


def is_groupable_punctuation_start(text: Text) -> bool:
    """The punctuation characters _can_ be grouped, e.g. +=, **=, etc."""
    c = text.viewnext(0)
    assert c != EOF
    if c in "~!@$%^&*-+=|:<>./?":
        return True
    return False


################################################################################
########## EXTRACTION FUNCTIONS ################################################
################################################################################
def capture_whitespace(text: Text) -> "Token | None":
    c = text.viewnext(0)
    assert c != EOF

    i = 0
    while c != EOF and c.isspace():
        i += 1
        c = text.viewnext(i)

    return text.capturetoken(i, TokenType.WHITESPACE)


def capture_comment(text: Text) -> "Token | None":
    """Types of comments:
    # This ends in \n or EOF.
    // This ends in \n or EOF.
    /* This can next but cannot end without its ending, which is */.
    """
    c = text.viewnext(0)
    next_c = text.viewnext(1)
    assert c != EOF

    if c == "#":
        start_comment = "#"
        next_idx = 1
    elif c == "/" and next_c == "/":
        start_comment = "//"
        next_idx = 2
    elif c == "/" and next_c == "*":
        start_comment = "/*"
        next_idx = 2
    else:
        raise ValueError("unexpected comment starter")

    while True:
        next_c = text.viewnext(next_idx)

        if start_comment == "#":
            print(f"> {next_c=}")
            if next_c == "\n":
                token = text.capturetoken(next_idx + 1, TokenType.COMMENT)
                return token
            elif next_c == EOF:
                token = text.capturetoken(next_idx, TokenType.COMMENT)
                return token
            # increment next_idx, continue
        elif start_comment == "//":
            if next_c == "\n":
                token = text.capturetoken(next_idx + 1, TokenType.COMMENT)
                return token
            elif next_c == EOF:
                token = text.capturetoken(next_idx, TokenType.COMMENT)
                return token
            # increment next_idx, continue
        elif start_comment == "/*":
            if next_c == EOF:
                raise ValueError("unexpected EOF!")
            if next_c == "*":
                next_next_c = text.viewnext(next_idx + 1)
                if next_next_c == "/":
                    token = text.capturetoken(next_idx + 2, TokenType.COMMENT)
                    return token
        else:
            raise ValueError("unexpected comment started")

        # Must do at the end
        next_idx += 1
    return None


def capture_string(text: Text) -> "Token | None":
    c = text.viewnext(0)
    assert c != EOF

    if c != '"':
        raise ValueError("unexpected starting character")

    next_idx = 1
    next_c = text.viewnext(1)
    while True:
        next_c = text.viewnext(next_idx)
        # Skip '"'
        if next_c == "\\":
            next_next_c = text.viewnext(next_idx + 1)
            if next_next_c not in {
                "'",
                '"',
                "\\",
                "n",
                "r",
                "t",
                "b",
                "f",
                "v",
            }:
                raise ValueError(f"unexpected escaped character {next_c}")
            next_idx += 2
            continue
        if next_c == '"':
            print('\t> "')
            token = text.capturetoken(next_idx + 1, TokenType.STRING)
            print(f"\t> {text.viewnext(0)}")
            return token
        if next_c == EOF:
            raise ValueError("end of string without finishing quote!")

        # Call at the end
        next_idx += 1


def capture_number(text: Text) -> "Token | None":
    c = text.viewnext(0)
    assert c != EOF

    next_idx = 0
    if c == "+" or c == "-":
        if not text.viewnext(1).isdecimal():
            # We call an error instead of passing this off because we checked
            # for it in is_number_start()
            raise ValueError("expected number!")
        next_idx = 1
    elif not c.isdecimal():
        raise ValueError("expected number!")

    while True:
        next_c = text.viewnext(next_idx)
        if next_c not in "1234567890.":
            return text.capturetoken(next_idx, TokenType.NUMBER)
        next_next_c = text.viewnext(next_idx + 1)
        # Separate ..
        if next_c == "." and next_next_c == ".":
            return text.capturetoken(next_idx, TokenType.NUMBER)
        next_idx += 1


def capture_identifier(text: Text) -> "Token | None":
    c = text.viewnext(0)
    assert c != EOF

    if not c.isalpha() and c != "_":
        raise ValueError("Unexpected literal start character!")

    idx = 1
    while True:
        c = text.viewnext(idx)
        if not c.isalnum() and c != "_":
            return text.capturetoken(idx, TokenType.IDENTIFIER)
        idx += 1


def capture_standalone_punctuation(text: Text) -> "Token | None":
    c = text.viewnext(0)
    assert c != EOF

    if not c in r"(){}[],;":
        raise ValueError("unexpected character!")
    return text.capturetoken(1, TokenType.PUNCTUATION)


def capture_groupable_punctuation(text: Text) -> "Token | None":
    """
    Single Characters: ~ ! @ % ^ & * - + = | : < > . ?
    Double Characters: ~= != @= %= ^= &= *= -= += == |= := <= >= ?= ** && || ..
    Triple Characters: === **= ... ..=
    """
    c = text.viewnext(0)
    assert c != EOF

    if not c in "~!@$%^&*-+=|:<>./?":
        raise ValueError("unexpected character!")

    first_c = text.viewnext(0)
    second_c = text.viewnext(1)
    third_c = text.viewnext(2)

    three_char = "=== **= ... ..=".split(" ")
    two_char = "~= != @= %= ^= &= *= -= += == |= := <= >= ?= ** && || ..".split(
        " "
    )
    one_char = "~ ! @ % ^ & * - + = | : < > . ?".split(" ")

    # Select greedily
    if (first_c, second_c, third_c) in set(map(tuple, three_char)):
        return text.capturetoken(3, TokenType.PUNCTUATION)
    elif (first_c, second_c) in set(map(tuple, two_char)):
        return text.capturetoken(2, TokenType.PUNCTUATION)
    elif (first_c,) in set(map(tuple, one_char)):
        return text.capturetoken(1, TokenType.PUNCTUATION)

    raise ValueError("unknown groupable type!")


################################################################################
########## MAIN FUNCTIONS ######################################################
################################################################################
def get_text() -> Text:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-file", type=str, default="./program.txt")
    args = parser.parse_args()

    with open(args.input_file) as f:
        text = f.read()

    return Text(text)


def get_tokens(text: Text) -> List[Token]:
    tokens = []
    while not text.is_eof():
        print(f"{len(tokens)=}, {text.viewnext(0)=}")
        if is_whitespace_start(text):
            t = capture_whitespace(text)
            if t is not None:
                tokens.append(t)
                continue
            # Otherwise, failure to capture whitespace
            raise ValueError(
                "failed to capture whitespace, even though I'm sure it was whitespace!"
            )
        if is_comment_start(text):
            t = capture_comment(text)
            if t is not None:
                tokens.append(t)
                continue
            # Otherwise, failure to capture comment
            raise ValueError(
                "failed to capture comment, even though I'm sure it was a comment!"
            )
        if is_string_start(text):
            t = capture_string(text)
            if t is not None:
                tokens.append(t)
                continue
            # Otherwise, failure to capture comment
            raise ValueError(
                "failed to capture string, even though I'm sure it was a string!"
            )
        if is_number_start(text):
            t = capture_number(text)
            if t is not None:
                tokens.append(t)
                continue
            # Otherwise, failure to capture comment
            raise ValueError(
                "failed to capture number, even though I'm sure it was a number!"
            )
        if is_identifier_start(text):
            t = capture_identifier(text)
            if t is not None:
                tokens.append(t)
                continue
            # Otherwise, failure to capture comment
            raise ValueError(
                "failed to capture identifier, even though I'm sure it was a identifier!"
            )
        if is_standalone_punctuation_start(text):
            t = capture_standalone_punctuation(text)
            if t is not None:
                tokens.append(t)
                continue
            # Otherwise, failure to capture comment
            raise ValueError(
                "failed to capture stand-alone punctuation, even though I'm sure it was a stand-alone punctuation!"
            )
        if is_groupable_punctuation_start(text):
            t = capture_groupable_punctuation(text)
            if t is not None:
                tokens.append(t)
                continue
            # Otherwise, failure to capture comment
            raise ValueError(
                "failed to capture groupable punctuation, even though I'm sure it was a groupable punctuation!"
            )
        next(text)
    return tokens


def main():
    text = get_text()
    tokens = get_tokens(text)

    for i, t in enumerate(tokens):
        if t.token_type is TokenType.WHITESPACE:
            continue
        print(f"Token {i}: {t}")


if __name__ == "__main__":
    main()
