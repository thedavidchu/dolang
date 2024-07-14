"""
# Parser

## Issues
- [ ] Parenthetic expressions are not necessarily evaluated before others (so if
they have side-effects, we have undefined behaviour)
"""

from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, fields
from enum import Enum, auto, unique
from typing import Any, List, Set, Tuple, Union

from compiler.lexer.lol_lexer_types import LolToken, LolTokenType
from compiler.parser.lol_parser_token_stream import TokenStream

frozen_dataclass = dataclass(frozen=True)
json_type = dict[str, list | dict | str | int | float | None]


################################################################################
### GENERIC
################################################################################


@unique
class LolParserOperatorType(Enum):
    UNARY_PREFIX = auto()
    UNARY_POSTFIX = auto()
    BINARY_INFIX = auto()


@unique
class LolParserLiteralType(Enum):
    INTEGER = auto()
    BOOLEAN = auto()
    STRING = auto()
    FLOAT = auto()


@frozen_dataclass
class LolParserGeneric:
    def to_dict(self):
        def recursive_to_dict(item: LolParserGeneric | Any) -> json_type:
            if isinstance(item, LolParserGeneric):
                # NOTE  We don't use the asdict() function because this
                #       recursively converts all values into a dict,
                #       which discards necessary type information.
                return dict(
                    metatype=item.__class__.__name__,
                ) | {
                    field.name: recursive_to_dict(getattr(item, field.name))
                    for field in fields(item)
                }
            elif isinstance(item, Enum):
                return item.name
            elif isinstance(item, list):
                return [recursive_to_dict(x) for x in item]
            else:
                return item

        r = recursive_to_dict(self)
        return r


################################################################################
### EXPRESSIONS, LEAVES, AND AMBIGUOUS (e.g. function calls)
################################################################################
LolParserValueExpression = Union[Any]
LolParserTypeExpression = Union[Any]
LolParserExpression = Union[LolParserValueExpression, LolParserTypeExpression]


@frozen_dataclass
class LolParserLiteral(LolParserGeneric):
    type: LolParserLiteralType
    value: Union[int, bool, float, str]


@frozen_dataclass
class LolParserIdentifier(LolParserGeneric):
    name: str


@frozen_dataclass
class LolParserOperatorExpression(LolParserGeneric):
    operator: str
    type: LolParserOperatorType
    operands: List[LolParserExpression]


@frozen_dataclass
class LolParserParameterDefinition(LolParserGeneric):
    name: LolParserIdentifier
    type: LolParserTypeExpression

    def get_name_as_str(self) -> str:
        return self.name.name


################################################################################
### AMBIGUOUS (can be both expression or statement)
################################################################################
@frozen_dataclass
class LolParserFunctionCall(LolParserGeneric):
    name: LolParserIdentifier
    arguments: List[LolParserExpression]

    def get_name_as_str(self):
        return self.name.name


@frozen_dataclass
class LolParserVariableDefinition(LolParserGeneric):
    name: LolParserIdentifier
    type: LolParserTypeExpression
    value: LolParserValueExpression

    def get_name_as_str(self) -> str:
        return self.name.name


################################################################################
### STATEMENTS
################################################################################
LolParserModuleLevelStatement = Union[Any]
LolParserFunctionLevelStatement = Union[Any]
LolParserStatement = Union[
    LolParserModuleLevelStatement, LolParserFunctionLevelStatement
]


@frozen_dataclass
class LolParserImportStatement(LolParserGeneric):
    metatype = "LolParserImportStatement"
    alias: LolParserIdentifier
    # This must be a string literal
    library_name: LolParserLiteral

    def __post_init__(self):
        assert self.library_name.type == LolParserLiteralType.STRING

    def get_alias_as_str(self) -> str:
        return self.alias.name

    def get_library_name_as_str(self) -> str:
        assert self.library_name.type == LolParserLiteralType.STRING
        return self.library_name.value


@frozen_dataclass
class LolParserFunctionDefinition(LolParserGeneric):
    name: LolParserIdentifier
    parameters: List[LolParserParameterDefinition]
    return_type: LolParserTypeExpression
    body: List[LolParserFunctionLevelStatement]

    def get_name_as_str(self) -> str:
        return self.name.name


