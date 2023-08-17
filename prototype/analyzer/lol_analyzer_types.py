from abc import ABCMeta
from enum import Enum, auto, unique
from typing import Any, Dict, List, Set, Union

import prototype.parser.lol_parser_types as parser_types
from prototype.analyzer.c_keywords import SymbolSource, C_KEYWORDS


@unique
class COpType(Enum):
    CALL = auto()  # <op>(<args>, ...), e.g. func_name(x, y, z)
    ACCESS = auto()  # <op>[<args>], e.g. array_name[x]
    PREFIX = auto()  # <op><arg>, e.g. +x
    INFIX = auto()  # <arg0> <op> <arg1>, e.g. x+y
    SUFFIX = auto()  # <arg><op>, e.g. x++


################################################################################
### BUILDING BLOCKS
################################################################################
class LolAnalysisObj(metaclass=ABCMeta):
    def __init__(self, name: str, alt_c_name: Union[str, None]):
        self.name = name
        self.c_name = alt_c_name if alt_c_name is not None else name


class LolDataType(LolAnalysisObj):
    """
    Represent a data type in LOL. E.g. struct, enum, monad, or builtin type.
    """

    def __init__(
        self,
        name: str,
        alt_c_name: str = None,
        ast_node: parser_types.ASTNode = None,
    ):
        super().__init__(name, alt_c_name)
        self._ast_node = ast_node
        self.functions: Dict[str, "LolFunction"] = {}

    def __repr__(self):
        return f"{self.name}"

    def add_function(self, func: "LolFunction"):
        self.functions[func.name] = func


class LolDataVariable(LolAnalysisObj):
    def __init__(
        self,
        name: str,
        ast_node: parser_types.ASTNode = None,
        data_type: LolDataType = None,  # Is unknown at instantiation
        init_value: Any = None,
        *,
        alt_c_name: str = None,  # Use name unless otherwise specified
        is_mut: bool = False,  # Opposite of C's const
        is_unrestricted: bool = False,  # Opposite of C's restrict
        is_volatile: bool = False,  # Equivalent to C's volatile
    ):
        super().__init__(name, alt_c_name)
        self._ast_node = ast_node
        self.data_type = data_type
        self.init_value = init_value

        self.is_mut = is_mut
        self.is_unrestricted = is_unrestricted
        self.is_volatile = is_volatile

    def __repr__(self):
        return f"{self.name}: {self.data_type} = {self.init_value}"

    def add_data_type(self, data_type: LolDataType):
        self.data_type = data_type

    def add_init_value(self, init_value: Any):
        self.init_value = init_value

    def get_return_type(self):
        return self.data_type


class LolFunction(LolAnalysisObj):
    def __init__(
        self,
        name: str,
        ast_node: parser_types.ASTNode = None,  # Only for user-defined func
        params: List[LolDataVariable] = None,  # DEPRECATED?
        return_type: LolDataType = None,  # DEPRECATED?
        *,
        alt_c_name: str = None,
        c_op_type: COpType = COpType.CALL,
        is_builtin_c: bool = None,  # If so, do not perform checks yet...
        is_pure: bool = None,
        is_public: bool = None,
    ):
        super().__init__(name, alt_c_name)
        # For debugging
        self._ast_node = ast_node

        self.params = params
        self.return_type = return_type
        self.body = None

        # C stuff
        self.c_op_type = c_op_type
        self.is_builtin_c = is_builtin_c

        # Optimization
        self.is_pure = is_pure
        self.is_public = is_public

    def __repr__(self):
        name = self.name
        params = tuple(self.params) if self.params is not None else "(?)"
        return_type = self.return_type if self.return_type is not None else "?"
        return f"function {name}{params} -> {return_type}"

    def add_params(self, params: List[LolDataVariable]):
        if self.params is not None:
            raise ValueError("trying to overwrite params")
        self.params = params

    def add_return_type(self, return_type: LolDataType):
        if self.return_type is not None:
            raise ValueError("trying to overwrite return_type")
        self.return_type = return_type

    def add_body(self) -> "LolFunction":
        if self.is_builtin_c:
            raise ValueError("trying to add body to built in function!")
        return self


class LolOperator(LolAnalysisObj):
    """TODO: maybe this could be derived from LolFunction?"""

    def __init__(
        self,
        operator: str,
        operator_type: parser_types.OperatorType,
        operand_types: List[LolDataType],
        return_type: LolDataType,
    ):
        # This implies that the LOL operators directly shadow their C
        # counterparts. That is, the c_alt_name == the name.
        super().__init__(operator, operator)
        self._operator = operator
        self._operator_type = operator_type
        self._operand_types = operand_types
        self._return_type = return_type

    def get_return_type(self):
        return self._return_type


