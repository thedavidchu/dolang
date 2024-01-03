"""
# Lexer

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
from typing import Dict, List

from lexer.lol_lexer_types import (
    TokenType, Token, CharacterStream, SYMBOL_CONTROL
)


class Lexer:
    def __init__(self, src: str):
        self.stream = CharacterStream(src)
        self.tokens = []

    @staticmethod
    def _get_identifier_token_type(identifier: str):
        if identifier in {
            "if", "else", "while", "for", "namespace", "break", "continue",
            "and", "or", "not"
        }:
            raise NotImplementedError(
                f"lexer supports keyword '{identifier}'; no further stage does"
            )
        key_words: Dict[str, TokenType] = {
            "if": TokenType.IF,
            "else": TokenType.ELSE,
            "let": TokenType.LET,
            "while": TokenType.WHILE,
            "for": TokenType.FOR,
            "function": TokenType.FUNCTION,
            "return": TokenType.RETURN,
            "namespace": TokenType.NAMESPACE,
            "module": TokenType.MODULE,
            "import": TokenType.IMPORT,
            "break": TokenType.BREAK,
            "continue": TokenType.CONTINUE,
            "and": TokenType.AND,
            "or": TokenType.OR,
            "not": TokenType.NOT,
        }
        token_type = key_words.get(identifier, TokenType.IDENTIFIER)
        return token_type

    @staticmethod
    def lex_identifier(stream: CharacterStream):
        # Concatentation to a list is more efficient than to a string, since
        # strings are immutable.
        c, pos = stream.get_char(), stream.get_pos()
        token = []
        while c.isalnum() or c == "_":
            token.append(c)
            stream.next_char()
            c = stream.get_char()

        identifier = "".join(token)
        token_type = Lexer._get_identifier_token_type(identifier)
        return Token(
            identifier,
            token_type,
            start_position=pos,
            full_text=stream.get_text()
        )

    @staticmethod
    def lex_number(stream: CharacterStream):
        # NOTE(dchu): for now, we assume that the number is a base-10 integer.
        c, pos = stream.get_char(), stream.get_pos()
        current_token_type = TokenType.INTEGER
        # Concatentation to a list is more efficient than to a string, since
        # strings are immutable.
        token = []
        while c.isdecimal():
            if c.isdecimal():
                token.append(c)
                stream.next_char()
                c = stream.get_char()
            elif c == "." and current_token_type == TokenType.INTEGER:
                raise NotImplementedError("floats not supported yet!")
                current_token_type = TokenType.FLOAT
                token.append(c)
                stream.next_char()
                c = stream.get_char()
            else:
                raise NotImplementedError
        return Token("".join(token), current_token_type, start_position=pos, full_text=stream.get_text())

    @staticmethod
    def lex_string(stream: CharacterStream):
        pos = stream.get_pos()
        # Concatentation to a list is more efficient than to a string, since
        # strings are immutable.
        stream.next_char()
        c = stream.get_char()
        token = [c]
        while c != '"' and c is not None:
            token.append(c)
            stream.next_char()
            c = stream.get_char()
        # Add trailing quote
        token.append(c)
        stream.next_char()
        return Token("".join(token), TokenType.STRING, start_position=pos, full_text=stream.get_text())

    @staticmethod
    def lex_comment(stream: CharacterStream):
        """Get a comment that is like a C-style comment: /* Comment */. We
        assume that there is already a '/*' and the front."""
        pos = stream.get_pos()
        assert stream.get_char() == "/" and stream.get_char(offset=1) == "*"
        stream.next_char()
        stream.next_char()
        # Concatentation to a list is more efficient than to a string, since
        # strings are immutable.
        token = ["/*"]
        c = stream.get_char()
        while True:
            token.append(c)
            stream.next_char()
            c, n = stream.get_char(), stream.get_char(offset=1)
            if c == "*" and n == "/":
                stream.next_char()
                stream.next_char()
                break
            elif c is None:
                raise ValueError("expected terminal '*/' in the comment")
        return Token("".join(token), TokenType.COMMENT, start_position=pos, full_text=stream.get_text())

    @staticmethod
    def _is_punctuation_implemented(token_type: TokenType) -> bool:
        # TODO(dchu): This is a hack! I should just maintain a list of
        #  unimplemented punctuation token types. The reason I do this is
        #  because it is very clear when inspecting the TokenType definition to
        #  see what is and isn't implemented.
        if (
            isinstance(token_type.value, tuple)
            and len(token_type.value) >= 2
            and token_type.value[1] in {
                TokenType.NOT_YET_IMPLEMENTED, TokenType.WONT_BE_IMPLEMENTED
            }
        ):
            raise NotImplementedError(
                f"token_type {token_type.n} not implemented"
            )
        return True

    @staticmethod
    def lex_punctuation(stream: CharacterStream):
        c, pos = stream.get_char(), stream.get_pos()
        if c is None:
            raise ValueError("expected more characters")

        control = SYMBOL_CONTROL
        lexeme = []
        while True:
            c = stream.get_char()
            if isinstance(control, TokenType):
                token_type = control
                break
            elif c in control:
                lexeme.append(c)
                stream.next_char()
                control = control[c]
            elif None in control:
                token_type = control[None]
                break
            else:
                raise ValueError(f"cannot append {c} to {''.join(lexeme)} -- potential bug, just separate the symbols")

        if not Lexer._is_punctuation_implemented(token_type):
            raise NotImplementedError

        return Token(
            "".join(lexeme), token_type, start_position=pos,
            full_text=stream.get_text()
            )

    def tokenize(self):
        while True:
            c = self.stream.get_char()
            if c is None:
                break

            if c.isspace():
                self.stream.next_char()
            elif c.isalpha() or c == "_":
                token = self.lex_identifier(self.stream)
                self.tokens.append(token)
            elif c.isdecimal():
                token = self.lex_number(self.stream)
                self.tokens.append(token)
            elif c == '"':
                token = self.lex_string(self.stream)
                self.tokens.append(token)
            elif c == "/" and self.stream.get_char(offset=1) == "*":
                _unused_token = self.lex_comment(self.stream)
                # TODO(dchu): re-enable this once the AST supports comments.
                # Right now, we skip comments.
                # self.tokens.append(_unused_token)
            elif c in SYMBOL_CONTROL:
                # TODO(dchu): '-' does not necessarily imply a punctuation mark.
                # It can also be the start of a negative number, e.g. -10.3
                token = self.lex_punctuation(self.stream)
                self.tokens.append(token)
            else:
                raise ValueError(f"character '{c}' not supported!")


def tokenize(text: str) -> List[Token]:
    t = Lexer(text)
    t.tokenize()
    return t.tokens
