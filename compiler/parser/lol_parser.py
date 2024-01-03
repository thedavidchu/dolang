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
from typing import List, Set, Union

from compiler.lexer.lol_lexer import Token, TokenType
from compiler.parser.lol_parser_token_stream import TokenStream
from compiler.parser.lol_parser_types import (
    OperatorType,
    # AST Nodes
    ASTNode,
    # Literals and Identifiers
    Literal,  # Abstract data type
    DecimalLiteral,
    StringLiteral,
    OperatorLiteral,
    Identifier,
    # Value Expressions
    Expression,  # Abstract data type
    ValueExpression,
    OperatorValueExpression,
    # Type Expressions
    TypeExpression,
    OperatorTypeExpression,
    # Functions
    FunctionNode,
    FunctionDefinitionNode,
    FunctionCallNode,
    # Variables
    VariableDefinitionNode,
    VariableModificationNode,
    VariableCallNode,
    # Imports
    ImportModuleNode,
    # Inner Function Expressions
    ReturnNode,
)
from compiler.error.lol_error import print_parser_error


LITERAL_TOKENS: Set[TokenType] = {TokenType.DEC, TokenType.STRING}
FUNCTION_STATEMENTS = Union[
    ValueExpression,
    TypeExpression,  # Only if we allow isolated type statements in
    # functions
    VariableDefinitionNode,
    VariableModificationNode,
    ReturnNode,
    FunctionDefinitionNode,  # Only if we allow function defintions within
    # other functions
    ImportModuleNode,  # Only if we allow module imports within functions
]


################################################################################
### HELPER FUNCTIONS
################################################################################
def eat_token(stream: TokenStream, expected_type: TokenType) -> Token:
    token = stream.get_token()
    if token.get_token_type() != expected_type:
        error_msg = f"expected {expected_type.name}, got {token.get_token_type_as_str()}"
        print_parser_error(stream, error_msg)
        raise ValueError(error_msg)
    stream.next_token()
    return token


# TODO(dchu): refactor this to make it smarter. Also move the hard-coded
# precedence somewhere smarter.
def get_binop_precedence(op: Token) -> int:
    """Get the precedence of a binary operator."""
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
        # NOTE(dchu): I remove the ability to parse the '=' and ',' as operators since this would be confusing!
        # TokenType.EQUAL: 200,
        # TokenType.COMMA: 100,  # Weakest
    }
    return precedence.get(op.get_token_type(), -1)


################################################################################
### PARSE VALUE EXPRESSIONS
################################################################################
def parse_literal(stream: TokenStream) -> Literal:
    token = stream.get_token()
    if token.is_type(TokenType.STRING):
        stream.next_token()
        return StringLiteral(token)
    elif token.is_type(TokenType.DEC):
        stream.next_token()
        return DecimalLiteral(token)
    else:
        raise ValueError(f"unexpected token type: {repr(token)}")


def parse_parenthetic_expression(stream: TokenStream) -> ValueExpression:
    eat_token(stream, TokenType.LPAREN)  # Eat '('
    ret = parse_value_expression(stream)
    eat_token(stream, TokenType.RPAREN)  # Eat ')'
    return ret


def parse_func_call_args(
    stream: TokenStream, identifier_leaf: Identifier
) -> FunctionCallNode:
    eat_token(stream, TokenType.LPAREN)
    args = []
    token = stream.get_token()
    # Check if empty set of arguments
    if token.is_type(TokenType.RPAREN):
        eat_token(stream, TokenType.RPAREN)
        return FunctionCallNode(identifier_leaf, [])
    # At this point, we have at least one argument (or error)
    while True:
        expr = parse_value_expression(stream)
        args.append(expr)
        token = stream.get_token()
        if token.is_type(TokenType.RPAREN):
            eat_token(stream, TokenType.RPAREN)
            break
        elif token.is_type(TokenType.COMMA):
            eat_token(stream, TokenType.COMMA)
            continue
        else:
            print_parser_error(
                stream,
                error_msg=f"Expected COMMA or RPAREN, got {stream.get_token().get_token_type()}",
            )
            raise ValueError("Expected COMMA or RPAREN")
    return FunctionCallNode(identifier_leaf, args)