@frozen_dataclass
class LolParserVariableModification(LolParserGeneric):
    name: LolParserIdentifier
    value: LolParserValueExpression


@frozen_dataclass
class LolParserIfStatement(LolParserGeneric):
    if_condition: LolParserValueExpression
    # NOTE These may only be inside a function.
    if_block: List[LolParserFunctionLevelStatement]
    else_block: List[LolParserFunctionLevelStatement]


@frozen_dataclass
class LolParserLoopStatement(LolParserGeneric):
    block: List[LolParserFunctionLevelStatement]


@frozen_dataclass
class LolParserBreakStatement(LolParserGeneric):
    pass


@frozen_dataclass
class LolParserReturnStatement(LolParserGeneric):
    value: LolParserValueExpression


################################################################################
### PARSER
################################################################################
LITERAL_TOKENS: Set[LolTokenType] = {LolTokenType.INTEGER, LolTokenType.STRING}


def eat_token(stream: TokenStream, expected_type: LolTokenType) -> LolToken:
    token = stream.get_token()
    if token.get_token_type() != expected_type:
        error_msg = f"expected {expected_type.name}, got {token.get_token_type_as_str()}"
        raise ValueError(error_msg)
    stream.next_token()
    return token


class Parser:
    def __init__(self):
        self.module_level_statements: List[LolParserModuleLevelStatement] = []

    @staticmethod
    def parse_literal(stream: TokenStream) -> LolParserLiteral:
        start_pos = stream.position
        token = stream.get_token()
        if token.is_type(LolTokenType.STRING):
            lit_type = LolParserLiteralType.STRING
            # Remove the surrounding quotations
            lit_value = token.as_str()[1:-1]
        elif token.is_type(LolTokenType.INTEGER):
            lit_type = LolParserLiteralType.INTEGER
            lit_value = int(token.as_str())
        else:
            raise ValueError(f"unexpected token type: {repr(token)}")
        stream.next_token()
        end_pos = stream.position
        return LolParserLiteral(lit_type, lit_value)

    @staticmethod
    def parse_parenthetic_expression(
        stream: TokenStream,
    ) -> LolParserExpression:
        eat_token(stream, LolTokenType.LPAREN)  # Eat '('
        ret = Parser.parse_expression(stream)
        eat_token(stream, LolTokenType.RPAREN)  # Eat ')'
        return ret

    @staticmethod
    def parse_func_call_args(
        stream: TokenStream, func_identifier: LolParserIdentifier
    ) -> LolParserFunctionCall:
        eat_token(stream, LolTokenType.LPAREN)
        args: List[LolParserValueExpression] = []
        token = stream.get_token()
        # Check if empty set of arguments
        if token.is_type(LolTokenType.RPAREN):
            eat_token(stream, LolTokenType.RPAREN)
            return LolParserFunctionCall(func_identifier, args)
        # At this point, we have at least one argument (or error)
        while True:
            expr = Parser.parse_value_expression(stream)
            args.append(expr)
            token = stream.get_token()
            if token.is_type(LolTokenType.RPAREN):
                eat_token(stream, LolTokenType.RPAREN)
                break
            elif token.is_type(LolTokenType.COMMA):
                eat_token(stream, LolTokenType.COMMA)
                continue
            else:
                raise ValueError("Expected COMMA or RPAREN")
        return LolParserFunctionCall(func_identifier, args)

    @staticmethod
    def parse_identifier_with_namespace_separator(
        stream: TokenStream, identifier_leaf: LolParserIdentifier
    ) -> LolParserIdentifier:
        namespaces: List[str] = [identifier_leaf.name]
        while True:
            next_separator_token = stream.get_token()
            if next_separator_token.is_type(LolTokenType.COLON_COLON):
                eat_token(stream, LolTokenType.COLON_COLON)
                identifier_name = eat_token(
                    stream, LolTokenType.IDENTIFIER
                ).as_str()
                namespaces.append(identifier_name)
            else:
                break
        hacky_identifier_str = "::".join(n for n in namespaces)
        return LolParserIdentifier(hacky_identifier_str)

    @staticmethod
    def parse_leading_identifier(
        stream: TokenStream,
    ) -> Union[
        LolParserIdentifier,
        LolParserFunctionCall,
        LolParserOperatorExpression,
        LolParserIdentifier,
    ]:
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
        id_token = eat_token(stream, LolTokenType.IDENTIFIER)
        identifier_leaf = LolParserIdentifier(id_token.as_str())

        token = stream.get_token()
        if token.is_type(LolTokenType.COLON_COLON):
            identifier_leaf = Parser.parse_identifier_with_namespace_separator(
                stream, identifier_leaf
            )
        token = stream.get_token()
        if token.is_type(LolTokenType.LPAREN):
            return Parser.parse_func_call_args(stream, identifier_leaf)
        elif token.is_type(LolTokenType.LSQB):
            raise ValueError("accesses not supported yet... i.e. `x[100]`")
        else:
            return LolParserIdentifier(identifier_leaf.name)

    @staticmethod
    def parse_if(stream: TokenStream) -> LolParserIfStatement:
        eat_token(stream, LolTokenType.IF)
        if_cond = Parser.parse_value_expression(stream)
        if_block = Parser.parse_block_body(stream)
        token = stream.get_token()
        else_block = []
        if token.is_type(LolTokenType.ELSE):
            eat_token(stream, LolTokenType.ELSE)
            else_block = Parser.parse_block_body(stream)
        return LolParserIfStatement(if_cond, if_block, else_block)

    @staticmethod
    def parse_primary(stream: TokenStream) -> LolParserExpression:
        token = stream.get_token()
        if token.is_type(LolTokenType.IDENTIFIER):
            return Parser.parse_leading_identifier(stream)
        elif token.get_token_type() in LITERAL_TOKENS:
            return Parser.parse_literal(stream)
        elif token.is_type(LolTokenType.LPAREN):
            return Parser.parse_parenthetic_expression(stream)
        else:
            error_msg = f"unrecognized primary {token}"
            raise ValueError(error_msg)

    @staticmethod
    # TODO(dchu): refactor this to make it smarter. Also move the hard-coded
    # precedence somewhere smarter.
    def get_binop_precedence(op: LolToken) -> int:
        """Get the precedence of a binary operator."""
        precedence = {
            # The '::' operator should always be on the left of any '.' operators,
            # so it has precedence due to left-associativity anyways.
            LolTokenType.COLON_COLON: 1500,  # Highest
            LolTokenType.DOT: 1400,
            LolTokenType.ARROW: 1400,
            # Prefix operators have precedence of 1300
            LolTokenType.STAR: 1200,
            LolTokenType.SLASH: 1200,  # TODO(dchu): Is this real divide?
            LolTokenType.SLASH_SLASH: 1200,  # Not in C
            LolTokenType.PERCENT: 1200,
            # TODO(dchu): Is this same semantics as in C?
            LolTokenType.PLUS: 1100,
            LolTokenType.MINUS: 1100,
            LolTokenType.LSHIFT: 1000,
            LolTokenType.RSHIFT: 1000,
            LolTokenType.AMPERSAND: 900,  # In C, this is lower than comparison ops
            LolTokenType.CIRCUMFLEX: 800,
            # In C, this is lower than comparison ops
            LolTokenType.VBAR: 700,  # In C, this is lower than comparison ops
            # TokenType.COLON: 600,  # Not in C
            LolTokenType.LESSER: 500,
            LolTokenType.LESSER_EQUAL: 500,
            LolTokenType.GREATER: 500,
            LolTokenType.GREATER_EQUAL: 500,
            LolTokenType.EQUAL_EQUAL: 500,
            # In C, this is lower than other comparison ops
            LolTokenType.NOT_EQUAL: 500,
            # In C, this is lower than other comparison ops
            LolTokenType.AND: 400,
            LolTokenType.OR: 300,
            # The '&&'/'and' operator is 400
            # The '||'/'or' operator is 300
            # NOTE(dchu): I remove the ability to parse the '=' and ',' as operators since this would be confusing!
            # TokenType.EQUAL: 200,
            # TokenType.COMMA: 100,  # Weakest
        }
        return precedence.get(op.get_token_type(), -1)

    @staticmethod
    def parse_binop_rhs(
        stream: TokenStream,
        min_expression_precedence: int,
        lhs: LolParserExpression,
    ) -> LolParserExpression:
        """
        Inputs
        ------

        * min_expression_precedence: int - min operator precedence that function is
                                            allowed to eat.
        """
        while True:
            binop_token = stream.get_token()
            binop_token_precedence = Parser.get_binop_precedence(binop_token)

            # Exit if the token has a lower precedence than what we're allowed to
            # consume. This could be for a variety of reasons: if we pass an invalid
            # binop (which is OK), if the token is None (representing the end of the
            # stream), or if it is a binop with too low precedence.
            if binop_token_precedence < min_expression_precedence:
                return lhs

            stream.next_token()
            rhs = Parser.parse_primary(stream)
            assert rhs

            # TODO(dchu): I have no idea what this is actually doing. I just copied
            # it from https://llvm.org/docs/tutorial/MyFirstLanguageFrontend/LangImpl02.html
            token = stream.get_token()
            next_prec = Parser.get_binop_precedence(token)
            if binop_token_precedence < next_prec:
                rhs = Parser.parse_binop_rhs(
                    stream, binop_token_precedence + 1, rhs
                )
                assert rhs

            lhs = LolParserOperatorExpression(
                binop_token.lexeme,
                LolParserOperatorType.BINARY_INFIX,
                [lhs, rhs],
            )

    @staticmethod
    def parse_expression(stream: TokenStream) -> LolParserExpression:
        """Helper functions for parsing identifiers, literals, and parenthetic expressions."""
        lhs = Parser.parse_primary(stream)
        assert lhs is not None
        return Parser.parse_binop_rhs(stream, 0, lhs)

    @staticmethod
    def parse_type_expression(stream: TokenStream) -> LolParserTypeExpression:
        # We only support single-token type expressions for now
        return LolParserIdentifier(
            eat_token(stream, LolTokenType.IDENTIFIER).as_str()
        )

    @staticmethod
    def parse_value_expression(stream: TokenStream) -> LolParserValueExpression:
        return Parser.parse_expression(stream)

    ############################################################################
    ### Functions
    ############################################################################
    @staticmethod
    def parse_parameter_definition(
        stream: TokenStream,
    ) -> LolParserParameterDefinition:
        start_pos = stream.position
        identifier = LolParserIdentifier(
            eat_token(stream, LolTokenType.IDENTIFIER).as_str()
        )
        eat_token(stream, LolTokenType.COLON)
        param_type = Parser.parse_type_expression(stream)
        end_pos = stream.position
        return LolParserParameterDefinition(identifier, param_type)

    @staticmethod
    def parse_function_prototype(
        stream: TokenStream,
    ) -> Tuple[
        LolParserIdentifier,
        List[LolParserParameterDefinition],
        LolParserTypeExpression,
    ]:
        _function = eat_token(stream, LolTokenType.FUNCTION)
        func_identifier = LolParserIdentifier(
            eat_token(stream, LolTokenType.IDENTIFIER).as_str()
        )
        eat_token(stream, LolTokenType.LPAREN)
        params: List[LolParserParameterDefinition] = []

        token = stream.get_token()
        if token.is_type(LolTokenType.RPAREN):
            eat_token(stream, LolTokenType.RPAREN)
        else:
            while True:
                params.append(Parser.parse_parameter_definition(stream))
                token = stream.get_token()
                if token.is_type(LolTokenType.COMMA):
                    eat_token(stream, LolTokenType.COMMA)
                elif token.is_type(LolTokenType.RPAREN):
                    eat_token(stream, LolTokenType.RPAREN)
                    break
                else:
                    raise ValueError(
                        f"expected comma or right parenthesis, got {token.as_str()}"
                    )
        eat_token(stream, LolTokenType.ARROW)
        ret_type = Parser.parse_type_expression(stream)
        return func_identifier, params, ret_type

    @staticmethod
    def parse_function_level_statement(
        stream: TokenStream,
    ) -> LolParserFunctionLevelStatement:
        token = stream.get_token()
        if token.is_type(LolTokenType.LET):  # Local variable
            return Parser.parse_variable_definition(stream)
        elif token.is_type(LolTokenType.RETURN):
            eat_token(stream, LolTokenType.RETURN)
            ret_val = Parser.parse_value_expression(stream)
            eat_token(stream, LolTokenType.SEMICOLON)
            return LolParserReturnStatement(ret_val)
        # TODO(dchu): if, while, for loops
        elif token.is_type(LolTokenType.IF):
            return Parser.parse_if(stream)
        else:
            result = Parser.parse_value_expression(stream)
            eat_token(stream, LolTokenType.SEMICOLON)
            return result

    @staticmethod
    def parse_block_body(
        stream: TokenStream,
    ) -> List[LolParserFunctionLevelStatement]:
        func_body: List[LolParserFunctionLevelStatement] = []
        eat_token(stream, LolTokenType.LBRACE)
        while True:
            func_body.append(Parser.parse_function_level_statement(stream))
            token = stream.get_token()
            if token.is_type(LolTokenType.RBRACE):
                break
        eat_token(stream, LolTokenType.RBRACE)
        return func_body

    @staticmethod
    def parse_function_definition(stream: TokenStream):
        start_pos = stream.position
        func_identifier, params, ret_type = Parser.parse_function_prototype(
            stream
        )
        func_body = Parser.parse_block_body(stream)
        end_pos = stream.position
        return LolParserFunctionDefinition(
            func_identifier, params, ret_type, func_body
        )

    ############################################################################
    ### VARIABLE DEFINITION
    ############################################################################
    @staticmethod
    def parse_variable_definition(
        stream: TokenStream,
    ):
        start_pos = stream.position
        _let = eat_token(stream, LolTokenType.LET)
        identifier = LolParserIdentifier(
            eat_token(stream, LolTokenType.IDENTIFIER).as_str()
        )
        eat_token(stream, LolTokenType.COLON)
        data_type = Parser.parse_type_expression(stream)
        eat_token(stream, LolTokenType.EQUAL)
        value = Parser.parse_value_expression(stream)
        eat_token(stream, LolTokenType.SEMICOLON)
        end_pos = stream.position
        return LolParserVariableDefinition(identifier, data_type, value)

    ############################################################################
    ### IMPORT
    ############################################################################
    @staticmethod
    def parse_import_module(
        stream: TokenStream,
    ) -> LolParserModuleLevelStatement:
        """
        Parse import statement outside of a function.

        E.g. `module io = import("stdio.h");`
        """
        # TODO(dchu): this is deprecated because eventually we will have
        #  namespaces and let statements all be one thing.
        start_pos = stream.position
        eat_token(stream, LolTokenType.MODULE)
        # NOTE: This only allows a single identifier for the module alias
        alias_name = eat_token(stream, LolTokenType.IDENTIFIER)
        eat_token(stream, LolTokenType.EQUAL)
        eat_token(stream, LolTokenType.IMPORT)
        eat_token(stream, LolTokenType.LPAREN)
        library_name = eat_token(stream, LolTokenType.STRING)
        eat_token(stream, LolTokenType.RPAREN)
        eat_token(stream, LolTokenType.SEMICOLON)
        end_pos = stream.position
        r = LolParserImportStatement(
            LolParserIdentifier(alias_name.as_str()),
            LolParserLiteral(
                LolParserLiteralType.STRING, library_name.as_str()
            ),
        )
        return r

    def parse_module_statements(
        self, stream: TokenStream
    ) -> List[LolParserStatement]:
        result = []
        token = stream.get_token()
        while token is not None:
            if token.is_type(LolTokenType.FUNCTION):
                result.append(Parser.parse_function_definition(stream))
            elif token.is_type(LolTokenType.MODULE):
                result.append(Parser.parse_import_module(stream))
            elif token.is_type(LolTokenType.LET):  # Global variable
                result.append(Parser.parse_variable_definition(stream))
            else:
                raise ValueError(f"Unexpected token: {token}")
            token = stream.get_token()
        self.module_level_statements = result
        return result


def parse(stream: TokenStream):
    parser = Parser()
    return parser.parse_module_statements(stream)