################################################################################
### VALUE EXPRESSIONS
################################################################################
class ValueExpression(metaclass=ABCMeta):
    """
    Abstract class for expressions with side effects.

    N.B. Expressions without side-effects may be safely removed.
    """

    pass


class FunctionCallExpression(ValueExpression):
    def __init__(self, function: LolFunction, arguments: List[ValueExpression]):
        super().__init__()
        self._function = function
        self._arguments = arguments

    def get_return_type(self) -> LolDataType:
        return self._function.return_type


class OperatorValueExpression(ValueExpression):
    def __init__(
        self,
        operator: LolOperator,
        arguments: List[ValueExpression],
    ):
        super().__init__()
        self._operator = operator
        self._arguments = arguments

    def get_return_type(self) -> LolDataType:
        return self._operator.get_return_type()


class LiteralExpression(ValueExpression):
    """
    Assign a literal to a variable for easier debugging.

    N.B. corner case: if we are already assigning a literal to a named variable,
    the we do not need to assign it to an unnamed variable.

    E.g. `named_var: int = 10;` does not need
        `unnamed_var: int = 10; named_var: int = unnamed_var;`
    """

    def __init__(
        self,
        literal: parser_types.Literal,
        data_type: LolDataType,
    ):
        super().__init__()
        self._literal = literal
        self._data_type = data_type

    def get_return_type(self) -> LolDataType:
        return self._data_type


class VariableCallExpression(ValueExpression):
    def __init__(self, data_variable: LolDataVariable):
        self._data_variable = data_variable

    def get_return_type(self) -> LolDataType:
        return self._data_variable.get_return_type()



################################################################################
### STATEMENTS
################################################################################
class Statement(metaclass=ABCMeta):
    def __init__(self):
        pass

    # @abstractmethod
    # def emit(self):
    #     pass


class VariableDefinitionStatement(Statement):
    """<lvalue> = <expr>"""

    def __init__(
        self,
        data_type: LolDataType,
        lvalue: LolDataVariable,
        expression: ValueExpression,
    ):
        super().__init__()
        self._data_type = data_type
        self._lvalue = lvalue
        self._expression = expression


class VariableModificationStatement(Statement):
    def __init__(
        self,
        lvalue: LolDataVariable,
        expression: ValueExpression,
    ):
        super().__init__()
        self._lvalue = lvalue
        self._expression = expression


class ExpressionWithSideEffectStatement(Statement):
    """Expression with side-effects."""

    def __init__(
        self,
        expression: ValueExpression,
    ):
        super().__init__()
        self._expression = expression


class ReturnStatement(Statement):
    def __init__(self, expr: ValueExpression):
        super().__init__()
        self.expr = expr