def parse_namespace(stream: TokenStream, identifier_leaf: Identifier) -> Identifier:
    namespaces = [identifier_leaf]
    while True:
        next_separator_token = stream.get_token()
        if next_separator_token.is_type(TokenType.COLON_COLON):
            eat_token(stream, TokenType.COLON_COLON)
            identifier_leaf = Identifier(eat_token(stream, TokenType.IDENTIFIER))
            namespaces.append(identifier_leaf)
        else:
            break
    hacky_token = Token("::".join(n.get_name_as_str() for n in namespaces), TokenType.IDENTIFIER)
    return Identifier(hacky_token)


def parse_identifier_or_call_or_access(
    stream: TokenStream,
) -> Union[Identifier, FunctionCallNode, OperatorValueExpression, VariableCallNode]:
    """
    Parse both variables and function calls.

    This is due to the semantics we do not know whether the identifier will be a
    variable name or a function call.

    In fact, this will handle any postfix unary operations. Postfix operators
    would have to be different than prefix operators, otherwise we would need to
    add backtracking into the parser. E.g. `x+ + x` would require backtracking.
    A unique operator, e.g. `x++ + x` would not.

    In the future, it may be an array thing too array[100].
    """
    id_token = eat_token(stream, TokenType.IDENTIFIER)
    identifier_leaf = Identifier(id_token)

    token = stream.get_token()
    if token.is_type(TokenType.COLON_COLON):
        identifier_leaf = parse_namespace(stream, identifier_leaf)

    token = stream.get_token()
    if token.is_type(TokenType.LPAREN):
        return parse_func_call_args(stream, identifier_leaf)
    elif token.is_type(TokenType.LSQB):
        raise ValueError("accesses not supported yet... i.e. `x[100]`")
    else:
        return VariableCallNode(identifier_leaf)


# TODO(dchu): figure out why this is called "primary"
def parse_primary(stream: TokenStream) -> ValueExpression:
    """Helper functions for parsing identifiers, literals, and parenthetic expressions."""
    token = stream.get_token()
    if token.is_type(TokenType.IDENTIFIER):
        return parse_identifier_or_call_or_access(stream)
    elif token.get_token_type() in LITERAL_TOKENS:
        return parse_literal(stream)
    elif token.is_type(TokenType.LPAREN):
        return parse_parenthetic_expression(stream)
    else:
        error_msg = f"unrecognized primary {token}"
        print_parser_error(stream, error_msg)
        raise ValueError(error_msg)


def parse_value_expression(stream: TokenStream) -> ValueExpression:
    lhs = parse_primary(stream)
    assert lhs is not None
    return parse_binop_rhs(stream, 0, lhs)


def parse_binop_rhs(
    stream: TokenStream, min_expression_precedence: int, lhs: ValueExpression
) -> ValueExpression:
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
        # binop (which is OK), if the token is None (representing the end of the
        # stream), or if it is a binop with too low precedence.
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

        binop = OperatorLiteral(binop_token, OperatorType.BINARY_INFIX)
        lhs = OperatorValueExpression(binop, lhs, rhs)


################################################################################
### PARSE VALUE EXPRESSIONS
################################################################################
def parse_type_expression(stream: TokenStream) -> TypeExpression:
    # TODO(dchu): enable compound types, e.g. Int[0:255]
    # Note: we only accept single-identifier expressions for types!
    data_type_token = eat_token(stream, TokenType.IDENTIFIER)
    data_type = Identifier(data_type_token)
    return data_type


################################################################################
### FUNCTION DEFINITION
################################################################################
def parse_statement_in_function_body(
    stream: TokenStream,
) -> FUNCTION_STATEMENTS:
    token = stream.get_token()
    if token.is_type(TokenType.LET):  # Local variable
        return parse_let_statement(stream)
    elif token.is_type(TokenType.RETURN):
        eat_token(stream, TokenType.RETURN)
        result = parse_value_expression(stream)
        eat_token(stream, TokenType.SEMICOLON)
        return ReturnNode(result)
    # TODO(dchu): if, while, for loops
    else:
        result = parse_value_expression(stream)
        eat_token(stream, TokenType.SEMICOLON)
        return result


