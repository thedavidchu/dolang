from typing import Any, Dict, List, Optional, Union

import compiler.parser.lol_parser as parser_types
from compiler.parser.lol_parser import (
    # Generic
    LolParserLiteralType,

    # Generic Expressions
    LolParserTypeExpression,
    LolParserExpression,

    LolParserModuleLevelStatement,
    LolParserFunctionLevelStatement,

    # Specific Expressions
    LolParserIdentifier,
    LolParserLiteral,
    LolParserFunctionCall,
    LolParserOperatorExpression,

    LolParserImportStatement,
    LolParserVariableDefinition,
    LolParserParameterDefinition,
    LolParserVariableModification,
    LolParserFunctionDefinition,
    LolParserReturnStatement,
    LolParserIfStatement,
)

################################################################################
### LOL ANALYSIS INTERMEDIATE REPRESENTATION
################################################################################
LolIRExpression = Union["LolIRFunctionCallExpression", "LolIROperatorExpression", "LolIRLiteralExpression", "LolAnalysisVariable"]
LolIRStatement = Union["LolIRDefinitionStatement", "LolIRSetStatement", "LolIRFunctionCallStatement", "LolIRIfStatement", "LolIRReturnStatement"]


### Expressions
class LolIRFunctionCallExpression:
    def __init__(self, function: "LolAnalysisFunction", arguments: List["LolAnalysisVariable"]):
        assert isinstance(function, LolAnalysisFunction)
        assert isinstance(arguments, list)
        assert all(isinstance(arg, LolAnalysisVariable) for arg in arguments)
        self.function = function
        self.arguments = arguments

    def __str__(self):
        return f"{self.function.name}{tuple(arg.name for arg in self.arguments)}"


class LolIROperatorExpression:
    def __init__(self, op: str, operands: List["LolAnalysisVariable"]):
        assert isinstance(op, str)
        assert isinstance(operands, list)
        assert all(isinstance(operand, LolAnalysisVariable) for operand in operands)
        self.op = op
        self.operands: List["LolAnalysisVariable"] = operands

    def __str__(self):
        return f"{self.operands[0].name} {self.op} {self.operands[1].name}"


class LolIRLiteralExpression:
    def __init__(self, literal: Any):
        self.literal = literal

    def __str__(self):
        return f"{self.literal}"


### Statements
class LolIRDefinitionStatement:
    def __init__(self, name: str, type: "LolAnalysisDataType", value: LolIRExpression):
        assert isinstance(name, str)
        # TODO(dchu): This is true for now, but will have to be generalized in
        #  future to allow different types.
        assert isinstance(type, LolAnalysisBuiltinType)
        self.name: str = name
        self.type: "LolAnalysisDataType" = type
        self.value = value

    def __str__(self):
        return f"let {self.name}: {str(self.type)} = {str(self.value)};"


class LolIRSetStatement:
    def __init__(self, name: str, value: LolIRExpression):
        self.name = name
        self.value = value

    def __str__(self):
        return f"let {self.name} = {str(self.value)};"


class LolIRFunctionCallStatement:
    def __init__(self, func_call: LolIRFunctionCallExpression):
        self.func_call = func_call

    def __str__(self):
        return f"{str(self.func_call)};"


class LolIRIfStatement:
    def __init__(self, if_cond: "LolAnalysisVariable", if_body: List[LolIRStatement], else_body: List[LolIRStatement]):
        self.if_cond = if_cond
        self.if_body = if_body
        self.else_body = else_body

    def __str__(self):
        return f"if ({str(self.if_cond)}) {{...}} else {{...}}"


class LolIRReturnStatement:
    def __init__(self, ret_var: "LolAnalysisVariable"):
        self.ret_var = ret_var

    def __repr__(self):
        return f"return {str(self.ret_var)}"


################################################################################
### LOL ANALYSIS TYPES
################################################################################
LolAnalysisDataType = Union["LolAnalysisBuiltinType"]
LolAnalysisSymbol = Union[LolAnalysisDataType, "LolAnalysisFunction", "LolAnalysisVariable"]


def optional_to_dict(obj: Any):
    """Return obj.to_dict() if it has that attribute."""
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
    """Get the names of a dict of objects with that attribute."""
    if obj is None:
        return None
    else:
        # assert isinstance(obj, Dict[str, LolAnalysisSymbol])
        return {key: val.name for key, val in obj.items()}


class LolAnalysisBuiltinType:
    # TODO(dchu): Make the object of the ops into a function so that we can
    #  specify the parameter types and the pointer types.
    def __init__(self, name: str, ops: Dict[str, "LolAnalysisBuiltinType"]):
        self.name = name
        self.ops = ops

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name})"

    def to_dict(self):
        return dict(
            metatype=self.__class__.__name__,
            name=self.name,
            ops={op: dt.name for op, dt in self.ops.items()},
            id=id(self),
        )


