"""
Take the AST and emit C code.

TODO
----

1. Minimal Viable Product
2. Correct indentation
"""
from typing import List
from compiler.analyzer.lol_analyzer import (
    LolAnalysisModule, LolAnalysisFunction, LolAnalysisBuiltinType,
    LolIRReturnStatement, LolIRFunctionCallStatement, LolIRDefinitionStatement, LolIRSetStatement, LolIRIfStatement,
    LolIRExpression, LolIRStatement,
    LolIRFunctionCallExpression, LolIROperatorExpression, LolIRLiteralExpression, LolAnalysisVariable
)

headers = """
#include <stdint.h>
#include <stdio.h>
"""

lol_to_c_types = {"cstr": "char *", "i32": "int", "void": "void"}


def mangle_var_name(var_name: str) -> str:
    return var_name.replace("%", "LOLvar_")


def emit_expr(expr: LolIRExpression) -> str:
    if isinstance(expr, LolIRFunctionCallExpression):
        func_name = expr.function.name
        func_args = [mangle_var_name(arg.name) for arg in expr.arguments]
        return f"{func_name}({', '.join(func_args)})"
    elif isinstance(expr, LolIROperatorExpression):
        if len(expr.operands) == 1:
            return f"{expr.op}{mangle_var_name(expr.operands[0].name)}"
        elif len(expr.operands) == 2:
            if expr.op in {"or", "and"}:
                expr_op = {"or": "||", "and": "&&"}.get(expr.op)
            else:
                expr_op = expr.op
            return f"{mangle_var_name(expr.operands[0].name)} {expr_op} {mangle_var_name(expr.operands[1].name)}"
        else:
            raise ValueError("only 1 or 2 operands accepted!")
    elif isinstance(expr, LolIRLiteralExpression):
        literal = expr.literal
        if isinstance(literal, str):
            return f"\"{literal}\""
        elif isinstance(literal, int):
            return f"{expr.literal}"
    elif isinstance(expr, LolAnalysisVariable):
        return f"{mangle_var_name(expr.name)}"


def emit_statements(
    ir_statements: List[LolIRStatement],
    *,
    indentation: str = "    "
) -> List[str]:
    statements: List[str] = []
    for stmt in ir_statements:
        if isinstance(stmt, LolIRDefinitionStatement):
            var_name = mangle_var_name(stmt.name)
            var_type = lol_to_c_types[stmt.type.name]
            var_value = emit_expr(stmt.value)
            statements.append(indentation + f"{var_type} {var_name} = {var_value};")
        elif isinstance(stmt, LolIRSetStatement):
            var_name = mangle_var_name(stmt.name)
            var_value = emit_expr(stmt.value)
            statements.append(indentation + f"{var_name} = {var_value};")
        elif isinstance(stmt, LolIRFunctionCallStatement):
            code = emit_expr(stmt.func_call)
            statements.append(indentation + f"{code};")
        elif isinstance(stmt, LolIRReturnStatement):
            name = mangle_var_name(stmt.ret_var.name)
            statements.append(indentation + f"return {name};")
        elif isinstance(stmt, LolIRIfStatement):
            statements.append(indentation + f"if ({mangle_var_name(stmt.if_cond.name)}) {{")
            statements.extend(emit_statements(stmt.if_body, indentation=indentation + "    "))
            statements.append(indentation + "} else {")
            statements.extend(emit_statements(stmt.else_body, indentation=indentation + "    "))
            statements.append(indentation + "}")
        else:
            raise ValueError("unrecognized statement type (maybe if statement?)")
    return statements

def emit_function(func: LolAnalysisFunction):
    prototype = (
        f"{lol_to_c_types[func.return_types.name]}\n"
        f"{func.name}({', '.join((f'{lol_to_c_types[arg_type.name]} {arg_name}' for arg_type, arg_name in zip(func.parameter_types, func.parameter_names)))})\n"
    )
    statements = emit_statements(func.body)

    return prototype + "{\n" + "\n".join(statements) + "\n}\n"


def emit_import(include: LolAnalysisModule):
    return f"#include <{include.name[1:-1]}>"


def emit_c(analysis_module: LolAnalysisModule):
    import_statements = []
    func_statements = []
    # Emit modules
    for name, s in analysis_module.module_symbol_table.items():
        if isinstance(s, LolAnalysisModule):
            import_statements.append(emit_import(s))
        elif isinstance(s, LolAnalysisFunction):
            func_statements.append(emit_function(s))
        elif isinstance(s, LolAnalysisBuiltinType):
            # Obviously, we don't need to define built-in types
            continue
        else:
            raise ValueError("unrecognized statement type")

    statements = import_statements + func_statements
    code = "\n".join(statements)
    print(code)
    return code