def parse_function_definition(stream: TokenStream) -> FunctionDefinitionNode:
    """
    Parse function definition.

    E.g. `function func_name(param: type) {...}`
    """
    eat_token(stream, TokenType.FUNCTION)  # Eat 'function'
    # TODO(dchu): Optional for anonymous functions.
    name = eat_token(stream, TokenType.IDENTIFIER)  # Eat function name
    name = Identifier(name)
    # TODO(dchu): add generics parsing here!
    pass  # Eat generics

    # Parameters
    params = []
    eat_token(stream, TokenType.LPAREN)
    while True:
        token = stream.get_token()
        if token.is_type(TokenType.IDENTIFIER):
            params.append(parse_variable_definition(stream))
        else:
            # NOTE: this is somewhat redundant. It is only useful to check for a
            # ')' immediately after the opening '('; on all other iterations, it
            # servers no purpose.
            eat_token(stream, TokenType.RPAREN)
            break
        token = stream.get_token()
        if token.is_type(TokenType.COMMA):
            eat_token(stream, TokenType.COMMA)
            continue
        elif token.is_type(TokenType.RPAREN):
            eat_token(stream, TokenType.RPAREN)
            break
        else:
            print_parser_error(stream, error_msg=f"error!")
            raise ValueError(f"unexpected token type: {repr(token)}")

    # Return type. Supports single word type for now.
    eat_token(stream, TokenType.ARROW)
    ret_t = parse_type_expression(stream)

    # Eat '{'
    eat_token(stream, TokenType.LBRACE)

    # Parse body
    # TODO(dchu): figure out what to do here. https://llvm.org/docs/tutorial/MyFirstLanguageFrontend/LangImpl02.html
    body = []
    while True:
        if stream.get_token().is_type(TokenType.RBRACE):
            break
        statement = parse_statement_in_function_body(stream)
        body.append(statement)
    # Eat '}'
    eat_token(stream, TokenType.RBRACE)
    return FunctionDefinitionNode(name, params, ret_t, body)


def parse_variable_definition(stream: TokenStream) -> VariableDefinitionNode:
    """Parse "<identifier> [: <type>] [= <value>]" expression.

    E.g. `one_hundred: int = 100;`"""
    name_token = eat_token(stream, TokenType.IDENTIFIER)
    identifier = Identifier(name_token)
    data_type: TypeExpression = None
    value: ValueExpression = None
    if stream.get_token().is_type(TokenType.COLON):
        eat_token(stream, TokenType.COLON)
        data_type = parse_type_expression(stream)
    if stream.get_token().is_type(TokenType.EQUAL):
        eat_token(stream, TokenType.EQUAL)
        value = parse_value_expression(stream)
    return VariableDefinitionNode(identifier, data_type, value)


def parse_let_statement(stream: TokenStream) -> VariableDefinitionNode:
    """Parse 'let' statement either inside or outside of a function."""
    eat_token(stream, TokenType.LET)
    result = parse_variable_definition(stream)
    eat_token(stream, TokenType.SEMICOLON)
    return result


################################################################################
### IMPORT MODULE STATEMENT
################################################################################
def parse_module_import_statement(stream: TokenStream) -> ImportModuleNode:
    """
    Parse import statement outside of a function.

    E.g. `module io = import("stdio.h");`
    """
    # TODO(dchu): this is deprecated because eventually we will have namespaces
    # and let statements all be one thing.
    eat_token(stream, TokenType.MODULE)
    name = eat_token(stream, TokenType.IDENTIFIER)
    eat_token(stream, TokenType.EQUAL)
    eat_token(stream, TokenType.IMPORT)
    eat_token(stream, TokenType.LPAREN)
    library = eat_token(stream, TokenType.STRING)
    eat_token(stream, TokenType.RPAREN)
    eat_token(stream, TokenType.SEMICOLON)
    return ImportModuleNode(Identifier(name), StringLiteral(library))


def parse(stream: TokenStream) -> List[ASTNode]:
    result = []
    while stream.get_token() is not None:
        token = stream.get_token()
        if token.is_type(TokenType.FUNCTION):
            result.append(parse_function_definition(stream))
        elif token.is_type(TokenType.MODULE):
            result.append(parse_module_import_statement(stream))
        elif token.is_type(TokenType.LET):  # Global variable
            result.append(parse_let_statement(stream))
        else:
            raise ValueError(f"Unexpected token: {token}")
    return result