################################################################################
### MODULE
################################################################################
class LolModule(LolAnalysisObj):
    """
    NOTES
    -----

    1. No name mangling
        * Thus, no overloading
    2. No custom types
    3. No default values for functions
    4. No default values for custom types
    """

    def __init__(self, name: str, raw_text: str):
        # TODO(dchu): figure this one out! What should the names of modules be?
        # TODO(dchu): The package?
        super().__init__(name, "")
        # Raw text is simply for debugging!
        self._raw_text: str = raw_text
        # C Standard Library Headers to Include
        # I will include the angled brackets or quotations since it is not
        # immediately obvious whether to use brackets or quotes otherwise.
        self.c_includes: List[str] = []
        # Symbols in the C namespace (NOTE: the struct, function, and variable
        # namespaces are all different in C, but we will keep them together).
        # This namespace is just to ensure there are no collisions (since we do
        # not allow name mangling).
        self.c_namespace: Dict[str, SymbolSource] = {**C_KEYWORDS}
        # The symbol table is the set of usable names.
        self.symbol_table: Dict[str, LolAnalysisObj] = {}

        # Add C and LOL builtins to C namespace and symbol table
        if name == "":
            self.add_lol_builtins()

    def __repr__(self):
        return repr(self.symbol_table)

    def add_lol_builtins(self):
        """
        NOTE: this adds these to only the top level module. We can only run
        this function once--otherwise, there will be duplicate int32 objects.
        """
        self.symbol_table["int32"] = LolDataType("int32", alt_c_name="int")
        self.symbol_table["str"] = LolDataType("str", alt_c_name="char *")

    def add_builtin_func(self, name: str):
        if (
            name in self.c_namespace
            and self.c_namespace[name] != SymbolSource.C_STDLIB
        ):
            raise ValueError(
                f"user-defined symbol '{name}' already in "
                f"C namespace '{self.c_namespace}'"
            )
        self.c_namespace[name] = SymbolSource.C_STDLIB
        self.symbol_table[name] = LolFunction(name, is_builtin_c=True)

    def include_stdio(self, lol_alias: str):
        from prototype.analyzer.lol_analyzer_reserved_names import STDIO_H_NAMES

        lib_name = "<stdio.h>"
        if lib_name in self.c_includes:
            raise ValueError(
                f"module '{lib_name}' already in "
                f"C includes list '{self.c_includes}'"
            )
        self.c_includes.append(lib_name)
        # Ensure that all names within stdio.h are unique
        # NOTE: some C standard library names overlap without problem.
        # E.g. NULL, size_t, etc. We take care of that by checking the source
        # as well.
        for stdio_name in STDIO_H_NAMES:
            if stdio_name in self.c_namespace:
                if self.c_namespace[stdio_name] == SymbolSource.C_STDLIB:
                    continue
                else:
                    raise ValueError(
                        f"name '{stdio_name}' already in "
                        f"C namespace '{self.c_namespace}'"
                    )
            else:
                self.c_namespace[stdio_name] = SymbolSource.C_STDLIB
        # Check that the alias is unique in the symbol table too!
        if lol_alias in self.symbol_table:
            raise ValueError(
                f"name '{lol_alias}' already in "
                f"symbol table '{self.symbol_table}'"
            )
        stdio_namespace = LolModule(lol_alias, self._raw_text)
        stdio_namespace.add_builtin_func("printf")
        self.symbol_table[lol_alias] = stdio_namespace

    ############################################################################
    ### Add names to module
    ############################################################################
    def add_function_name(
        self, function_node: parser_types.FunctionDefinitionNode
    ):
        name = function_node.get_name_as_str()
        if name in self.c_namespace:
            raise ValueError(
                f"name '{name}' already in C namespace '{self.c_namespace}'"
            )
        if name in self.symbol_table:
            raise ValueError(
                f"name '{name}' already in symbol table '{self.symbol_table}'"
            )
        self.c_namespace[name] = SymbolSource.USER
        self.symbol_table[name] = LolFunction(name, function_node)

    def add_variable_definition_name(
        self, var_def_node: parser_types.VariableDefinitionNode
    ):
        name = var_def_node.get_name_as_str()
        if name in self.c_namespace:
            raise ValueError(
                f"name '{name}' already in C namespace '{self.c_namespace}'"
            )
        if name in self.symbol_table:
            raise ValueError(
                f"name '{name}' already in symbol table '{self.symbol_table}'"
            )
        self.c_namespace[name] = SymbolSource.USER
        self.symbol_table[name] = LolDataVariable(name, ast_node=var_def_node)

    def add_submodule(self, submodule_node: parser_types.ImportModuleNode):
        # TODO - this should just import all recursively!
        name = submodule_node.get_name_as_str()
        submodule_name = submodule_node.get_library_as_str()
        if name in self.symbol_table:
            raise ValueError(
                f"name '{name}' already in "
                f"symbol table '{self.symbol_table}'"
            )
        if submodule_name == "stdio.h":
            self.include_stdio(name)
        else:
            # self.symbol_table[name] = Module(name, "")
            raise ValueError("general imports not supported!")

    ############################################################################
    ### Add prototypes to module
    ############################################################################
    def _parse_type_expression(
        self, type_expression: parser_types.TypeExpression
    ) -> LolDataType:
        if isinstance(type_expression, parser_types.Identifier):
            name = type_expression.token.lexeme
            if name not in self.symbol_table:
                raise ValueError(
                    f"type '{name}' not in symbol table '{self.symbol_table}'"
                )
            result = self.symbol_table[name]
            assert isinstance(result, LolDataType)
            return result
        else:
            raise ValueError(f"type '{type(type_expression)}' is unsupported")

    def _parse_value_expression(
        self, value_expression: parser_types.ValueExpression
    ) -> ValueExpression:
        if isinstance(value_expression, parser_types.Literal):
            data_type = {
                parser_types.StringLiteral: self.symbol_table["str"],
                parser_types.DecimalLiteral: self.symbol_table["int32"],
            }.get(type(value_expression))
            assert data_type is not None
            return LiteralExpression(value_expression.value, data_type)
        elif isinstance(value_expression, parser_types.VariableCallNode):
            data_var_name = value_expression.get_name_as_str()
            data_var = self.symbol_table[data_var_name]
            assert isinstance(data_var, LolDataVariable)
            return VariableCallExpression(data_var)
        elif isinstance(value_expression, parser_types.OperatorValueExpression):
            # Get operator
            op_str = value_expression.get_operator_as_str()
            # NOTE: operators for int/float are overloaded. How do we decide
            # which one to get?
            operator = self.symbol_table[op_str]
            assert isinstance(operator, LolOperator)
            # Get operands
            analysis_args = []
            for parser_args in value_expression.get_operands():
                arg = self._parse_value_expression(parser_args)
                analysis_args.append(arg)
            return OperatorValueExpression(operator, analysis_args)
        elif isinstance(value_expression, parser_types.FunctionCallNode):
            # Get function
            func_name = value_expression.get_name_as_str()
            func = self.symbol_table[func_name]
            assert isinstance(func, LolFunction)
            # Get operands
            analysis_args = []
            for parser_args in value_expression.get_arguments():
                arg = self._parse_value_expression(parser_args)
                analysis_args.append(arg)
            return FunctionCallExpression(func, analysis_args)

    def add_function_prototype(
        self, func_node: parser_types.FunctionDefinitionNode
    ):
        name = func_node.get_name_as_str()
        assert name in self.symbol_table
        func = self.symbol_table[name]
        assert isinstance(func, LolFunction)
        func.add_params(
            [
                LolDataVariable(
                    name=var_def_node.get_name_as_str(),
                    data_type=self._parse_type_expression(
                        var_def_node.get_data_type()
                    ),
                    init_value=None,  # We don't support default val functions
                )
                for var_def_node in func_node.get_parameters()
            ]
        )
        func.add_return_type(
            self._parse_type_expression(func_node.get_return_type())
            )

    def add_variable_definition_prototype(
        self, variable_definition_node: parser_types.VariableDefinitionNode
    ):
        name = variable_definition_node.get_name_as_str()
        assert name in self.symbol_table
        var_def = self.symbol_table[name]
        assert isinstance(var_def, LolDataVariable)
        var_def.add_data_type(
            self._parse_type_expression(
                variable_definition_node.get_data_type()
                )
        )
        var_def.add_init_value(variable_definition_node.get_value())

    ############################################################################
    # Add bodies
    ############################################################################
    def add_function_body(self, func_node: parser_types.FunctionDefinitionNode):
        # TODO - check func_node's name exists in symbol table. Add body statements to function
        name = func_node.name.token.lexeme
        assert name in self.symbol_table and isinstance(
            self.symbol_table[name], LolFunction
        )
        func: LolFunction = self.symbol_table[name]

        body: List[Statement] = []
        var_counter = 0
        for i, statement in func_node.body:
            if isinstance(statement, parser_types.DefinitionNode):
                body.append(Statement())
            elif isinstance(statement, parser_types.OperatorValueExpression):
                pass
            elif isinstance(statement, parser_types.FunctionCallNode):
                pass
            elif isinstance(statement, parser_types.ReturnNode):
                body.append(ReturnStatement())
            else:
                raise ValueError(f"unsupported statement {statement}")


