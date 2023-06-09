from abc import ABCMeta
from enum import Enum, auto, unique
from typing import Any, Dict, List, Set, Tuple, Union

from parser.lol_parser_types import (
    FunctionDefNode,
    DefinitionNode,
    ImportNode,
    ASTNode,
    IdentifierLeaf,
    BinOpNode,
    ReturnNode,
    FunctionCallNode,
)

@unique
class COpType(Enum):
    CALL = auto()   # <op>(<args>, ...), e.g. func_name(x, y, z)
    ACCESS = auto() # <op>[<args>], e.g. array_name[x]
    PREFIX = auto() # <op><arg>, e.g. +x
    INFIX = auto()  # <arg0> <op> <arg1>, e.g. x+y
    SUFFIX = auto() # <arg><op>, e.g. x++


@unique
class SymbolSource(Enum):
    C_STDLIB = auto()
    C_BUILTIN = auto()
    LOL_BUILTIN = auto()
    USER = auto()


################################################################################
### BUILTINS
################################################################################


class Obj(metaclass=ABCMeta):
    def __init__(self, name: str, alt_c_name: Union[str, None]):
        self.name = name
        self.c_name = alt_c_name if alt_c_name is not None else name


class DataType(Obj):
    def __init__(self, name: str, alt_c_name: str = None):
        super().__init__(name, alt_c_name)
        self.functions: Dict[str, "Function"] = {}

    def __repr__(self):
        return f"{self.name}"

    def add_function(self, func: "Function"):
        self.functions[func.name] = func


class DataVar(Obj):
    def __init__(
        self,
        name: str,
        data_type: DataType = None, # Is unknown at
        init_value: Any = None,
        *,
        alt_c_name: str = None,             # Use name unless otherwise specified
        is_mut: bool = False,           # Opposite of C's const
        is_unrestricted: bool = False,  # Opposite of C's restrict
        is_volatile: bool = False,      # Equivalent to C's volatile
    ):
        super().__init__(name, alt_c_name)
        self.data_type = data_type
        self.init_value = init_value

        self.is_mut = is_mut
        self.is_unrestricted = is_unrestricted
        self.is_volatile = is_volatile

    def __repr__(self):
        return f"{self.name}: {self.data_type} = {self.init_value}"

    def add_data_type(self, data_type: DataType):
        self.data_type = data_type

    def add_init_value(self, init_value: Any):
        self.init_value = init_value


class Function(Obj):
    def __init__(
        self,
        name: str,
        params: List[DataVar] = None,   # DEPRECATED?
        return_type: DataType = None,   # DEPRECATED?
        *,
        alt_c_name: str = None,
        c_op_type: COpType = COpType.CALL,
        is_builtin_c: bool = None,      # If so, do not perform checks yet...
        is_pure: bool = None,
        is_public: bool = None,
    ):
        super().__init__(name, alt_c_name)
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

    def add_params(self, params: List[DataVar]):
        if self.params is not None:
            raise ValueError("trying to overwrite params")
        self.params = params

    def add_return_type(self, return_type: DataType):
        if self.return_type is not None:
            raise ValueError("trying to overwrite return_type")
        self.return_type = return_type

    def add_body(self) -> "Function":
        if self.is_builtin_c:
            raise ValueError("trying to add body to built in function!")
        return self


