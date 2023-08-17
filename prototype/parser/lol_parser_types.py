from abc import ABCMeta, abstractmethod
from enum import Enum, auto, unique
from typing import List, Tuple, Union

from lexer.lol_lexer import Token


@unique
class OperatorType(Enum):
    UNARY_PREFIX = auto()
    UNARY_POSTFIX = auto()
    BINARY_INFIX = auto()


################################################################################
### AST ABSTRACT CLASSES
################################################################################
# Might have to be an Abstract Base Class?
class ASTNode(metaclass=ABCMeta):
    @abstractmethod
    def to_dict(self):
        raise NotImplementedError("abc")

    def __repr__(self) -> str:
        return repr(self.to_dict())


class Expression(ASTNode, metaclass=ABCMeta):
    pass


class ValueExpression(Expression, metaclass=ABCMeta):
    pass


class TypeExpression(Expression, metaclass=ABCMeta):
    pass


class ASTLeaf(ASTNode, metaclass=ABCMeta):
    def __init__(self, token: Token):
        self.token = token


class Literal(ASTLeaf, ValueExpression, metaclass=ABCMeta):
    """The literals.

    N.B. Type expressions cannot contain literals yet. Eventually, they should
    be able to, e.g. `x: int[100]`.
    """

    def __init__(self, token: Token):
        super().__init__(token)
        self.value = None


################################################################################
### OPERATOR LITERAL
################################################################################
class OperatorLiteral(ASTLeaf):
    """An operator, such as '+'."""

    def __init__(self, token: Token, operator_type: OperatorType):
        super().__init__(token)
        self._operator_type = operator_type

    def get_operator_type_as_str(self):
        return self._operator_type.name

    def to_dict(self):
        return dict(
            type=self.__class__.__name__,
            operator=self.token.lexeme,
            operator_type=self._operator_type.name,
        )


################################################################################
### OPERATOR NODES
################################################################################
class OperatorValueExpression(ValueExpression):
    """
    Operator expressions containing a value (as opposed to a type).

    E.g. `10 + 10` vs `int[100]`

    The position of the operand is important if it has differing semantics
    between positions. E.g. prefix and postfix operators: ++x` vs `x++`.
    """

    def __init__(
        self,
        operator: OperatorLiteral,
        *operands: ValueExpression,  # i.e. each argument is a ValueExpression
    ):
        self._operator = operator
        self._operands = operands

    def get_operator_as_str(self) -> str:
        return self._operator.token.lexeme

    def get_operator_type_as_str(self) -> str:
        return self._operator.get_operator_type_as_str()

    def get_operands(self) -> Tuple[ValueExpression]:
        return self._operands

    def to_dict(self):
        return dict(
            type=self.__class__.__name__,
            operator=self._operator.to_dict(),
            operands=[x.to_dict() for x in self._operands],
        )


################################################################################
### TYPE OPERATOR NODES
################################################################################
class OperatorTypeExpression(TypeExpression):
    """
    Operator expressions containing a type (as opposed to a value).

    E.g. `int[100]` vs `10 + 10`

    The position of the operand is important if it has differing semantics
    between positions. E.g. prefix and postfix operators: ++x` vs `x++`.
    """

    def __init__(
        self,
        operator: OperatorLiteral,
        *operands: TypeExpression,
        operator_type: OperatorType = None,  # May be unspecified for binary ops
    ):
        self._operator = operator
        self._operands = operands

    def to_dict(self):
        return dict(
            type=self.__class__.__name__,
            operator=self._operator.to_dict(),
            operands=[x.to_dict() for x in self._operands],
        )


################################################################################
### LITERALS
################################################################################
class DecimalLiteral(Literal):
    def __init__(self, token: Token):
        super().__init__(token)
        self.value = int(token.lexeme)

    def to_dict(self):
        return dict(type=__class__.__name__, value=self.value)


class StringLiteral(Literal):
    def __init__(self, token: Token):
        super().__init__(token)
        # TODO(dchu): Parse string such that "hello, world\n" has the characters
        # TODO(dchu): suitably replaced.
        self.value = token.lexeme[1:-1]  # String surrounding quotations

    def to_dict(self):
        return dict(type=self.__class__.__name__, value=self.value)


