from abc import ABCMeta, abstractmethod
from typing import List, Union
from warnings import warn

from lexer.lol_lexer import Token

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


class ASTLeaf(ASTNode, metaclass=ABCMeta):
    def __init__(self, token: Token):
        self.token = token


class LiteralLeaf(ASTLeaf, metaclass=ABCMeta):
    def __init__(self, token: Token):
        super().__init__(token)
        self.value = None

################################################################################
### AST LEAFS
################################################################################


class DecimalLeaf(LiteralLeaf):
    def __init__(self, token: Token):
        super().__init__(token)
        self.value = int(token.lexeme)

    def to_dict(self):
        return dict(type=__class__.__name__, value=self.value)


class StringLeaf(LiteralLeaf):
    def __init__(self, token: Token):
        super().__init__(token)
        self.value = token.lexeme[1:-1]  # String surrounding quotations

    def to_dict(self):
        return dict(type=self.__class__.__name__, value=self.value)


class IdentifierLeaf(ASTLeaf):
    def __init__(self, token: Token):
        super().__init__(token)

    def to_dict(self):
        return dict(type=self.__class__.__name__, identifier=self.token.lexeme)


class OperatorLeaf(ASTLeaf):
    """An operator, such as '+'."""

    def __init__(self, token: Token):
        super().__init__(token)

    def to_dict(self):
        return dict(type=self.__class__.__name__, op=self.token.lexeme)


################################################################################
### AST NODES
################################################################################

class BinOpNode(ASTNode):
    """A binary op with a lhs and rhs."""

    def __init__(self, op: OperatorLeaf, lhs: ASTNode, rhs: ASTNode):
        self.op = op
        self.lhs = lhs
        self.rhs = rhs

    def to_dict(self):
        return dict(
            type=self.__class__.__name__,
            op=self.op.to_dict(),
            lhs=self.lhs.to_dict(),
            rhs=self.rhs.to_dict(),
        )


# NOTE: we don't really need this class; it could be replaced by a more general
# expression node; however, specializing early helps keep the code cleaner in
# later stages.
class DefinitionNode(ASTNode):
    def __init__(
        self,
        identifier: IdentifierLeaf,
        type: Union[ASTNode, None],
        value: Union[ASTNode, None],
    ):
        self._identifier = identifier
        self._type = type
        self._value = value

    def get_identifier(self):
        return self._identifier

    def get_type(self):
        return self._type

    def get_value(self):
        return self._value

    def to_dict(self):
        to_dict_or_none = lambda x: x.to_dict() if x is not None else None
        return dict(
            type=self.__class__.__name__,
            identifier=self._identifier.to_dict(),
            type_annotation=to_dict_or_none(self._type),
            value=to_dict_or_none(self._value),
        )

# NOTE: I thought about wrapping this into the FunctionDefNode, but it is nice
# to have separate prototypes, because external C functions may only be known by
# their prototypes.
class FunctionPrototypeNode(ASTNode):
    def __init__(
        self,
        name: IdentifierLeaf,
        parameters: List[DefinitionNode],
        return_type: ASTNode,
    ):
        self.name = name
        self.parameters = parameters
        self.return_type = return_type

    def to_dict(self):
        return dict(
            type=self.__class__.__name__,
            name=self.name.to_dict(),
            parameters=[p.to_dict() for p in self.parameters],
            return_type=self.return_type.to_dict(),
        )


class FunctionDefNode(ASTNode):
    def __init__(self, prototype: FunctionPrototypeNode, body: List[ASTNode]):
        self.prototype = prototype
        self.body = body

    def to_dict(self):
        return dict(
            type=self.__class__.__name__,
            prototype=self.prototype.to_dict(),
            body=[b.to_dict() for b in self.body],
        )


class FunctionCallNode(ASTNode):
    # Include generics in function call?
    def __init__(self, identifier: IdentifierLeaf, arguments: List[ASTNode]):
        self.identifier = identifier
        self.arguments = arguments

    def to_dict(self):
        return dict(
            type=self.__class__.__name__,
            name=self.identifier.to_dict(),
            arguments=[a.to_dict() for a in self.arguments],
        )


class ReturnNode(ASTNode):
    def __init__(self, expression: ASTNode) -> None:
        super().__init__()
        self.expression = expression

    def to_dict(self):
        return dict(
            type=self.__class__.__name__,
            expression=self.expression.to_dict(),
        )


class ImportNode(ASTNode):
    def __init__(self, name: IdentifierLeaf, expression: ASTNode) -> None:
        super().__init__()
        self.name = name
        self.expression = expression

    def to_dict(self):
        return dict(
            type=self.__class__.__name__,
            expression=self.expression.to_dict(),
        )
