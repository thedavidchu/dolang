from typing import Any, Dict, Tuple, List, Optional, Union
from enum import Enum, auto, unique

from compiler.parser.lol_parser import (
    ASTNode,
    FunctionDefinitionNode,
    ImportModuleNode,
    VariableDefinitionNode,
)
import compiler.parser.lol_parser_types as parser_types
import compiler.lexer.lol_lexer_types as lexer_types


################################################################################
### LOL ANALYSIS INTERMEDIATE REPRESENTATION
################################################################################
LolIRExpression = Union["LolIRFunctionCallExpression", "LolIROperatorExpression", "LolIRLiteralExpression", "LolAnalysisVariable"]
LolIRStatement = Union["LolIRDefinitionStatement", "LolIRSetStatement", "LolIRFunctionCallStatement", "LolIRIfStatement", "LolIRReturnStatement"]


### Expressions
class LolIRFunctionCallExpression:
    def __init__(self, function: "LolAnalysisFunction", arguments: List["LolAnalysisVariable"]):
        self.function = function
        self.arguments = arguments


class LolIROperatorExpression:
    def __init__(self, op: str, operands: List["LolAnalysisVariable"]):
        self.op = op
        self.operands: List["LolAnalysisVariable"] = operands


class LolIRLiteralExpression:
    def __init__(self, literal: Any):
        self.literal = literal


### Statements
class LolIRDefinitionStatement:
    def __init__(self, name: str, type: "LolAnalysisDataType", value: LolIRExpression):
        self.name: str = name
        self.type: "LolAnalysisDataType" = type
        self.value = value


class LolIRSetStatement:
    def __init__(self, name: str, value: LolIRExpression):
        self.name = name
        self.value = value


class LolIRFunctionCallStatement:
    def __init__(self, func_call: LolIRFunctionCallExpression):
        self.func_call = func_call

class LolIRIfStatement:
    def __init__(self, if_cond: "LolAnalysisVariable", if_body: List[LolIRStatement], else_body: List[LolIRStatement]):
        self.if_cond = if_cond
        self.if_body = if_body
        self.else_body = else_body


class LolIRReturnStatement:
    def __init__(self, ret_var: "LolAnalysisVariable"):
        self.ret_var = ret_var


################################################################################
### LOL ANALYSIS TYPES
################################################################################
LolAnalysisDataType = Union["LolAnalysisBuiltinType"]
LolAnalysisSymbol = Union[LolAnalysisDataType, "LolAnalysisFunction", "LolAnalysisVariable"]


def optional_to_dict(obj: Any):
    if obj is None:
        return None
    else:
        return obj.to_dict()


def recursive_to_dict(obj: Optional[Dict[str, LolAnalysisSymbol]]):
    """This is like optional_names() but calls to_dict() on each value."""
    if obj is None:
        return None
    else:
        return {key: val.to_dict() for key, val in obj.items()}


def optional_names(obj: Optional[Dict[str, LolAnalysisSymbol]]):
    if obj is None:
        return None
    else:
        # assert isinstance(obj, Dict[str, LolAnalysisSymbol])
        return {key: val.name for key, val in obj.items()}


class LolAnalysisBuiltinType:
    def __init__(self, name: str, ops: Dict[str, "LolAnalysisBuiltinType"]):
        self.name = name
        self.ops = ops

    def to_dict(self):
        return dict(
            metatype=self.__class__.__name__,
            name=self.name,
            ops={op: dt.name for op, dt in self.ops.items()},
            id=id(self),
        )


def get_type(
    type_ast: parser_types.TypeExpression, module_symbol_table: Dict[str, LolAnalysisSymbol]
) -> LolAnalysisDataType:
    # TODO: Change this in when we support multi-token TypeExpressions
    assert isinstance(type_ast, parser_types.Identifier)
    type_token: lexer_types.Token = type_ast.token
    type_name: str = type_token.as_str()
    if type_name not in module_symbol_table:
        raise ValueError(f"module symbol table should contain name {type_name}")
    type_symbol: LolAnalysisDataType = module_symbol_table[type_name]
    # Python 3.10 should support this due to PIP 604
    # assert isinstance(type_symbol, LolAnalysisDataType)
    return type_symbol


