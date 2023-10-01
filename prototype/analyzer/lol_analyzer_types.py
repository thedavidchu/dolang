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


def parse_type_expression(
    scope: "LolScope", type_expression: parser_types.TypeExpression
) -> "LolDataType":
    if isinstance(type_expression, parser_types.Identifier):
        name = type_expression.token.lexeme
        if name not in scope:
            raise ValueError(
                f"type '{name}' not in symbol table '{scope}'"
            )
        result = scope.search_scope(name)
        assert isinstance(result, LolDataType)
        return result
    else:
        raise ValueError(f"type '{type(type_expression)}' is unsupported")


def parse_value_expression(
    scope: "LolScope", value_expression: parser_types.ValueExpression
) -> "ValueExpression":
    if isinstance(value_expression, parser_types.Literal):
        data_type = {
            parser_types.StringLiteral: scope.search_scope("str"),
            parser_types.DecimalLiteral: scope.search_scope("int32"),
        }.get(type(value_expression))
        assert data_type is not None
        return LiteralExpression(value_expression.value, data_type)
    elif isinstance(value_expression, parser_types.VariableCallNode):
        data_var_name = value_expression.get_name_as_str()
        data_var = scope.search_scope(data_var_name)
        assert isinstance(data_var, LolDataVariable)
        return VariableCallExpression(data_var)
    elif isinstance(value_expression, parser_types.OperatorValueExpression):
        # Get operator
        op_str = value_expression.get_operator_as_str()
        # NOTE: operators for int/float are overloaded. How do we decide
        # which one to get?
        operator = scope.search_scope(op_str)
        assert isinstance(operator, LolOperator)
        # Get operands
        analysis_args = []
        for parser_args in value_expression.get_operands():
            arg = parse_value_expression(parser_args)
            analysis_args.append(arg)
        return OperatorValueExpression(operator, analysis_args)
    elif isinstance(value_expression, parser_types.FunctionCallNode):
        # Get function
        func_name = value_expression.get_name_as_str()
        func = scope.search_scope(func_name)
        assert isinstance(func, LolFunction)
        # Get operands
        analysis_args = []
        for parser_args in value_expression.get_arguments():
            arg = parse_value_expression(parser_args)
            analysis_args.append(arg)
        return FunctionCallExpression(func, analysis_args)


