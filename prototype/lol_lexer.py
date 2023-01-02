"""
# Parser

## Language

This parser will parse white-space separated tokens. It will output the results
into a text file in the form:

```
<absolute index start: int>,<line number start: int>,<column number start: int>,<token type id: int>,<token: string>
```

We use white-space as the delimiter because CSVs are well formed.

********************************************************************************

The accepted tokens are (ASCII):

1. words : [A-Za-z_][A-Za-z0-9_]*
    - Keywords: if, else, while, function, return
2. integers : [1-9][0-9]*
3. strings : ["](\"|[^"])*["]
4. parentheses : "(" or ")"
5. braces : "{" or "}"
6. brackets : "[" or "]"
7. dot : "."
8. comma : ","
9. equals : "="
10. colon : ":"
11. comments : #.*
12. semicolon : ";"

********************************************************************************

Future tokens to accept in the future are:

1. More types of numbers (binary, octal, hexadecimal, floats, scientific notation)
2. Differentiate keywords from words (not really necessary, we can do this later)
3. Add support for other operators (!, %, ^, &, *, +, -, ==, <, >, <=, >=, ->, |, ~, /, //)
4. Add escaping for strings ("\n\t\\\v\a\b")
5. Add support for single quote strings?
6. Add multiline strings ('''multiline string''')
7. Add multiline comments
"""

text = """
# My first program!
print("Hello, World!")
"""

medium_text = """
io = import("io")

io.stdout("Hello, World!")

function sum3(a: int, b: int, c: int): int {
    return a.add(b).add(c)
}

let a: int = 0
let b: int = 1
let c: int = 2
let d: int = sum3(a, b, c)
io.stdout("Answer: ", d)
"""

advanced_text = """
io = import ( "io" );

# Fibonacci sequence
function fibonacci ( iterations : int ) -> int {
    let result : int = 0 , prev_result : int = 0
    for _ in range ( 0 , 10 ) {
        result = 0
    }
}

let a : int = fibonacci ( 0 )
let b : int = fibonacci ( 1 )

let a_str : str = str ( a )
let b_str : str = str ( b )

io . stdout ( a_str )
io . stdout ( b_str )
"""

from typing import Tuple
from enum import Enum, auto, unique


@unique
class TokenType(Enum):
    LPAREN = auto()    # (
    RPAREN = auto()    # )
    LBRACK = auto()    # [
    RBRACK = auto()    # ]
    LBRACE = auto()    # {
    RBRACE = auto()    # }

    DOT = auto()        # .
    COMMA = auto()      # ,
    EQUAL = auto()      # =
    COLON = auto()      # :

    NEWLINE = auto()    # \n
    
    WORD = auto()       # [A-Za-z_][A-Za-z_0-9]
    STRING = auto()     # "[^"\n]*"
    DEC = auto()        # [1-9][0-9]*
    COMMENT = auto()    # #.*

    # Keywords
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FUNCTION = auto()
    RETURN = auto()


class Token:
    def __init__(self, idx: int, line_number: int, column_number: int, token_type: TokenType, text: str):
        self.idx = idx
        self.line_number = line_number
        self.column_number = column_number
        self.token_type = token_type
        self.text = text

    def __str__(self):
        """Serialize the token."""
        return f"{self.idx},{self.line_number},{self.column_number},{self.token_type.value},{self.text}"


    def __repr__(self):
        """Pretty print the token. This is NOT for serialization, because the
        token type should be an integer id so that it's easier to parse."""
        return f"{self.idx},{self.line_number},{self.column_number},{self.token_type},{self.text}"


class CharacterStream:
    def __init__(self, src: str):
        self.src = src
        self.idx = 0
        self.line_number = 1
        self.column_number = 0
        self.tokens = []

    def get_char(self) -> str:
        """Get the current character or return None"""
        if self.idx >= len(self.src):
            return None
        return self.src[self.idx]

    def next_char(self):
        """Advance to the next character or return early if we are at the last character."""
        c = self.get_char()
        if c is None:
            return
        self.idx += 1
        if c == "\n":
            self.line_number += 1
            self.column_number = 0
        else:
            self.column_number += 1

    def get_pos(self) -> Tuple[int, int, int]:
        """Get the current character position in a (absolute_index, line_number,
        column_number) tuple"""
        return (self.idx, self.line_number, self.column_number)


