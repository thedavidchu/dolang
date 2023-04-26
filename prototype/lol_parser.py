"""
Sources
-------

I used the LLVM Kaleidoscope tutorial extensively.

TODO
----

1. Differentiate between nodes and leaves
    - Leaf: literal (decimal, string, variable, op)
2. Handle errors instead of `assert`
"""
from typing import List, Union

from lol_lexer import Token, TokenType, tokenize
from lol_parser_token_stream import TokenStream
from lol_parser_types import (
    DecimalLeaf,
    StringLeaf,
    IdentifierLeaf,
    OperatorLeaf,
    BinOpNode,
    FunctionPrototypeNode,
    FunctionDefNode,
    FunctionCallNode,
    LetNode,
    ReturnNode,
    NamespaceNode,
    # Abstract Types
    LiteralLeaf,
    ASTNode,
)
from lol_error import print_parser_error


def eat_token(stream: TokenStream, expected_type: TokenType) -> Token:
    token = stream.get_token()
    if token.type() != expected_type:
        error_msg = f"expected {expected_type.name}, got {token.type_name()}"
        print_parser_error(stream, error_msg)
        raise ValueError(error_msg)
    stream.next_token()
    return token


def parse_literal(stream: TokenStream) -> LiteralLeaf:
    token = stream.get_token()
    if token.type() == TokenType.STRING:
        stream.next_token()
        return StringLeaf(token)
    elif token.type() == TokenType.DEC:
        stream.next_token()
        return DecimalLeaf(token)
    else:
        raise ValueError(f"unexpected token type: {repr(token)}")


def parse_paren(stream: TokenStream) -> ASTNode:
    eat_token(stream, TokenType.LPAREN)
    ret = parse_expr(stream)
    eat_token(stream, TokenType.RPAREN)
    return ret


def parse_identifier(
    stream: TokenStream,
) -> Union[IdentifierLeaf, FunctionCallNode]:
    """Parse both variables and function calls.

    This is due to the semantics we do not know whether the identifier will be a
    variable name or a function call.

    In the future, it may be an array thing too array[100]."""
    token = eat_token(stream, TokenType.IDENTIFIER)

    if stream.get_token().type() != TokenType.LPAREN:
        return IdentifierLeaf(token)

    # Call
    eat_token(stream, TokenType.LPAREN)
    args = []
    # TODO(dchu): fix the bug where this will exceed the array limits of the
    # token stream if it doesn't find anything.
    while stream.get_token().type() != TokenType.RPAREN:
        args.append(parse_expr(stream))
        if stream.get_token().type() == TokenType.RPAREN:
            break
        elif stream.get_token().type() == TokenType.COMMA:
            continue
        else:
            print_parser_error(
                stream,
                error_msg=f"Expected COMMA or RPAREN, got {stream.get_token().type()}",
            )
            raise ValueError("Expected COMMA or RPAREN")
    eat_token(stream, TokenType.RPAREN)
    return FunctionCallNode(IdentifierLeaf(token), args)


# TODO(dchu): figure out why this is called "primary"
def parse_primary(stream: TokenStream) -> ASTNode:
    """Helper functions for parsing identifiers, literals, and parenthetic expressions."""
    token = stream.get_token()
    if token.type() == TokenType.IDENTIFIER:
        return parse_identifier(stream)
    elif token.type() in {TokenType.DEC, TokenType.STRING}:
        return parse_literal(stream)
    elif token.type() == TokenType.LPAREN:
        return parse_paren(stream)
    else:
        error_msg = f"unrecognized primary {token}"
        print_parser_error(stream, error_msg)
        raise ValueError(error_msg)


# TODO(dchu): refactor this to make it smarter. Also move the hard-coded
# precedence somewhere smarter.
def get_binop_precedence(op: Token) -> int:
    precedence = {
        # The '::' operator should always be on the left of any '.' operators,
        # so it has precedence due to left-associativity anyways.
        TokenType.COLON_COLON: 1500,  # Highest
        TokenType.DOT: 1400,
        TokenType.ARROW: 1400,
        # Prefix operators have precedence of 1300
        TokenType.STAR: 1200,
        TokenType.SLASH: 1200,  # TODO(dchu): Is this real divide?
        TokenType.SLASH_SLASH: 1200,  # Not in C
        TokenType.PERCENT: 1200,  # TODO(dchu): Is this same semantics as in C?
        TokenType.PLUS: 1100,
        TokenType.MINUS: 1100,
        TokenType.LSHIFT: 1000,
        TokenType.RSHIFT: 1000,
        TokenType.AMPERSAND: 900,  # In C, this is lower than comparison ops
        TokenType.CIRCUMFLEX: 800,  # In C, this is lower than comparison ops
        TokenType.VBAR: 700,  # In C, this is lower than comparison ops
        TokenType.COLON: 600,  # Not in C
        TokenType.LESSER: 500,
        TokenType.LESSER_EQUAL: 500,
        TokenType.GREATER: 500,
        TokenType.GREATER_EQUAL: 500,
        TokenType.EQUAL_EQUAL: 500,  # In C, this is lower than other comparison ops
        TokenType.NOT_EQUAL: 500,  # In C, this is lower than other comparison ops
        # The '&&'/'and' operator is 400
        # The '||'/'or' operator is 300
        TokenType.EQUAL: 200,
        TokenType.COMMA: 100,  # Weakest
    }
    return precedence.get(op.type(), -1)


