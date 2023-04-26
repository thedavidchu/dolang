from abc import ABCMeta, abstractmethod
from typing import List

from lol_lexer import Token

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


class FunctionPrototypeNode(ASTNode):
    def __init__(
        self,
        name: IdentifierLeaf,
        parameters: List[ASTNode],
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
    def __init__(self, name: IdentifierLeaf, arguments: List[ASTNode]):
        self.name = name
        self.arguments = arguments

    def to_dict(self):
        return dict(
            type=self.__class__.__name__,
            name=self.name.to_dict(),
            arguments=[a.to_dict() for a in self.arguments],
        )


class LetNode(ASTNode):
    def __init__(self, expression: ASTNode) -> None:
        super().__init__()
        self.expression = expression

    def to_dict(self):
        return dict(
            type=self.__class__.__name__,
            expression=self.expression.to_dict(),
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


class NamespaceNode(ASTNode):
    def __init__(self, expression: ASTNode) -> None:
        super().__init__()
        self.expression = expression

    def to_dict(self):
        return dict(
            type=self.__class__.__name__,
            expression=self.expression.to_dict(),
        )