def get_type(
    type_ast: LolParserTypeExpression,
    module_symbol_table: Dict[str, LolAnalysisSymbol]
) -> LolAnalysisDataType:
    """Get the data type of an AST node."""
    # TODO: Change this in when we support multi-token TypeExpressions
    assert isinstance(type_ast, LolParserIdentifier)
    type_name = type_ast.name
    if type_name not in module_symbol_table:
        raise ValueError(f"module symbol table should contain name {type_name}")
    type_symbol: LolAnalysisDataType = module_symbol_table[type_name]
    # Python 3.10 should support this due to PIP 604
    # assert isinstance(type_symbol, LolAnalysisDataType)
    return type_symbol


class LolAnalysisVariable:
    def __init__(
        self,
        name: str,
        ast_definition_node: Optional[Union[LolParserVariableDefinition, LolParserParameterDefinition]],
        *,
        type: Optional[LolAnalysisDataType] = None,
    ):
        assert isinstance(name, str)
        assert isinstance(ast_definition_node, (LolParserVariableDefinition, LolParserParameterDefinition)) or ast_definition_node is None
        self.name = name
        self.ast_definition_node = ast_definition_node

        self.type: Optional[LolAnalysisDataType] = type

    def __str__(self):
        return f"{self.name}: {str(self.type)}"

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name}, type={str(self.type)})"

    @staticmethod
    def init_local_variable(
        name: str,
        ast_definition_node: Optional[Union[LolParserVariableDefinition, LolParserParameterDefinition]],
        module_symbol_table: Dict[str, LolAnalysisSymbol]
    ) -> "LolAnalysisVariable":
        """This method is to allow initializing a variable without needing to
        wait to complete the prototype. This is just for convenience."""
        r = LolAnalysisVariable(name, ast_definition_node)
        r.complete_prototype(module_symbol_table)
        return r

    def complete_prototype(self, module_symbol_table: Dict[str, LolAnalysisSymbol]):
        assert self.type is None
        self.type = get_type(self.ast_definition_node.type, module_symbol_table)

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
        ast_definition_node: Optional[parser_types.LolParserFunctionDefinition],
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

    def __str__(self):
        parameters = ", ".join(
            f'{name}: {str(type_)}'
                for name, type_ in
            zip(self.parameter_names, self.parameter_types)
        )
        return f"function {self.name}({parameters}) -> {str(self.return_types)}"

    def __repr__(self):
        parameters = ", ".join(
            f'{name}: {str(type_)}'
            for name, type_ in zip(self.parameter_names, self.parameter_types)
        )
        return f"{self.__class__.__name__}(name={self.name}, parameters=({parameters}), return_type={str(self.return_types)})"

    def complete_prototype(self, module_symbol_table: Dict[str, LolAnalysisSymbol]):
        assert self.return_types is None
        assert self.parameter_types is None
        assert self.parameter_names is None
        self.return_types = get_type(self.ast_definition_node.return_type, module_symbol_table)
        self.parameter_types = [
            get_type(t.type, module_symbol_table) for t in self.ast_definition_node.parameters
        ]
        self.parameter_names = [
            t.get_name_as_str() for t in self.ast_definition_node.parameters
        ]

    def _get_temporary_variable_name(self) -> str:
        # NOTE: this is a complete hack!
        if not hasattr(self, "tmp_cnt"):
            self.tmp_cnt = 0
        tmp = self.tmp_cnt
        self.tmp_cnt += 1
        return f"%{tmp}"

    def _get_symbol(self, module_symbol_table: Dict[str, LolAnalysisSymbol], name: str) -> LolAnalysisSymbol:
        split_names = name.split("::")
        first_name = split_names[0]

        if first_name in self.symbol_table:
            module = self.symbol_table
            for name in split_names[:-1]:
                module = module[name].module_symbol_table
            last_name = split_names[-1]
            return module[last_name]
        elif first_name in module_symbol_table:
            module = module_symbol_table
            for name in split_names[:-1]:
                module = module[name].module_symbol_table
            last_name = split_names[-1]
            return module[last_name]
        else:
            raise ValueError(f"symbol {first_name} not found in either module")

    def _get_operator_return_type(
        self,
        module_symbol_table: Dict[str, LolAnalysisSymbol],
        op_name: str,
        operands: List["LolAnalysisVariable"]
    ) -> Optional[LolAnalysisDataType]:
        first_operand, *_ = operands
        hacky_ret_type = self._get_symbol(module_symbol_table, first_operand.name).type
        return hacky_ret_type

    def _parse_expression_recursively(
        self,
        x: LolParserExpression,
        module_symbol_table: Dict[str, LolAnalysisSymbol],
        *,
        body_block: List[LolIRStatement],
    ) -> str:
        if isinstance(x, LolParserOperatorExpression):
            op_name: str = x.operator
            operands: List["LolAnalysisVariable"] = [
                self._get_symbol(
                    module_symbol_table,
                    self._parse_expression_recursively(y, module_symbol_table, body_block=body_block)
                )
                for y in x.operands
            ]
            ret = self._get_temporary_variable_name()
            ret_type = self._get_operator_return_type(module_symbol_table, op_name, operands)
            ret_value = LolIROperatorExpression(op_name, operands)
            stmt = LolIRDefinitionStatement(
                ret, ret_type, ret_value
            )
            body_block.append(stmt)
            self.symbol_table[ret] = LolAnalysisVariable(ret, None, type=ret_type)
            return ret
        elif isinstance(x, LolParserLiteral):
            if x.type == LolParserLiteralType.INTEGER:
                ret = self._get_temporary_variable_name()
                ret_type = module_symbol_table["i32"]
                stmt = LolIRDefinitionStatement(
                    ret, ret_type, LolIRLiteralExpression(x.value)
                )
                body_block.append(stmt)
                self.symbol_table[ret] = LolAnalysisVariable(ret, None, type=ret_type)
                return ret
            elif x.type == LolParserLiteralType.STRING:
                ret = self._get_temporary_variable_name()
                ret_type = module_symbol_table["cstr"]
                stmt = LolIRDefinitionStatement(
                    ret, ret_type, LolIRLiteralExpression(x.value)
                )
                body_block.append(stmt)
                self.symbol_table[ret] = LolAnalysisVariable(ret, None, type=ret_type)
                return ret
            else:
                raise NotImplementedError
        elif isinstance(x, LolParserFunctionCall):
            func_name: str = x.get_name_as_str()
            func: LolAnalysisFunction = self._get_symbol(module_symbol_table, func_name)
            assert isinstance(func, LolAnalysisFunction)
            args: List["LolAnalysisVariable"] = [
                self._get_symbol(
                    module_symbol_table,
                    self._parse_expression_recursively(y, module_symbol_table, body_block=body_block)
                )
                for y in x.arguments
            ]
            ret: str = self._get_temporary_variable_name()
            ret_type = func.return_types
            stmt = LolIRDefinitionStatement(
                ret, ret_type, LolIRFunctionCallExpression(func, args)
            )
            body_block.append(stmt)
            self.symbol_table[ret] = LolAnalysisVariable(ret, None, type=ret_type)
            return ret
        elif isinstance(x, LolParserReturnStatement):
            ret = self._parse_expression_recursively(x.value, module_symbol_table, body_block=body_block)
            stmt = LolIRReturnStatement(self._get_symbol(module_symbol_table, ret))
            body_block.append(stmt)
        elif isinstance(x, LolParserIfStatement):
            if_cond_name = self._parse_expression_recursively(x.if_condition, module_symbol_table, body_block=body_block)
            if_cond = self._get_symbol(module_symbol_table, if_cond_name)
            if_block = []
            for y in x.if_block:
                self._parse_statement(module_symbol_table, y, body_block=if_block)
            else_block = []
            for y in x.else_block:
                self._parse_statement(module_symbol_table, y, body_block=else_block)
            stmt = LolIRIfStatement(if_cond, if_block, else_block)
            body_block.append(stmt)
        elif isinstance(x, LolParserIdentifier):
            return x.name
        else:
            raise NotImplementedError

    def _parse_statement(
        self,
        module_symbol_table: Dict[str, LolAnalysisSymbol],
        x: LolParserFunctionLevelStatement,
        *,
        body_block: List[LolIRStatement],
    ):
        if isinstance(x, LolParserVariableDefinition):
            name = x.get_name_as_str()
            ast_data_type = x.type
            assert isinstance(ast_data_type, LolParserIdentifier)
            data_type = self._get_symbol(module_symbol_table, ast_data_type.name)
            value = self._parse_expression_recursively(x.value, module_symbol_table, body_block=body_block)
            self.symbol_table[name] = LolAnalysisVariable.init_local_variable(name, x, module_symbol_table)
            stmt = LolIRDefinitionStatement(
                name, data_type, self._get_symbol(module_symbol_table, value)
            )
            body_block.append(stmt)
        elif isinstance(x, LolParserVariableModification):
            # I'm not even sure that the parser supports modification nodes
            raise NotImplementedError
        else:
            _unused_return_variable = self._parse_expression_recursively(x, module_symbol_table, body_block=body_block)

    def complete_body(self, module_symbol_table: Dict[str, LolAnalysisSymbol]):
        assert self.symbol_table is None
        assert self.body is None
        # Add parameters to the symbol table
        self.symbol_table = {
            t.get_name_as_str(): LolAnalysisVariable.init_local_variable(
                t.get_name_as_str(), t, module_symbol_table
                )
            for t in self.ast_definition_node.parameters
        }
        self.body = []
        for statement in self.ast_definition_node.body:
            self._parse_statement(module_symbol_table, statement, body_block=self.body)

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
    def _add_function_name(self, ast_definition: LolParserFunctionDefinition):
        name = ast_definition.get_name_as_str()
        symbol = LolAnalysisFunction(name, ast_definition)
        self.add_to_module_symbol_table(name, symbol)

    def _add_variable_name(self, ast_definition: LolParserVariableDefinition):
        name = ast_definition.get_name_as_str()
        symbol = LolAnalysisVariable.init_local_variable(name, ast_definition)
        self.add_to_module_symbol_table(name, symbol)

    # TODO: merge this into the variable!
    def _add_import_name(self, ast_definition: LolParserImportStatement):
        alias = ast_definition.get_alias_as_str()
        library = ast_definition.get_library_name_as_str()
        if library == "\"stdio.h\"":
            module = LolAnalysisModule(library, caller_module=self)
            i32: LolAnalysisBuiltinType = self.module_symbol_table["i32"]
            cstr: LolAnalysisBuiltinType = self.module_symbol_table["cstr"]
            printf_func = LolAnalysisFunction(
                "printf",
                None,
                return_types=i32,
                parameter_types=[cstr],
                parameter_names=["format"],
            )
            module.add_to_module_symbol_table("printf", printf_func)
        else:
            raise NotImplementedError("only stdio.h library is supported!")
        self.add_to_module_symbol_table(alias, module)

    def get_module_names(self, ast_nodes: List[LolParserModuleLevelStatement]):
        """
        Extract names (only) of function definitions, module definitions, and
        imports.

        TODO
        ----
        1. Add struct/enum/monad
        """
        for i, node in enumerate(ast_nodes):
            if isinstance(node, LolParserFunctionDefinition):
                self._add_function_name(node)
            elif isinstance(node, LolParserVariableDefinition):
                self._add_variable_name(node)
            elif isinstance(node, LolParserImportStatement):
                # TODO(dchu) - recursively add members to this submodule!
                self._add_import_name(node)
            # TODO(dchu): accept data structures
            else:
                # We will ignore anything outside of functions! This is an error
                raise ValueError(f"{node} cannot be outside of functions!")

    ### PROTOTYPES
    def add_function_prototype(self, ast_definition: LolParserFunctionDefinition):
        name = ast_definition.get_name_as_str()
        func: LolAnalysisFunction = self.module_symbol_table[name]
        func.complete_prototype(self.module_symbol_table)

    def add_variable_prototype(self, ast_definition: LolParserVariableDefinition):
        name = ast_definition.get_name_as_str()
        var: LolAnalysisVariable = self.module_symbol_table[name]
        var.complete_prototype(self.module_symbol_table)

    def add_import_prototype(self, ast_definition: LolParserImportStatement):
        # Intentionally do nothing
        pass

    def get_module_prototypes(self, ast_nodes: List[LolParserModuleLevelStatement]):
        """Get function and variable prototypes."""
        for i, node in enumerate(ast_nodes):
            if isinstance(node, LolParserFunctionDefinition):
                self.add_function_prototype(node)
            elif isinstance(node, LolParserVariableDefinition):
                self.add_variable_prototype(node)
            elif isinstance(node, LolParserImportStatement):
                self.add_import_prototype(node)
            else:
                # We will ignore anything outside of functions! This is an error
                raise ValueError(f"{node} cannot be outside of functions!")

    ### BODIES
    def add_function_body(self, ast_definition: LolParserFunctionDefinition):
        name = ast_definition.get_name_as_str()
        func: LolAnalysisFunction = self.module_symbol_table[name]
        func.complete_body(self.module_symbol_table)

    def add_variable_body(self, ast_definition: LolParserVariableDefinition):
        # Intentionally do nothing
        pass

    def add_import_body(self, ast_definition: LolParserImportStatement):
        # Intentionally do nothing
        pass

    def get_module_bodies(self, ast_nodes: List[LolParserModuleLevelStatement]):
        for i, node in enumerate(ast_nodes):
            if isinstance(node, LolParserFunctionDefinition):
                self.add_function_body(node)
            elif isinstance(node, LolParserVariableDefinition):
                self.add_variable_body(node)
            elif isinstance(node, LolParserImportStatement):
                self.add_import_body(node)
            else:
                # We will ignore anything outside of functions! This is an error
                raise ValueError(f"{node} cannot be outside of functions!")


def analyze(asts: List[LolParserModuleLevelStatement], raw_text: str) -> LolAnalysisModule:
    module = LolAnalysisModule("main")
    module.get_module_names(asts)
    module.get_module_prototypes(asts)
    module.get_module_bodies(asts)

    return module
