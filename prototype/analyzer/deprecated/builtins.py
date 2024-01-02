# from typing import Dict, Union
#
# from analyzer.lol_analyzer_types import TypeDef, FunctionDef
#
#
# def create_builtin_type():
#     namespace_type = TypeDef("namespace")
#     int_type = TypeDef("int")
#     bool_type = TypeDef("bool")
#     float_type = TypeDef("float")
#     str_type = TypeDef("str")
#
#     # Create int ops
#     int_type.add_binop("+", int_type, int_type)
#     int_type.add_binop("-", int_type, int_type)
#     int_type.add_binop("*", int_type, int_type)
#     int_type.add_binop("/", int_type, int_type)
#
#     int_type.add_binop("<", int_type, bool_type)
#     int_type.add_binop("<=", int_type, bool_type)
#     int_type.add_binop("==", int_type, bool_type)
#     int_type.add_binop("!=", int_type, bool_type)
#     int_type.add_binop(">=", int_type, bool_type)
#     int_type.add_binop(">", int_type, bool_type)
#
# BUILTINS: Dict[str, Union[TypeDef, FunctionDef]] = {
#     "int": TypeDef("int")
# }