################################################################################
### BUILDING BLOCKS
################################################################################
class LolAnalysisObj(metaclass=ABCMeta):
    """More like, 'named C object'. i.e. data type, variable, function."""

    def __init__(self, name: str, alt_c_name: Union[str, None] = None):
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

        self._parameters = params
        self._return_type = return_type
        self._body = None

        # C stuff
        self.c_op_type = c_op_type
        self.is_builtin_c = is_builtin_c

        # Optimization
        self.is_pure = is_pure
        self.is_public = is_public

    def __repr__(self):
        name = self.name
        params = tuple(
            self._parameters
            ) if self._parameters is not None else "(?)"
        ret_t = self._return_type if self._return_type is not None else "?"
        return f"function {name}{params} -> {ret_t}"

    ############################################################################
    ### FUNCTION PROTOTYPE
    ############################################################################
    def add_prototype(
        self, scope: "LolScope", func_node: parser_types.FunctionDefinitionNode
    ):
        parser_params = func_node.get_parameters()
        self._add_parameters(scope, parser_params)

        parser_ret_t = func_node.get_return_type()
        self._add_return_type(scope, parser_ret_t)

    def _add_parameters(
        self, scope: "LolScope",
        parser_params: List[parser_types.VariableDefinitionNode]
    ):
        if self._parameters is not None:
            raise ValueError("trying to overwrite params")
        params = []
        for var_def_node in parser_params:
            name = var_def_node.get_name_as_str()
            data_t = parse_type_expression(scope, var_def_node.get_data_type())
            p = LolDataVariable(
                name=name,
                data_type=data_t,
                init_value=None,  # We don't support default val functions
            )
            params.append(p)
        self._parameters = params

    def _add_return_type(
        self, scope: "LolScope", return_type: parser_types.TypeExpression
    ):
        if self._return_type is not None:
            raise ValueError("trying to overwrite return_type")
        ret_t = parse_type_expression(scope, return_type)
        self._return_type = ret_t

    ############################################################################
    ### FUNCTION BODY
    ############################################################################
    def add_body(
        self, scope: "LolScope", func_node: parser_types.FunctionDefinitionNode
    ):
        if self.is_builtin_c:
            raise ValueError("trying to add body to built in function!")
        # Type check
        func_name = func_node.get_name_as_str()
        func = scope.search_scope(func_name)
        assert isinstance(func, LolFunction)

        analyzer_body: List[Statement] = []
        anon_var_counter = 0
        # NOTE: does not support function definitions or module imports here.
        for i, statement in func_node.get_body():
            if isinstance(statement, parser_types.VariableDefinitionNode):
                r = self._add_variable_definition_statement(scope, statement)
                analyzer_body.append(r)
            elif isinstance(statement, parser_types.VariableModificationNode):
                r = self._add_variable_modification_statement(scope, statement)
                analyzer_body.append(r)
            elif isinstance(statement, parser_types.FunctionCallNode):
                r = self._add_function_call_statement(scope, statement)
                analyzer_body.append(r)
            elif isinstance(statement, parser_types.ReturnNode):
                raise NotImplementedError
            # Allowing expressions means that we expect operators to potentially
            # have side-effects!
            elif isinstance(
                statement, parser_types.OperatorValueExpression
            ):
                raise NotImplementedError
            # TODO(dchu): ignore solitary literals and identifiers that have no
            # TODO(dchu): ... side effects or observable actions.
            else:
                raise ValueError(f"unsupported statement {statement}")

    def _add_variable_definition_statement(
        self, scope: "LolScope", var_def: parser_types.VariableDefinitionNode
    ):
        lvalue = var_def.get_name_as_str()
        parser_data_type = var_def.get_data_type()
        parser_value = var_def.get_value()

        data_t = parse_type_expression(scope, parser_data_type)
        value = parse_value_expression(scope, parser_value)

        data_var = LolDataVariable(
            lvalue, var_def, data_type=data_t, init_value=value
        )
        analyzer_statement = VariableDefinitionStatement(
            lvalue=data_var,
            data_type=data_t,
            expression=value,
        )
        return analyzer_statement

    def _add_variable_modification_statement(
        self, scope: "LolScope", var_mod: parser_types.VariableModificationNode
    ):
        lvalue = var_mod.get_name_as_str()
        parser_value = var_mod.get_value()

        value = parse_value_expression(scope, parser_value)

        data_var = scope.search_scope(lvalue)
        analyzer_statement = VariableModificationStatement(
            lvalue=data_var,
            expression=value,
        )
        return analyzer_statement

    def _add_function_call_statement(
        self, scope: "LolScope", func_call: parser_types.FunctionCallNode
    ) -> "ExpressionWithSideEffectStatement":
        name = func_call.get_name_as_str()
        args = func_call.get_arguments()
        func = scope.search_scope(name)
        analyzer_args = [parse_value_expression(scope, expr) for expr in args]
        func_statement = FunctionCallExpression(func, analyzer_args)
        analyzer_statement = ExpressionWithSideEffectStatement(func_statement)
        return analyzer_statement

    def _add_return_statement(
        self, scope: "LolScope", ret_stmt: parser_types.ReturnNode
    ):
        expr = ret_stmt.get_expression()
        analyzer_expr = parse_value_expression(scope, expr)
        analyzer_statement = ReturnStatement(analyzer_expr)
        return analyzer_statement

    ############################################################################
    ### SEARCHING
    ############################################################################
    def get_return_type(self):
        return self._return_type


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
        return self._function.get_return_type()


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
class LolScope(LolAnalysisObj):
    def __init__(
        self, name: str, outer_scope: Union["LolScope", None]
    ):
        """
        Params
        ------
        * name: str - name of the scope (e.g. name of the function)
        * outer_scope: LolScope | None - scope beyond this one. If None, then it
            is the outermost scope (i.e. the global scope).
        """
        super().__init__(name)
        # Symbols in the C namespace (NOTE: the struct, function, and variable
        # namespaces are all different in C, but we will keep them together).
        # This namespace is just to ensure there are no collisions (since we do
        # not allow name mangling).
        # TODO(dchu): eventually, we may want the type of each symbol here!
        self._c_namespace: Dict[str, SymbolSource] = {**C_KEYWORDS}
        # The symbol table is the set of usable names.
        self._symbol_table: Dict[str, LolAnalysisObj] = {}
        self._outer_scope = outer_scope

    def __repr__(self):
        return repr(self._symbol_table)

    def create_inner_scope(self, name: str) -> "LolScope":
        """
        Create a scope that nests within the current scope.

        By just deleting the inner scope once we are done with it, we may lose
        some valuable debugging information.

        E.g.
        ```
        let var_0: int = 0;
        if var_0 == 0 {
            let var_1: int = 1;
        }
        print(var_1);   // We want to tell the user that var_1 is _no longer_
                        // in scope!
        ```
        """
        return LolScope(name, self)

    def add_to_scope(
        self,
        name: str,
        obj: Union[LolDataType, LolDataVariable, LolFunction],
        *,
        source: SymbolSource = SymbolSource.USER,
    ):
        """Adds to scope if the symbol isn't already used; otherwise, it raises
        an error."""
        # Assert types are correct (just to make debugging easier). This is
        # important because we might have a Python str and a Token that are both
        # supposed to be the same thing, but due to the differing types, they
        # appear to be different. N.B. Tokens are not allowed in here!
        assert isinstance(name, str)
        assert isinstance(obj, (LolDataType, LolDataVariable, LolFunction))
        # Ensure names are not already used
        if name in self._c_namespace:
            msg = f"'{name}' already in C namespace '{self._c_namespace}'"
            raise ValueError(msg)
        if name in self._symbol_table:
            msg = f"'{name}' already in symbol table '{self._symbol_table}'"
            raise ValueError(msg)
        # Add to C and LOL namespaces
        self._c_namespace[name] = source
        self._symbol_table[name] = obj

    def add_function(
        self,
        name: str,
        ast_node: parser_types.FunctionDefinitionNode,
        *,
        source: SymbolSource = SymbolSource.USER,
    ):
        func = LolFunction(
            name=name,
            ast_node=ast_node,
        )
        self.add_to_scope(name, func, source=source)

    def add_variable(
        self,
        name: str,
        ast_node: parser_types.VariableDefinitionNode,
        *,
        source: SymbolSource = SymbolSource.USER,
    ):
        var = LolDataVariable(
            name=name,
            ast_node=ast_node,
            data_type=None,
        )
        self.add_to_scope(name, var, source=source)

    def search_scope(self, name: str, *, recursion_depth: int = 0):
        # If found, then return!
        if name in self._symbol_table:
            return name
        # If not found, then recurse
        if self._outer_scope is None:
            raise ValueError(f"unable to find {name} in any scope!")
        elif recursion_depth >= 32:
            raise ValueError(f"recursion depth is >=32. Infinite loop?")
        return self._outer_scope.search_scope(
            name, recursion_depth=recursion_depth + 1
        )

    def assert_contains(self, name: str):
        assert name in self._symbol_table


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

        # Module scope is the outermost scope
        self._scope = LolScope(name, outer_scope=None)

    def __repr__(self):
        return f"LolModule(scope={self._scope})"


    ############################################################################
    ### Add names to module
    ############################################################################
    def add_function_name(
        self, function_node: parser_types.FunctionDefinitionNode
    ):
        name = function_node.get_name_as_str()
        self._scope.assert_contains(name)
        self._scope.add_function(name, function_node, source=SymbolSource.USER)

    def add_variable_definition_name(
        self, var_def_node: parser_types.VariableDefinitionNode
    ):
        name = var_def_node.get_name_as_str()
        self._scope.add_variable(name, var_def_node, source=SymbolSource.USER)

    def add_submodule(self, submodule_node: parser_types.ImportModuleNode):
        # TODO - this should just import all recursively!
        name = submodule_node.get_name_as_str()
        submodule_name = submodule_node.get_library_as_str()
        if submodule_name == "stdio.h":
            self.include_stdio(name)
        else:
            # self.symbol_table[name] = Module(name, "")
            raise ValueError("general imports not supported!")

    ############################################################################
    ### Add prototypes to module
    ############################################################################

    def add_function_prototype(
        self, func_node: parser_types.FunctionDefinitionNode
    ):
        name = func_node.get_name_as_str()
        func = self._scope.search_scope(name)
        assert isinstance(func, LolFunction)
        func.add_prototype(self._scope, func_node)

    def add_variable_definition_prototype(
        self, variable_definition_node: parser_types.VariableDefinitionNode
    ):
        name = variable_definition_node.get_name_as_str()
        var_def = self._scope.search_scope(name)
        assert isinstance(var_def, LolDataVariable)
        var_def.add_data_type(
            parse_type_expression(
                variable_definition_node.get_data_type()
            )
        )

    ############################################################################
    # Add bodies
    ############################################################################
    def add_function_body(self, func_node: parser_types.FunctionDefinitionNode):
        name = func_node.get_name_as_str()
        func = self._scope.search_scope(name)
        assert isinstance(func, LolFunction)
        func.add_body(self._scope, func_node)

    def add_variable_definition_body(
        self, variable_definition_node: parser_types.VariableDefinitionNode
    ):
        name = variable_definition_node.get_name_as_str()
        var_def = self._scope.search_scope(name)
        assert isinstance(var_def, LolDataVariable)
        var_def.add_init_value(variable_definition_node.get_value())



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
