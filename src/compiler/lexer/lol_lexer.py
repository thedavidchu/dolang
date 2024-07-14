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

from pathlib import Path
from typing import Dict, List

from compiler.lexer.lol_lexer_types import (
    LolTokenType,
    LolToken,
    CharacterStream,
    SYMBOL_CONTROL,
)

from compiler.error import LolError


class Lexer:
    def __init__(self, path: Path):
        self.stream = CharacterStream(path)
        self.tokens = []

    @staticmethod
    def _get_identifier_token_type(identifier: str):
        if identifier in {
            "while",
            "for",
            "namespace",
            "break",
            "continue",
            "not",
        }:
            return None
        key_words: Dict[str, LolTokenType] = {
            "if": LolTokenType.IF,
            "else": LolTokenType.ELSE,
            "let": LolTokenType.LET,
            "while": LolTokenType.WHILE,
            "for": LolTokenType.FOR,
            "function": LolTokenType.FUNCTION,
            "return": LolTokenType.RETURN,
            "namespace": LolTokenType.NAMESPACE,
            "module": LolTokenType.MODULE,
            "import": LolTokenType.IMPORT,
            "break": LolTokenType.BREAK,
            "continue": LolTokenType.CONTINUE,
            "and": LolTokenType.AND,
            "or": LolTokenType.OR,
            "not": LolTokenType.NOT,
        }
        token_type = key_words.get(identifier, LolTokenType.IDENTIFIER)
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
        if token_type is None:
            LolError.print_error(
                stream.text,
                pos,
                pos + len(identifier),
                "heretofore unsupported token",
            )
            raise NotImplementedError(
                f"lexer supports keyword '{identifier}'; no further stage does"
            )
        return LolToken(
            identifier,
            token_type,
            start_position=pos,
        )

    @staticmethod
    def lex_number(stream: CharacterStream):
        # NOTE(dchu): for now, we assume that the number is a base-10 integer.
        c, pos = stream.get_char(), stream.get_pos()
        current_token_type = LolTokenType.INTEGER
        # Concatentation to a list is more efficient than to a string, since
        # strings are immutable.
        token = []
        while c.isdecimal():
            if c.isdecimal():
                token.append(c)
                stream.next_char()
                c = stream.get_char()
            elif c == "." and current_token_type == LolTokenType.INTEGER:
                LolError.print_error(
                    stream.text,
                    pos,
                    pos + len(token),
                    "floats not supported yet",
                )
                raise NotImplementedError("floats not supported yet!")
                current_token_type = LolTokenType.FLOAT
                token.append(c)
                stream.next_char()
                c = stream.get_char()
            else:
                LolError.print_error(
                    stream.text,
                    pos,
                    pos + len(token),
                    "unrecognized number format (0b0, 0o0, 0x0, etc not supported)",
                )
                raise NotImplementedError
        return LolToken(
            "".join(token),
            current_token_type,
            start_position=pos,
        )

    @staticmethod
    def lex_string(stream: CharacterStream):
        c, pos = stream.get_char(), stream.get_pos()
        # Concatentation to a list is more efficient than to a string, since
        # strings are immutable.
        stream.next_char()
        token = ['"']
        while True:
            # TODO(dchu) support escaped quotations
            c = stream.get_char()
            if c == '"' or c is None:
                stream.next_char()
                break
            token.append(c)
            stream.next_char()
        # Add trailing quote
        token.append(c)
        return LolToken(
            "".join(token),
            LolTokenType.STRING,
            start_position=pos,
        )

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
                LolError.print_error(
                    stream.text,
                    pos,
                    pos + len("/*"),
                    "expecting closing '*/' for comment",
                )
                raise ValueError("expected terminal '*/' in the comment")
        return LolToken(
            "".join(token),
            LolTokenType.COMMENT,
            start_position=pos,
        )

    @staticmethod
    def _is_punctuation_implemented(token_type: LolTokenType) -> bool:
        # TODO(dchu): This is a hack! I should just maintain a list of
        #  unimplemented punctuation token types. The reason I do this is
        #  because it is very clear when inspecting the TokenType definition to
        #  see what is and isn't implemented.
        if (
            isinstance(token_type.value, tuple)
            and len(token_type.value) >= 2
            and token_type.value[1]
            in {
                LolTokenType.NOT_YET_IMPLEMENTED.value,
                LolTokenType.WONT_BE_IMPLEMENTED.value,
            }
        ):
            return False
        return True

    @staticmethod
    def lex_punctuation(stream: CharacterStream):
        start_pos = stream.get_pos()

        control = SYMBOL_CONTROL
        lexeme = []
        while True:
            c = stream.get_char()
            if c is None:
                if isinstance(control, LolTokenType):
                    token_type = control
                    break
                elif None in control:
                    token_type = control[None]
                    break
            if isinstance(control, LolTokenType):
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
                LolError.print_error(
                    stream.text, start_pos, start_pos + len(lexeme), ""
                )
                raise ValueError(
                    f"cannot append {c} to {''.join(lexeme)} -- potential bug, just separate the symbols"
                )

        if not Lexer._is_punctuation_implemented(token_type):
            LolError.print_error(
                stream.text,
                start_pos,
                start_pos + len(lexeme),
                "unimplemented token",
            )
            raise NotImplementedError

        return LolToken(
            "".join(lexeme),
            token_type,
            start_position=start_pos,
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
                LolError.print_error(
                    self.stream.text,
                    self.stream.get_pos(),
                    self.stream.get_pos() + 1,
                    "character is not supported",
                )
                raise ValueError(f"character '{c}' not supported!")


def tokenize(path: Path) -> List[LolToken]:
    t = Lexer(path)
    t.tokenize()
    return t.tokens