class Module(Obj):
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
        # The package?
        super().__init__(name, "")
        # Raw text is simply for debugging!
        self.raw_text: str = raw_text
        # C Standard Library Headers to Include
        # I will include the angled brackets or quotations since it is not
        # immediately obvious whether to use brackets or quotes otherwise.
        self.c_includes: List[str] = []
        # Symbols in the C namespace (NOTE: the struct, function, and variable
        # namespaces are all different in C, but we will keep them together).
        # This namespace is just to ensure there are no collisions (since we do
        # not allow name mangling).
        self.c_namespace: Dict[str, SymbolSource] = {}
        # The symbol table is the set of usable names.
        self.symbol_table: Dict[str, Obj] = {}

        # Add C and LOL builtins to C namespace and symbol table
        self.add_c_keywords()
        if name == "__main__":
            self.add_lol_builtins()

    def __repr__(self):
        return repr(self.symbol_table)

    def add_c_keywords(self):
        """Add to list of used symbols (up to and including C99 standard)."""
        c89_keywords = {
            "auto": SymbolSource.C_BUILTIN,
            "break": SymbolSource.C_BUILTIN,
            "case": SymbolSource.C_BUILTIN,
            "char": SymbolSource.C_BUILTIN,
            "const": SymbolSource.C_BUILTIN,
            "continue": SymbolSource.C_BUILTIN,
            "default": SymbolSource.C_BUILTIN,
            "do": SymbolSource.C_BUILTIN,
            "double": SymbolSource.C_BUILTIN,
            "else": SymbolSource.C_BUILTIN,
            "enum": SymbolSource.C_BUILTIN,
            "extern": SymbolSource.C_BUILTIN,
            "float": SymbolSource.C_BUILTIN,
            "for": SymbolSource.C_BUILTIN,
            "goto": SymbolSource.C_BUILTIN,
            "if": SymbolSource.C_BUILTIN,
            "int": SymbolSource.C_BUILTIN,
            "long": SymbolSource.C_BUILTIN,
            "register": SymbolSource.C_BUILTIN,
            "return": SymbolSource.C_BUILTIN,
            "short": SymbolSource.C_BUILTIN,
            "signed": SymbolSource.C_BUILTIN,
            "sizeof": SymbolSource.C_BUILTIN,
            "static": SymbolSource.C_BUILTIN,
            "struct": SymbolSource.C_BUILTIN,
            "switch": SymbolSource.C_BUILTIN,
            "typedef": SymbolSource.C_BUILTIN,
            "union": SymbolSource.C_BUILTIN,
            "unsigned": SymbolSource.C_BUILTIN,
            "void": SymbolSource.C_BUILTIN,
            "volatile": SymbolSource.C_BUILTIN,
            "while": SymbolSource.C_BUILTIN,
        }
        c99_keywords = {
            "inline": SymbolSource.C_BUILTIN,
            "restrict": SymbolSource.C_BUILTIN,
            "_Bool": SymbolSource.C_BUILTIN,
            "_Complex": SymbolSource.C_BUILTIN,
            "_Imaginary": SymbolSource.C_BUILTIN,
        }
        self.c_namespace.update(c89_keywords)
        self.c_namespace.update(c99_keywords)

    def add_lol_builtins(self):
        """
        NOTE: this adds these to only the top level module. We can only run
        this function once--otherwise, there will be duplicate int32 objects.
        """
        self.symbol_table["int32"] = DataType("int32", alt_c_name="int")
        self.symbol_table["str"] = DataType("str", alt_c_name="char *")

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
        self.symbol_table[name] = Function(name, is_builtin_c=True)

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
        stdio_namespace = Module(lol_alias, self.raw_text)
        stdio_namespace.add_builtin_func("printf")
        self.symbol_table[lol_alias] = stdio_namespace

    ############################################################################
    ### Add names to module
    ############################################################################
    def add_func_name(self, func_node: FunctionDefNode):
        name = func_node.prototype.name.token.lexeme
        if name in self.c_namespace:
            raise ValueError(f"name '{name}' already in C namespace '{self.c_namespace}'")
        if name in self.symbol_table:
            raise ValueError(f"name '{name}' already in symbol table '{self.symbol_table}'")
        self.c_namespace[name] = SymbolSource.USER
        self.symbol_table[name] = Function(name)

    def add_defn_name(self, defn_node: DefinitionNode):
        name = defn_node.get_identifier().token.lexeme
        if name in self.c_namespace:
            raise ValueError(f"name '{name}' already in C namespace '{self.c_namespace}'")
        if name in self.symbol_table:
            raise ValueError(f"name '{name}' already in symbol table '{self.symbol_table}'")
        self.c_namespace[name] = SymbolSource.USER
        self.symbol_table[name] = DataVar(name)

    def add_submod(self, submod_node: ImportNode):
        # TODO - this should just import all recursively!
        name = submod_node.name.token.lexeme
        submod_name = submod_node.expression.value
        if name in self.symbol_table:
            raise ValueError(
                f"name '{name}' already in "
                f"symbol table '{self.symbol_table}'"
            )
        if submod_name == "stdio.h":
            self.include_stdio(name)
        else:
            # self.symbol_table[name] = Module(name, "")
            raise ValueError("general imports not supported!")


    ############################################################################
    ### Add prototypes to module
    ############################################################################
    def _parse_type_expr(self, type_expr: ASTNode):
        if isinstance(type_expr, IdentifierLeaf):
            name = type_expr.token.lexeme
            if name not in self.symbol_table:
                raise ValueError(f"type '{name}' not in symbol table '{self.symbol_table}'")
            result = self.symbol_table[name]
            assert isinstance(result, DataType)
        else:
            raise ValueError(f"type '{type(type_expr)}' is unsupported")

    def add_func_proto(self, func_node: FunctionDefNode):
        name = func_node.prototype.name.token.lexeme
        assert name in self.symbol_table and isinstance(
            self.symbol_table[name], Function
        )
        func: Function = self.symbol_table[name]
        func.add_params(
            [
                DataVar(
                    name=defn_node.get_identifier().token.lexeme,
                    # TODO(dchu) - parse these values somehow
                    data_type=self._parse_type_expr(defn_node.get_type()),
                )
                for defn_node in func_node.prototype.parameters
            ]
        )
        func.add_return_type(self._parse_type_expr(func_node.prototype.return_type))

    def add_defn_proto(self, defn_node: DefinitionNode):
        name = defn_node.get_identifier().token.lexeme
        assert name in self.symbol_table and isinstance(
            self.symbol_table[name], Function
            )
        func: Function = self.symbol_table[name]

    ############################################################################
    # Add bodies
    ############################################################################
    def add_func_body(self, func_node: FunctionDefNode):
        # TODO - check func_node's name exists in symbol table. Add body statements to function
        name = func_node.prototype.name.token.lexeme
        assert name in self.symbol_table and isinstance(
            self.symbol_table[name], Function
        )
        func: Function = self.symbol_table[name]

        body: List[Statement] = []
        var_counter = 0
        for i, statement in func_node.body:
            if isinstance(statement, DefinitionNode):
                body.append(
                    Statement()
                )
            elif isinstance(statement, BinOpNode):
                pass
            elif isinstance(statement, FunctionCallNode):
                pass
            elif isinstance(statement, ReturnNode):
                body.append(ReturnStatement())
            else:
                raise ValueError(f"unsupported statement {statement}")