################################################################################
### BUILTINS
################################################################################

# TODO
# ====
# 1. Move builtins to separate file
# 2. blah

# Data Types
lol_int32 = LolDataType("int32", alt_c_name="int")
lol_str = LolDataType("str", alt_c_name="char *")
lol_bool = LolDataType("bool", alt_c_name="int")
lol_void = LolDataType("void")

# Placeholder Variables
unnamed_lol_int32 = LolDataVariable(None, lol_int32, None)
unnamed_lol_str = LolDataVariable(None, lol_str, None)

# Functions
lol_printf = LolFunction(
    "printf",
    [unnamed_lol_str],
    lol_int32,
    is_builtin_c=True,
)

builtins: Dict[str, Any] = {
    "int32": lol_int32,
    "string": lol_str,
    "bool": lol_bool,
}

includes: Set[str] = {"stdio.h"}

lol_int32.add_function(
    LolFunction(
        "+",
        [unnamed_lol_int32, unnamed_lol_int32],
        lol_int32,
        alt_c_name="+",
        is_builtin_c=True,
        c_op_type=COpType.INFIX,
    )
)
lol_int32.add_function(
    LolFunction(
        "-",
        [unnamed_lol_int32, unnamed_lol_int32],
        lol_int32,
        alt_c_name="-",
        is_builtin_c=True,
        c_op_type=COpType.INFIX,
    )
)