class LolAnalysisVariable:
    def __init__(self, name: str, ast_definition_node: VariableDefinitionNode):
        self.name = name
        self.ast_definition_node = ast_definition_node

        self.type: Optional[LolAnalysisDataType] = None

    def complete_prototype(self, module_symbol_table: Dict[str, LolAnalysisSymbol]):
        assert self.type is None
        self.type = get_type(self.ast_definition_node.get_data_type(), module_symbol_table)

    def to_dict(self):
        return dict(
            metatype=self.__class__.__name__,
            name=self.name,
            type=optional_to_dict(self.type),
        )


class LolAnalysisFunction:
    def __init__(
        self,
        name: str,
        ast_definition_node: Optional[FunctionDefinitionNode],
        *,
        # Function Prototype
        return_types: Optional[LolAnalysisDataType] = None,
        parameter_types: Optional[List[LolAnalysisDataType]] = None,
        parameter_names: Optional[List[str]] = None,
        # Function Body
        symbol_table: Optional[Dict[str, LolAnalysisSymbol]] = None,
        body: Optional[List[LolIRStatement]] = None,
    ):
        self.name = name
        self.ast_definition_node = ast_definition_node

        self.return_types: Optional[LolAnalysisDataType] = return_types
        self.parameter_types: Optional[List[LolAnalysisDataType]] = parameter_types
        self.parameter_names: Optional[List[str]] = parameter_names

        self.symbol_table: Optional[Dict[str, LolAnalysisSymbol]] = symbol_table
        self.body: Optional[List[LolIRStatement]] = body

    def complete_prototype(self, module_symbol_table: Dict[str, LolAnalysisSymbol]):
        assert self.return_types is None
        assert self.parameter_types is None
        assert self.parameter_names is None
        self.return_types = get_type(self.ast_definition_node.get_return_type(), module_symbol_table)
        self.parameter_types = [
            get_type(t.get_data_type(), module_symbol_table) for t in self.ast_definition_node.get_parameters()
        ]
        self.parameter_names = [
            get_type(t.get_name_as_str(), module_symbol_table) for t in self.ast_definition_node.get_parameters()
        ]

    def _get_temporary_variable_name(self) -> str:
        # NOTE: this is a complete hack!
        if not hasattr(self, "tmp_cnt"):
            self.tmp_cnt = 0
        tmp = self.tmp_cnt
        self.tmp_cnt += 1
        return f"%{tmp}"

    def _get_symbol(self, module_symbol_table: Dict[str, LolAnalysisSymbol], name: str):
        split_names = name.split("::")
        first_name = split_names[0]

        if first_name in self.symbol_table:
            module = self.symbol_table
            for name in split_names[:-1]:
                module = module[name].module_symbol_table
            last_name = split_names[-1]
            print(module, last_name)
            return module[last_name]
        elif first_name in module_symbol_table:
            module = module_symbol_table
            for name in split_names[:-1]:
                module = module[name].module_symbol_table
            last_name = split_names[-1]
            print(module, last_name)
            return module[last_name]
        else:
            raise ValueError(f"symbol {first_name} not found in either module")

    def _parse_expression_recursively(self, x: parser_types.ASTNode, module_symbol_table: Dict[str, LolAnalysisSymbol]) -> str:
        if isinstance(x, parser_types.OperatorValueExpression):
            op_name: str = x.get_operator_as_str()
            operands: List["LolAnalysisVariable"] = [
                self._get_symbol(module_symbol_table, self._parse_expression_recursively(y))
                for y in x.get_operands()
            ]
            ret = self._get_temporary_variable_name()
            stmt = LolIRDefinitionStatement(ret, LolIROperatorExpression(op_name, operands))
            self.body.append(stmt)
            self.symbol_table[ret] = LolAnalysisVariable(ret, x)
            return ret
        elif isinstance(x, parser_types.Literal):
            if isinstance(x, parser_types.DecimalLiteral):
                ret = self._get_temporary_variable_name()
                stmt = LolIRDefinitionStatement(
                    ret, module_symbol_table["i32"], LolIRLiteralExpression(x.value)
                )
                self.body.append(stmt)
                self.symbol_table[ret] = LolAnalysisVariable(ret, x)
                return ret
            elif isinstance(x, parser_types.StringLiteral):
                ret = self._get_temporary_variable_name()
                stmt = LolIRDefinitionStatement(
                    ret, module_symbol_table["cstr"], LolIRLiteralExpression(x.value)
                )
                self.body.append(stmt)
                self.symbol_table[ret] = LolAnalysisVariable(ret, x)
                return ret
        elif isinstance(x, parser_types.FunctionCallNode):
            func_name: str = x.get_name_as_str()
            func: LolAnalysisFunction = self._get_symbol(module_symbol_table, func_name)
            assert isinstance(func, LolAnalysisFunction)
            args: List["LolAnalysisVariable"] = [
                self._get_symbol(
                    module_symbol_table,
                    self._parse_expression_recursively(y, module_symbol_table))
                for y in x.get_arguments()
            ]
            ret: str = self._get_temporary_variable_name()
            stmt = LolIRDefinitionStatement(
                ret, func.return_types, LolIRFunctionCallExpression(func, args)
            )
            self.body.append(stmt)
            self.symbol_table[ret] = LolAnalysisVariable(ret, x)
            return ret
        elif isinstance(x, parser_types.ReturnNode):
            ret = self._parse_expression_recursively(x.get_expression(), module_symbol_table)
            stmt = LolIRReturnStatement(self._get_symbol(module_symbol_table, ret))
            self.body.append(stmt)
        elif isinstance(x, parser_types.VariableCallNode):
            return x.get_name_as_str()
        else:
            raise NotImplementedError("")

    def complete_body(self, module_symbol_table: Dict[str, LolAnalysisSymbol]):
        assert self.symbol_table is None
        assert self.body is None
        self.symbol_table = {}
        self.body = []
        for statement in self.ast_definition_node.get_body():
            self._parse_expression_recursively(statement, module_symbol_table)

    def to_dict(self):
        return dict(
            metatype=self.__class__.__name__,
            name=self.name,
            return_types=None,
            parameter_types=None,
            parameter_names=self.parameter_names,
            symbol_table=optional_names(self.symbol_table),
            body="TODO",
        )