################################################################################
### USAGES
################################################################################


class Expression:
    def __init__(self):
        pass


class FuncCallExpr(Expression):
    def __init__(self, function: Function, args: List[Expression]):
        super().__init__()
        self.function = function
        self.args = args

    def get_return_type(self) -> DataType:
        return self.function.return_type


class OpExpr(Expression):
    def __init__(self, op: Function, args: List[Expression], c_op_type: COpType):
        super().__init__()
        self.op = op
        self.args = args
        self.c_op_type = c_op_type

    def get_return_type(self) -> DataType:
        return self.op.return_type


################################################################################


class Statement:
    def __init__(self):
        pass


class SetStatement(Statement):
    """<lvalue> = <expr>"""
    def __init__(self, lvalue: DataVar, rhs_expr: Expression):
        super().__init__()
        self.lvalue = lvalue
        self.expr = rhs_expr


class ReturnStatement(Statement):
    def __init__(self, expr: Expression):
        super().__init__()
        self.expr = expr

################################################################################
### BUILTINS
################################################################################

# TODO
# ====
# 1. Move builtins to separate file
# 2. blah

# Data Types
lol_int64 = DataType("int32", alt_c_name="int")
lol_str = DataType("str", alt_c_name="char *")
lol_bool = DataType("bool", alt_c_name="int")
lol_void = DataType("void")

# Placeholder Variables
unnamed_lol_int64 = DataVar(None, lol_int64, None)
unnamed_lol_str = DataVar(None, lol_str, None)

# Functions
lol_printf = Function(
    "printf",
    [unnamed_lol_str],
    lol_int64,
    is_builtin_c=True,
)

builtins: Dict[str, Any] = {
    "int32": lol_int64,
    "string": lol_str,
    "bool": lol_bool,
}

includes: Set[str] = {
    "stdio.h"
}

lol_int64.add_function(Function("+", [unnamed_lol_int64, unnamed_lol_int64], lol_int64, alt_c_name="+", is_builtin_c=True, c_op_type=COpType.INFIX))
lol_int64.add_function(Function("-", [unnamed_lol_int64, unnamed_lol_int64], lol_int64, alt_c_name="-", is_builtin_c=True, c_op_type=COpType.INFIX))
