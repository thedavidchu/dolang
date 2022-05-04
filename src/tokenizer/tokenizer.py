"""
================================================================================

TODO
====

* Tokens
    * Get line number and column number
* Comments
    * Support multi-character comments
* String
    * Check escaped character is in the set {"\\", "\", "\'", "\a",}
"""


import argparse
from enum import Enum


PUNCTUATION = {c for c in r"~!@#$%^&*-+=|\:<>.?/"} - {"#"} # Remove comment char
INVALID_CHAR = None

class TokenType(str, enum):
    PUNCTUATION = "PUNCTUATION" # Single punctuation, multi-punctuation, specific type
    NUMBER = "NUMBER" # Float, int, complex
    IDENTIFIER = "IDENTIFIER" # Keyword, identifier
    COMMENT = "COMMENT" # Block comment (may be nested), line comment
    

class Text:
    def __init__(self, text: str):
        self.text = text
        self.idx = 0
        self.line_number: int = 1  # Line numbers start on 1
        self.col_number: int = 0   # Col numbers start on 0
        
        self.prev_c: str = INVALID_CHAR

    def next_char(self) -> str:
        self.idx += 1
        if self.idx >= len(self.text):
            return INVALID_CHAR
        c = self.text[self.idx]
        # We look at the previous character because a new line pushes the _next_
        # character onto the new line.
        if self.prev_c == "\n":
            self.line_number += 1
            self.col_number = 0
        else:
            self.col_number += 1
        return c
         

class Token:
    def __init__(self, token: str, token_type: str):
        self.token = token.strip()
        self.token_type = token_type

    def __repr__(self):
        return f"({self.token_type}): {self.token}"


def printslice(text: str, start: int, last_minus_one: int):
    print(f"({start}..{last_minus_one + 1}): {text[start:last_minus_one + 1].strip()}")


def is_comment(text: str, i: int):
    return text[i] in {"#"}


def goto_endcomment(text: str, i_0: int):
    """Get the last character belonging to the comment."""
    i = i_0
    start = text[i_0]   # Doesn't support multi-character comment-starts
    while i < len(text):
        c = text[i]
        if start == "#" and c == "\n":
            return i
        # This is at the end
        i += 1
    raise ValueError("no end to comment")


def is_string(text: str, i: int):
    return text[i] in {"\"", "\'", "`"}


def goto_endstring(text: str, i_0: int):
    # TODO(dchu): enable for ' and `
    start = text[i_0]
    i = i_0 + 1 # Start one after start
    while i < len(text):
        c = text[i]
        if c == "\\":
            # Skip the next character
            # TODO(dchu): check it is a valid character to skip. We can do this
            # when we validate the tokens.
            i += 2
            continue
        elif start == "\"" and c == "\"":
            return i
        elif start == "\'" and c == "\'":
            return i
        elif start == "`" and c == "`":
            return i
        # This is at the end
        i += 1
    raise ValueError("no end to string")

def is_singlechar(text: str, i: int):
    return text[i] in {"`", "(", ")", "{", "}", "[", "]", ";", ","}


def is_number(text: str, i: int):
    if text[i] in {"+", "-", "."} and len(text) > i + 1 and text[i + 1].isdecimal():
        return True
    elif text[i].isdecimal():
        return True
    else:
        return False

