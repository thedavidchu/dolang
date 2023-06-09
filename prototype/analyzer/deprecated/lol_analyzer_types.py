"""Types to aid with type analysis.

TODO
----
1. Deprecate value in VariableDef
2. Create smarter way for dealing with binary ops
"""


import warnings
from abc import ABCMeta, abstractmethod
from typing import Any, Dict, List, Tuple, Union
from enum import Enum, auto, unique

from lexer.lol_lexer_types import Token


# TODO: make this not a floating constant
_INDENT: str = "    "


################################################################################
### ABSTRACT CLASSES
################################################################################


class AnalysisObj(metaclass=ABCMeta):
    """
    TODO
    ----
    1. Create mangle method
    2. Create generic methods
    """

    @abstractmethod
    def __repr__(self) -> str:
        raise NotImplementedError("abc")

    @abstractmethod
    def emit_c_def(self, indentation_level: int = 0) -> str:
        raise NotImplementedError("abc")

    @abstractmethod
    def emit_c_ref(self, indentation_level: int = 0) -> str:
        raise NotImplementedError("abc")


@unique
class DataTypeType(Enum):
    """The type of a type."""
    PRIMITIVE = auto()
    STRUCT = auto()
    ENUM = auto()
    MONAD = auto()
    if False:   # NOT IMPLEMENTED
        GENERIC_STRUCT = auto()
        GENERIC_ENUM = auto()
        GENERIC_MONAD = auto()
        FUNCTION = auto()
        GENERIC_FUNCTION = auto()
        NAMESPACE = auto()


@unique
class OpType(Enum):
    """The type of an operator."""
    PREFIX = auto()
    INFIX = auto()
    SUFFIX = auto()


################################################################################
### CONCRETE CLASSES
################################################################################


class DataTypeObj(AnalysisObj):
    """
    Define or refer to a data type. This data type can be a structure, enum, or
    monad (which is a combination of an enum and a C union in my implementation)

    Operations
    ----------
    * <type>(<args>)    : Initialization
    * <type>::<name>    : Namespace
    * <type>.<name>     : Namespace (same as :: maybe?)
    * <type> == <type>  : Type equality
    * <type> != <type>  : Type inequality
    * <type> | <type>   : Type union
    * <type> & <type>   : Type intersection
    * <type> - <type>   : Type difference
    * <type>[<args>]    : Type refinement
    """
    def __init__(
        self,
        name: str,
        type: DataTypeType,
        attr: Dict[str, Union["DataTypeObj", "FuncObj", "VarObj"]],
    ) -> None:
        self.name = name
        self.type = type
        if type == DataTypeType.PRIMITIVE:
            assert attr == {}
        else:
            # TODO(dchu): add support for type fields, as in structs
            self.attr: Dict[str, "DataTypeObj"] = attr

    def __repr__(self) -> str:
        return f"TypeDefinition({self.name}, {self.type.name})"

    def emit_c_def(self, indentation_level: int = 0) -> str:
        start = indentation_level * _INDENT + f"struct {self.name} {{"
        middle = [
            f"{type_ref.emit_c(indentation_level + 1)} {name};"
            for name, type_ref in self.attr.items()
        ]
        end = indentation_level * _INDENT + "};\n"
        return "\n".join([start, *middle, end])

    def emit_c_ref(self, indentation_level: int = 0) -> str:
        return f"{indentation_level * _INDENT}{self.name}"

    def add_func(self, func: "FuncObj") -> None:
        pass


class OpObj(AnalysisObj):
    """
    Op calls are built-in only for now, since we do not support operator
    overloading.

    These operators are ones that run at runtime, such as '+', '-', etc.

    These do not include compile-time operators, such as '.' or '::'.
    """

    def __init__(
        self,
        op: str,
        c_op_type: OpType,
        args: List[DataTypeObj],
        return_type: DataTypeObj,
    ):
        self.name = op
        self.c_op_type = c_op_type
        self.args = None
        self.return_type = return_type



class FuncObj(AnalysisObj):
    def __init__(
        self,
        name: str,
        # TODO(dchu): add default value
        arguments: List[Tuple[str, DataTypeObj]],
        return_type: DataTypeObj,
        # NOTE: this produces a function prototype by default
        body: Union[str, List[AnalysisObj]] = ";",
    ) -> None:
        self.name = name
        self.return_type = return_type
        self.arguments = arguments
        self.body = body

    def __repr__(self) -> str:
        return f"Function({self.name}({', '.join(self.arguments)}) -> {self.return_type})"

    def emit_c_def(self, indentation_level: int = 0) -> str:
        prototype = f"{self.return_type.emit_c_ref()} {self.name}"
        params = "(" + ", ".join([f"{t} {name}" for name, t in self.arguments]) + ")"
        return prototype + params + self.body


class NamespaceObj:
    def __init__(
        self,
        name: str,
        namespace: Dict[str, Union["DataTypeObj", "NamespaceObj", "VarObj", FuncObj]],
    ) -> None:
        self.name = name
        self.namespace = namespace

    def add_to_namespace(
        self, name: str, var: Union["DataTypeObj", "NamespaceObj", "VarObj", FuncObj]
    ) -> None:
        if name in self.namespace:
            raise ValueError(f"this namespace already contains value {var}")
        self.namespace[name] = var

    def __repr__(self) -> str:
        return f"Namespace({self.namespace})"


class VarObj(AnalysisObj):
    """
    Give the definition of a variable.

    TODO
    ----
    1.
    """
    def __init__(self, name: str, type: DataTypeObj, value: Any = None) -> None:
        self.name = name
        self.type = type
        self.value = value

    def __repr__(self) -> str:
        if self.value is not None:
            return f"VariableDef({self.name}: {self.type} = {self.value})"
        return f"VariableDef({self.name}: {self.type})"

    def emit_c_def(self, indentation_level: int = 0) -> str:
        return f"{self.type.emit_c_ref(indentation_level)} {self.name};\n"

    def emit_c_ref(self, indentation_level: int = 0) -> str:
        return f"{self.name}"


################################################################################
### PROGRAMMING CONCEPTS
################################################################################


class FuncDef:
    def __init__(self, name: Token, args: List[Any], return_type: DataTypeObj):
        self.name = name
        self.args = args
        self.return_type = return_type

    # def emit_c_def(self) -> str:
    #     # TODO(dchu): add support for name mangling
    #     return f"{self._return_type.emit_c_ref()} {self._name}({','.join()})"



################################################################################
### BUILTIN THINGS
################################################################################

global_namespace = NamespaceObj(
    "global",
    {
        "int64": DataTypeObj("int64", DataTypeType.PRIMITIVE, {"+": None})
    },
)