class Tokenizer:
    def __init__(self, src: str):
        self.stream = CharacterStream(src)
        self.tokens = []

    def get_word(self, stream: CharacterStream):
        # Concatentation to a list is more efficient than to a string, since
        # strings are immutable.
        c, pos = stream.get_char(), stream.get_pos()
        token = []
        while c.isalnum() or c == "_":
            token.append(c)
            stream.next_char()
            c = stream.get_char()

        word = "".join(token)
        if word == "if":
            return Token(*pos, TokenType.IF, word)
        elif word == "else":
            return Token(*pos, TokenType.ELSE, word)
        elif word == "while":
            return Token(*pos, TokenType.WHILE, word)
        elif word == "function":
            return Token(*pos, TokenType.FUNCTION, word)
        elif word == "return":
            return Token(*pos, TokenType.RETURN, word)
        else:
            return Token(*pos, TokenType.WORD, word)

    def get_dec(self, stream: CharacterStream):
        # NOTE(dchu): for now, we assume that the number is a base-10 integer.
        c, pos = stream.get_char(), stream.get_pos()
        # Concatentation to a list is more efficient than to a string, since
        # strings are immutable.
        token = []
        while c.isdecimal():
            token.append(c)
            stream.next_char()
            c = stream.get_char()
        return Token(*pos, TokenType.DEC, "".join(token))

    def get_string(self, stream: CharacterStream):
        c, pos = stream.get_char(), stream.get_pos()
        # Concatentation to a list is more efficient than to a string, since
        # strings are immutable.

        # We need to do one iteration outside the loop, since the first
        # character is the same as the stop character in a string.
        token = [c]
        stream.next_char()
        c = stream.get_char()
        while c != "\"" and c is not None:
            token.append(c)
            stream.next_char()
            c = stream.get_char()
        # Add trailing quote
        token.append(c)
        stream.next_char()
        return Token(*pos, TokenType.STRING, "".join(token))

    def get_comment(self, stream: CharacterStream):
        c, pos = stream.get_char(), stream.get_pos()
        # Concatentation to a list is more efficient than to a string, since
        # strings are immutable.
        token = []
        while c != "\n" and c is not None:
            token.append(c)
            stream.next_char()
            c = stream.get_char()
        return Token(*pos, TokenType.COMMENT, "".join(token))

    def get_single_char(self, stream: CharacterStream):
        c, pos = stream.get_char(), stream.get_pos()
        stream.next_char()
        if c == "(":
            return Token(*pos, TokenType.LPAREN, c)
        elif c == ")":
            return Token(*pos, TokenType.RPAREN, c)
        elif c == "[":
            return Token(*pos, TokenType.LBRACK, c)
        elif c == "]":
            return Token(*pos, TokenType.RBRACK, c)
        elif c == "{":
            return Token(*pos, TokenType.LBRACE, c)
        elif c == "}":
            return Token(*pos, TokenType.RBRACE, c)
        elif c == ",":
            return Token(*pos, TokenType.COMMA, c)
        elif c == ".":
            return Token(*pos, TokenType.DOT, c)
        elif c == "=":
            return Token(*pos, TokenType.EQUAL, c)
        elif c == ":":
            return Token(*pos, TokenType.COLON, c)
        elif c == ";":
            return Token(*pos, TokenType.SEMICOLON, c)
        else:
            raise ValueError(f"character '{c}' not supported!")

    def tokenize(self):
        while True:
            c = self.stream.get_char()
            pos = self.stream.get_pos()

            if c is None:
                break
            
            if c.isspace():
                self.stream.next_char()
            elif c.isalpha() or c == "_":
                token = self.get_word(self.stream)
                self.tokens.append(token)
            elif c.isdecimal():
                token = self.get_dec(self.stream)
                self.tokens.append(token)
            elif c == "\"":
                token = self.get_string(self.stream)
                self.tokens.append(token)
            elif c == "#":
                token = self.get_comment(self.stream)
                self.tokens.append(token)
            elif c in "()[]{}.,=:;":
                token = self.get_single_char(self.stream)
                self.tokens.append(token)
            else:
                raise ValueError(f"character '{c}' not supported!")

if __name__ == "__main__":
    tokenizer = Tokenizer(medium_text)
    tokenizer.tokenize()
    for token in tokenizer.tokens:
        print(repr(token))
    
