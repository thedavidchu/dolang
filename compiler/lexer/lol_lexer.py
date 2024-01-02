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

1. identifiers : [A-Za-z_][A-Za-z0-9_]*
    - Keywords: if, else, while, function, return, let, namespace
2. decimal integers : [1-9][0-9]*
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
13. arrow : "->" # N.B. NOT a binary op. This is only used in the context of functions

********************************************************************************

Future tokens to accept in the future are:

1. More types of numbers (binary, octal, hexadecimal, floats, scientific notation)
2. Differentiate keywords from identifiers (not really necessary, we can do this later)
3. Add support for other operators (!, %, ^, &, *, +, -, ==, <, >, <=, >=, ->, |, ~, /, //)
4. Add escaping for strings ("\n\t\\\v\a\b")
5. Add support for single quote strings?
6. Add multiline strings ('''multiline string''')
7. Add multiline comments
"""

lexeme = """
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

from typing import List

from lexer.lol_lexer_types import TokenType, Token, CharacterStream


class Tokenizer:
    def __init__(self, src: str):
        self.stream = CharacterStream(src)
        self.tokens = []

    def get_identifier(self, stream: CharacterStream):
        # Concatentation to a list is more efficient than to a string, since
        # strings are immutable.
        c, pos = stream.get_char(), stream.get_pos()
        token = []
        while c.isalnum() or c == "_":
            token.append(c)
            stream.next_char()
            c = stream.get_char()

        ident = "".join(token)
        if ident == "if":
            return Token(*pos, TokenType.IF, ident)
        elif ident == "else":
            return Token(*pos, TokenType.ELSE, ident)
        elif ident == "while":
            return Token(*pos, TokenType.WHILE, ident)
        elif ident == "function":
            return Token(*pos, TokenType.FUNCTION, ident)
        elif ident == "return":
            return Token(*pos, TokenType.RETURN, ident)
        elif ident == "let":
            return Token(*pos, TokenType.LET, ident)
        elif ident == "namespace":
            return Token(*pos, TokenType.NAMESPACE, ident)
        elif ident == "module":
            return Token(*pos, TokenType.MODULE, ident)
        elif ident == "import":
            return Token(*pos, TokenType.IMPORT, ident)
        else:
            return Token(*pos, TokenType.IDENTIFIER, ident)

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
        while c != '"' and c is not None:
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

    def get_symbol(self, stream: CharacterStream):
        c, pos = stream.get_char(), stream.get_pos()
        stream.next_char()
        if c == "(":
            return Token(*pos, TokenType.LPAREN, c)
        elif c == ")":
            return Token(*pos, TokenType.RPAREN, c)
        elif c == "[":
            return Token(*pos, TokenType.LSQB, c)
        elif c == "]":
            return Token(*pos, TokenType.RSQB, c)
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
            if stream.get_char() == ":":
                stream.next_char()
                return Token(*pos, TokenType.COLON_COLON, "::")
            return Token(*pos, TokenType.COLON, c)
        elif c == ";":
            return Token(*pos, TokenType.SEMICOLON, c)
        elif c == "+":
            return Token(*pos, TokenType.PLUS, c)
        elif c == "-":
            if stream.get_char() == ">":
                stream.next_char()
                return Token(*pos, TokenType.ARROW, "->")
            return Token(*pos, TokenType.MINUS, c)
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
                token = self.get_identifier(self.stream)
                self.tokens.append(token)
            elif c.isdecimal():
                token = self.get_dec(self.stream)
                self.tokens.append(token)
            elif c == '"':
                token = self.get_string(self.stream)
                self.tokens.append(token)
            elif c == "#":
                token = self.get_comment(self.stream)
                # TODO(dchu): re-enable this once the AST supports comments.
                # Right now, we skip comments.
                # self.tokens.append(token)
            elif c in "()[]{}.,=:;-+":
                # TODO(dchu): '-' does not necessarily imply a punctuation mark.
                # It can also be the start of a negative number, e.g. -10.3
                token = self.get_symbol(self.stream)
                self.tokens.append(token)
            else:
                raise ValueError(f"character '{c}' not supported!")


def tokenize(text: str) -> List[Token]:
    t = Tokenizer(text)
    t.tokenize()
    return t.tokens