def parse_expr(stream: TokenStream) -> ASTNode:
    lhs = parse_primary(stream)
    assert lhs is not None
    return parse_binop_rhs(stream, 0, lhs)


def parse_binop_rhs(
    stream: TokenStream, min_expression_precedence: int, lhs: ASTNode
) -> ASTNode:
    """
    Inputs
    ------

    * min_expression_precedence: int - min operator precedence that function is
                                        allowed to eat.
    """
    while True:
        binop_token = stream.get_token()
        binop_token_precedence = get_binop_precedence(binop_token)

        # Exit if the token has a lower precedence than what we're allowed to
        # consume. This could be for a variety of reasons: if we pass an invalid
        # binop, if the token is None (representing the end of the stream), or
        # if it is a binop with too low precedence.
        if binop_token_precedence < min_expression_precedence:
            return lhs

        stream.next_token()
        rhs = parse_primary(stream)
        assert rhs

        # TODO(dchu): I have no idea what this is actually doing. I just copied
        # it from https://llvm.org/docs/tutorial/MyFirstLanguageFrontend/LangImpl02.html
        token = stream.get_token()
        next_prec = get_binop_precedence(token)
        if binop_token_precedence < next_prec:
            rhs = parse_binop_rhs(stream, binop_token_precedence + 1, rhs)
            assert rhs

        binop = OperatorLeaf(binop_token)
        lhs = BinOpNode(binop, lhs, rhs)


def parse_function_prototype(stream: TokenStream) -> FunctionPrototypeNode:
    """Parse function definition."""
    eat_token(stream, TokenType.FUNCTION)

    # TODO(dchu): Optional for anonymous functions.
    name = eat_token(stream, TokenType.IDENTIFIER)
    name = IdentifierLeaf(name)

    # TODO(dchu): add generics parsing here!
    pass

    # Parameters
    eat_token(stream, TokenType.LPAREN)
    args = []
    while True:
        token = stream.get_token()
        if token.type() == TokenType.IDENTIFIER:
            # NOTE: we explicitly accept only an identifier. Refactor this out
            # because we'll use this in the 'let' statements and 'namespace'
            # statements too!
            lhs = IdentifierLeaf(token)
            stream.next_token()
            comma_precedence = get_binop_precedence(
                Token(-1, -1, -1, TokenType.COMMA, ",")
            )
            expr = parse_binop_rhs(stream, comma_precedence + 1, lhs)
            args.append(expr)
        elif token.type() == TokenType.COMMA:
            eat_token(stream, TokenType.COMMA)
            continue
        elif token.type() == TokenType.RPAREN:
            eat_token(stream, TokenType.RPAREN)
            break
        else:
            print_parser_error(
                stream.get_text(), stream.get_token(), error_msg=f"error!"
            )
            raise ValueError(f"unexpected token type: {repr(token)}")

    # Return type
    eat_token(stream, TokenType.ARROW)
    # TODO(dchu): enable compound types, e.g. Int[0:255]
    ret = eat_token(stream, TokenType.IDENTIFIER)
    ret = IdentifierLeaf(ret)
    return FunctionPrototypeNode(name, args, ret)


def parse_function_def(stream: TokenStream) -> FunctionDefNode:
    proto = parse_function_prototype(stream)
    eat_token(stream, TokenType.LBRACE)

    # Parse body
    # TODO(dchu): figure out what to do here. https://llvm.org/docs/tutorial/MyFirstLanguageFrontend/LangImpl02.html
    body = []
    while True:
        if stream.get_token().type() == TokenType.RBRACE:
            break
        body.append(parse_statement(stream))
    eat_token(stream, TokenType.RBRACE)

    return FunctionDefNode(proto, body)


def parse_let(stream: TokenStream) -> ASTNode:
    """Parse 'let' statement outside of a function."""
    eat_token(stream, TokenType.LET)
    return LetNode(parse_statement(stream))


def parse_namespace(stream: TokenStream) -> ASTNode:
    """Parse 'namespace' statement outside of a function."""
    eat_token(stream, TokenType.NAMESPACE)
    return NamespaceNode(parse_statement(stream))


def parse_statement(stream: TokenStream) -> ASTNode:
    token = stream.get_token()
    if token.type() == TokenType.LET:
        eat_token(stream, TokenType.LET)
        result = parse_expr(stream)
        eat_token(stream, TokenType.SEMICOLON)
        return LetNode(result)
    elif token.type() == TokenType.RETURN:
        eat_token(stream, TokenType.RETURN)
        result = parse_expr(stream)
        eat_token(stream, TokenType.SEMICOLON)
        return ReturnNode(result)
    # TODO(dchu): if, while, for loops
    else:
        result = parse_expr(stream)
        eat_token(stream, TokenType.SEMICOLON)
        return result


def parse(stream: TokenStream) -> List[ASTNode]:
    result = []
    while stream.get_token() is not None:
        token = stream.get_token()
        if token.type() == TokenType.FUNCTION:
            result.append(parse_function_def(stream))
        elif token.type() == TokenType.NAMESPACE:
            result.append(parse_namespace(stream))
        elif token.type() == TokenType.LET:
            result.append(parse_let(stream))
        else:
            raise ValueError(f"Unexpected token: {token}")
    return result


if __name__ == "__main__":
    with open("prototype/examples/fibonacci.lol") as f:
        text = f.read()
    tokens = tokenize(text=text)
    stream = TokenStream(tokens, text=text)
    ast = parse(stream)
    import json

    for a in ast:
        print(json.dumps(a.to_dict(), indent=4))