class Identifier(ASTLeaf, TypeExpression):
    def __init__(self, token: Token):
        super().__init__(token)

    def to_dict(self):
        return dict(type=self.__class__.__name__, name=self.token.lexeme)


################################################################################
### VARIABLE NODES
################################################################################
class VariableNode(ASTNode, metaclass=ABCMeta):
    pass


class VariableDefinitionNode(VariableNode):
    def __init__(
        self,
        name: Identifier,
        data_type: TypeExpression,
        value: Union[ValueExpression, None],
    ):
        self._name = name
        self._data_type = data_type
        self._value = value

    def get_name_as_str(self):
        return self._name.token.lexeme

    def get_data_type(self):
        return self._data_type

    def get_value(self):
        return self._value

    def to_dict(self):
        to_dict_or_none = lambda x: x.to_dict() if x is not None else None
        return dict(
            type=self.__class__.__name__,
            name=self._name.to_dict(),
            data_type=to_dict_or_none(self._data_type),
            value=to_dict_or_none(self._value),
        )


class VariableModificationNode(VariableNode):
    def __init__(
        self,
        name: Identifier,
        value: Union[ValueExpression, None],
    ):
        self._name = name
        self._value = value

    def get_name(self):
        return self._name

    def get_value(self):
        return self._value

    def to_dict(self):
        to_dict_or_none = lambda x: x.to_dict() if x is not None else None
        return dict(
            type=self.__class__.__name__,
            name=self._name.to_dict(),
            value=to_dict_or_none(self._value),
        )


class VariableCallNode(VariableNode, ValueExpression):
    """Use this when the value of the identifier is being used."""

    def __init__(self, name: Identifier):
        self._name = name

    def get_name_as_str(self):
        return self._name.token.lexeme

    def to_dict(self):
        return dict(
            type=self.__class__.__name__,
            name=self._name.to_dict(),
        )


################################################################################
### VARIABLE NODES
################################################################################
class FunctionNode(ASTNode, metaclass=ABCMeta):
    pass


class FunctionDefinitionNode(FunctionNode):
    def __init__(
        self,
        name: Identifier,
        parameters: List[VariableDefinitionNode],
        return_type: TypeExpression,
        body: List[ASTNode],
    ):
        self._name = name
        self._parameters = parameters
        self._return_type = return_type
        self._body = body

    def get_name_as_str(self):
        return self._name.token.lexeme

    def get_parameters(self):
        return self._parameters

    def get_return_type(self):
        return self._return_type

    def to_dict(self):
        return dict(
            type=self.__class__.__name__,
            name=self._name.to_dict(),
            parameters=[p.to_dict() for p in self._parameters],
            return_type=self._return_type.to_dict(),
            body=[b.to_dict() for b in self._body],
        )


class FunctionCallNode(FunctionNode, ValueExpression):
    # Include generics in function call?
    def __init__(self, name: Identifier, arguments: List[ValueExpression]):
        self._name = name
        self._arguments = arguments

    def get_name_as_str(self):
        return self._name.token.lexeme

    def get_arguments(self):
        return self._arguments

    def to_dict(self):
        return dict(
            type=self.__class__.__name__,
            name=self._name.to_dict(),
            arguments=[a.to_dict() for a in self._arguments],
        )


################################################################################
### IMPORT MODULE NODES
################################################################################
class ImportModuleNode(ASTNode):
    def __init__(self, name: Identifier, library: StringLiteral) -> None:
        super().__init__()
        self._name = name
        self._library = library

    def get_name_as_str(self):
        return self._name.token.lexeme

    def get_library_as_str(self):
        # N.B. this may be a raw string value. Injection attacks? Or just plain
        # ugly messes.
        return self._library.value

    def to_dict(self):
        return dict(
            type=self.__class__.__name__,
            name=self._name.to_dict(),
            expression=self._library.to_dict(),
        )


################################################################################
### FUNCTION BODY NODES
################################################################################
# TODO(dchu): if-else, while, for, etc.


class ReturnNode(ASTNode):
    def __init__(self, expression: ValueExpression) -> None:
        super().__init__()
        self._expression = expression

    def to_dict(self):
        return dict(
            type=self.__class__.__name__,
            expression=self._expression.to_dict(),
        )