class LolAnalysisModule:
    def __init__(self, name: str, caller_module: Optional["LolAnalysisModule"] = None):
        self.name = name
        self.intermediate_repr: List[Any] = []
        self.module_symbol_table: Dict[str, LolAnalysisSymbol] = {}

        self.add_builtin_types(caller_module)

    def add_to_module_symbol_table(self, name, symbol):
        if name in self.module_symbol_table:
            raise ValueError(f"name {name} already in module symbol table")
        self.module_symbol_table[name] = symbol

    def add_builtin_types(self, caller_module: Optional["LolAnalysisModule"]):
        if caller_module is None:
            i32 = LolAnalysisBuiltinType("i32", {})
            i32.ops["+"] = i32
            i32.ops["-"] = i32
            i32.ops["*"] = i32
            i32.ops["/"] = i32
            cstr = LolAnalysisBuiltinType("cstr", {})
            void = LolAnalysisBuiltinType("void", {})
        else:
            # We want all of the built-in objects to be identical objects with
            # even the pointers matching (so module_a's i32 is module_b's i32)
            i32 = caller_module.module_symbol_table["i32"]
            cstr = caller_module.module_symbol_table["cstr"]
            void = caller_module.module_symbol_table["void"]
        self.add_to_module_symbol_table("i32", i32)
        self.add_to_module_symbol_table("cstr", cstr)
        self.add_to_module_symbol_table("void", void)

    def to_dict(self):
        # NOTE: This could end up in an infinite loop of recursion if we
        # have circular imports; however, it is useful to see the verbose
        # printing of modules, especially leaf modules.
        return dict(
            metatype=self.__class__.__name__,
            name=self.name,
            module_symbol_table=recursive_to_dict(self.module_symbol_table),
        )

    ### NAME
    def _add_function_name(self, ast_definition: FunctionDefinitionNode):
        name = ast_definition.get_name_as_str()
        symbol = LolAnalysisFunction(name, ast_definition)
        self.add_to_module_symbol_table(name, symbol)

    def _add_variable_name(self, ast_definition: VariableDefinitionNode):
        name = ast_definition.get_name_as_str()
        symbol = LolAnalysisVariable(name, ast_definition)
        self.add_to_module_symbol_table(name, symbol)

    # TODO: merge this into the variable!
    def _add_import_name(self, ast_definition: ImportModuleNode):
        name = ast_definition.get_name_as_str()
        library = ast_definition.get_library_as_str()
        if library == "stdio.h":
            symbol = LolAnalysisModule(library, caller_module=self)
            i32: LolAnalysisBuiltinType = self.module_symbol_table["i32"]
            cstr: LolAnalysisBuiltinType = self.module_symbol_table["cstr"]
            printf_func = LolAnalysisFunction(
                "printf",
                None,
                return_types=i32,
                parameter_types=[cstr],
                parameter_names=["format"],
            )
            symbol.add_to_module_symbol_table("printf", printf_func)
        else:
            raise NotImplementedError("only stdio.h library is supported!")
        self.add_to_module_symbol_table(name, symbol)

    def get_module_names(self, ast_nodes: List[ASTNode]):
        """
        Extract names (only) of function definitions, module definitions, and
        imports.

        TODO
        ----
        1. Add struct/enum/monad
        """
        for i, node in enumerate(ast_nodes):
            if isinstance(node, FunctionDefinitionNode):
                self._add_function_name(node)
            elif isinstance(node, VariableDefinitionNode):
                self._add_variable_name(node)
            elif isinstance(node, ImportModuleNode):
                # TODO(dchu) - recursively add members to this submodule!
                self._add_import_name(node)
            # TODO(dchu): accept data structures
            else:
                # We will ignore anything outside of functions! This is an error
                raise ValueError(f"{node} cannot be outside of functions!")

    ### PROTOTYPES
    def add_function_prototype(self, ast_definition: FunctionDefinitionNode):
        name = ast_definition.get_name_as_str()
        func: LolAnalysisFunction = self.module_symbol_table[name]
        func.complete_prototype(self.module_symbol_table)

    def add_variable_prototype(self, ast_definition: VariableDefinitionNode):
        name = ast_definition.get_name_as_str()
        var: LolAnalysisVariable = self.module_symbol_table[name]
        var.complete_prototype(self.module_symbol_table)

    def add_import_prototype(self, ast_definition: ImportModuleNode):
        # Intentionally do nothing
        pass

    def get_module_prototypes(self, ast_nodes: List[ASTNode]):
        """Get function and variable prototypes."""
        for i, node in enumerate(ast_nodes):
            if isinstance(node, FunctionDefinitionNode):
                self.add_function_prototype(node)
            elif isinstance(node, VariableDefinitionNode):
                self.add_variable_prototype(node)
            elif isinstance(node, ImportModuleNode):
                self.add_import_prototype(node)
            else:
                # We will ignore anything outside of functions! This is an error
                raise ValueError(f"{node} cannot be outside of functions!")

    ### BODIES
    def add_function_body(self, ast_definition: FunctionDefinitionNode):
        name = ast_definition.get_name_as_str()
        func: LolAnalysisFunction = self.module_symbol_table[name]
        func.complete_body(self.module_symbol_table)

    def add_variable_body(self, ast_definition: VariableDefinitionNode):
        # Intentionally do nothing
        pass

    def add_import_body(self, ast_definition: ImportModuleNode):
        # Intentionally do nothing
        pass

    def get_module_bodies(self, ast_nodes: List[ASTNode]):
        for i, node in enumerate(ast_nodes):
            if isinstance(node, FunctionDefinitionNode):
                self.add_function_body(node)
            elif isinstance(node, VariableDefinitionNode):
                self.add_variable_body(node)
            elif isinstance(node, ImportModuleNode):
                self.add_import_body(node)
            else:
                # We will ignore anything outside of functions! This is an error
                raise ValueError(f"{node} cannot be outside of functions!")


def analyze(asts: List[ASTNode], raw_text: str) -> LolAnalysisModule:
    module = LolAnalysisModule("main")
    module.get_module_names(asts)
    module.get_module_prototypes(asts)
    module.get_module_bodies(asts)
    print(module.to_dict())

    return module