def goto_endnumber(text: str, i_0: int):
    """Go to the end of a number.

    Integers
    --------
    * Binary      : "0[Bb][0-1]+"
        * 0b0
        * 0b00
        * 0b1
        * 0b (invalid)
    * Octal       : "0[Oo][0-7]+"
        * 0o0
        * 0o00
        * 0o7
        * 0o (invalid)
    * Decimal     : "[+-]?(0|[1-9][0-9]*)"
        * 0
        * 00 (invalid)
        * -0 (valid)
    * Hexadecimal : "0[Xx][0-9A-Fa-f]*"
        * 0x0
        * 0x00
        * 0xF
        * 0xFf (bad, but valid)
        * 0x (invalid)

    Floating Point
    --------------
    * Let DECIMAL := "(0|[1-9][0-9]*)"
    * Floating Point : "[+-]?((DECIMAL\.[0-9]+|DECIMAL\.|\.[0-9]+)([Ee][+-]?DECIMAL)?|DECIMAL[Ee][+-]?DECIMAL)"
        * i.e. [+-]?(DECIMAL\.[0-9]+|DECIMAL\.|\.[0-9]+)([Ee][+-]?)DECIMAL)?
                * i.e. [+-]?DECIMAL\.[0-9]+([Ee][+-]?)DECIMAL)?
                    or [+-]?DECIMAL\.([Ee][+-]?)DECIMAL)?
                    or [+-]?\.[0-9]+([Ee][+-]?)DECIMAL)?
            or [+-]?DECIMAL[Ee][+-]?DECIMAL
        * +.0
        * -0.
        * +. (invalid)

    Complex
    -------
    * Let FLOAT := any floating point number as defined above
    * Complex     : "(FLOAT)j" (N.B. does not include REAL part)
    """
    i = i_0 + 1 # Skip the first
    while i < len(text):
        c = text[i]
        if c in {"e", "E"}:
            # Allow the next letter to be + or -
            pass
        elif c.isalnum() or c == "_":
            i += 1
            continue
        elif c == ".":
            # Ensure that the next is either an number or e
            if text[i + 1] in {"e", "E"} or text[i + 1].isdecimal():
                i += 1
                continue
            else:
                return i - 1
        # Does not parse 1.23 (.) or 1e+23 (+) or 1.23e-45 (. and -)
        return i - 1
    raise ValueError("no end to number")


def is_identifier(text: str, i: int):
    return text[i].isalpha() or text[i] == "_"


def goto_endidentifier(text: str, i_0: int):
    i = i_0 + 1
    while i < len(text):
        c = text[i]
        if c.isalnum() or c == "_":
            i += 1
            continue
        return i - 1
    raise ValueError("no end to identifier")


def is_punctuation(text: str, i: int):
    return text[i] in PUNCTUATION

def goto_endpunctuation(text: str, i_0: int):
    i = i_0 + 1
    while i < len(text):
        c = text[i]
        if c in {"+", "-"} and is_number(text, i):
            return i - 1
        # How to deal with 0..10 vs +.10?
        elif c == "." and is_number(text, i):
            raise NotImplemented("How to deal with ..10 vs +.10?")
            return i - 1
        elif c in PUNCTUATION:
            i += 1
            continue
        return i - 1
    raise ValueError("no end to punctuation")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-file", type=str, default="./program.txt")
    args = parser.parse_args()

    with open(args.input_file) as f:
        text = f.read()

    tokens = []
    i = 0
    while i < len(text):
        c = text[i]
        if c.isspace():
            i += 1  # We increment here because there is no "goto"
            continue
        elif is_comment(text, i):
            i_end = goto_endcomment(text, i)
            # If it ends in a '\n', it will not print the newline.
            tokens.append(Token(token=text[i:i_end+1], token_type="Comment"))
            print(tokens[-1])
            i = i_end
        elif is_string(text, i):
            i_end = goto_endstring(text, i)
            tokens.append(Token(token=text[i:i_end+1], token_type="String"))
            print(tokens[-1])
            i = i_end
        elif is_singlechar(text, i):
            tokens.append(Token(token=text[i:i+1], token_type="Single-Char"))
            print(tokens[-1])
        elif is_number(text, i):
            i_end = goto_endnumber(text, i)
            tokens.append(Token(token=text[i:i_end+1], token_type="Number"))
            print(tokens[-1])
            i = i_end
        elif is_identifier(text, i):
            i_end = goto_endidentifier(text, i)
            tokens.append(Token(token=text[i:i_end+1], token_type="Identifier"))
            print(tokens[-1])
            i = i_end
        elif is_punctuation(text, i):
            i_end = goto_endpunctuation(text, i)
            tokens.append(Token(token=text[i:i_end+1], token_type="Punctuation"))
            print(tokens[-1])
            i = i_end
        else:
            raise ValueError(f"unrecognized character: {text[i]}")
        
        # This is at the end
        i += 1

    for t in tokens:
        print(t)

if __name__ == "__main__":
    main()
