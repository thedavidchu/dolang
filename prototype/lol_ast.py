from typing import List


from lol_lexer import Token


# Might have to be an Abstract Base Class?
class ASTNode:
    pass



class BinOpNode(ASTNode):
    def __init__(self, lhs: Union[ASTNode, Token], op: Token, rhs: Union[ASTNode, Token]):
        self.lhs = lhs
        self.op = op
        self.rhs = rhs


class FunctionDefNode(ASTNode):
    def __init__(self, name, generics, parameters, body):
        self.name = name
        self.generics = generics
        self.parameters = parameters
        self.body = body


class FunctionCallNode(ASTNode):
    # Include generics in function call?
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments


if __name__ == "__main__":
    pass
