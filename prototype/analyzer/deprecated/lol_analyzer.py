"""
Analyze Abstract Syntax Trees
=============================

SIMPLIFICATIONS
---------------
1. No name mangling
    - No check to make sure mangled names don't conflict
    - No code to generate mangling (I'm not sure if it's even correct)
2. No generics
    - Symptom of no mangling

TODO
----
1. Validate correct syntax
2. Create list of global symbol names
    - Verify no names conflict with C standard library
    - Verify all names have reference
3. Ensure only public functions are referenced
4. Mangle names correctly
    - Only non-external names can be mangled (i.e. invisible to linker)
    - Mangled names are from: object oriented code, namespaces
    - But then what if you want a library of generics?
5. Expressions should not have side effects
    - The only '=' should have side effects... oh but what about function calls?
"""

from typing import Any, Dict, List, Set
from lol_lexer import Token
from lol_parser_types import (
    ASTNode,
    FunctionDefinitionNode,
    ImportNode,
    DefinitionNode,
    FunctionPrototypeNode,
    BinOpNode,
    LiteralLeaf,
    FunctionCallNode,
    ReturnNode,
)
from lol_error import print_analyzer_error

from lol_analyzer_types import FunctionDef, TypeDef, VarObj, NamespaceDef

IO_NAMESPACE: Dict[str, str] = {
    "print": "printf",
}

STANDARD_LIBRARIES: Dict[str, Any] = {"io": IO_NAMESPACE}


def is_valid_name(text: str, token: Token) -> bool:
    """Disallow double underscores and leading/trailing underscores."""
    name = token.lexeme
    if "__" in name or name.startswith("_") or name.endswith("_"):
        return False
    return True


def ensure_unique_namespaces(
    text: str, asts: List[ASTNode]
) -> Dict[str, ASTNode]:
    """Get namespace names and ensure they are unique."""
    result = {}
    for ast in asts:
        if not isinstance(ast, ImportNode):
            continue
        name_token = ast.identifier
        name = name_token.token.lexeme
        if name in result:
            error_msg = "name already defined in module!"
            print_analyzer_error(text, name_token.token, error_msg)
            raise ValueError(error_msg)
        result[name] = ast.expression
    return result


def ensure_unique_variables(
    text: str, asts: List[ASTNode]
) -> Dict[str, ASTNode]:
    """Get module-level variable names and ensure they are unique."""
    result = {}
    for ast in asts:
        if not isinstance(ast, DefinitionNode):
            continue
        name_token = ast.identifier
        name = name_token.token.lexeme
        if name in result:
            error_msg = "name already defined in module!"
            print_analyzer_error(text, name_token.token, error_msg)
            raise ValueError(error_msg)
        result[name] = ast.expression
    return result


def get_function_names(
    text: str, asts: List[ASTNode]
) -> Dict[str, FunctionPrototypeNode]:
    """Get function names and ensure they are unique."""
    result = {}
    for ast in asts:
        if not isinstance(ast, FunctionDefinitionNode):
            continue
        name_token = ast.prototype.identifier
        name = name_token.token.lexeme
        if name in result:
            error_msg = "name already defined in module!"
            print_analyzer_error(text, name_token.token, error_msg)
            raise ValueError(error_msg)
        result[name] = ast.prototype
    return result


def get_expression_type(text: str, ast: ASTNode) -> str:
    # TODO
    # 1.
    if isinstance(ast, BinOpNode):
        op = ast.op.token.lexeme
        if op in {""}:
            pass
    elif isinstance(ast, FunctionCallNode):
        pass


def analyze_function(
    text: str,
    functions: Dict[str, FunctionPrototypeNode],
    namespaces: Dict[str, ASTNode],
    global_var: Dict[str, ASTNode],
    func_def: FunctionDefinitionNode,
) -> None:
    body = func_def.body
    local_var: Dict[str, ASTNode] = {}
    for j, statement in enumerate(body):
        if isinstance(statement, DefinitionNode):
            # TODO
            # 1. Check if already defined locally
            # 2. Check if shadows global variable (if so, warn!)
            # 3. Add to local var
            name_token = statement.identifier
            name = name_token.token.lexeme
            if name in local_var:
                # TODO(dchu): allow rewriting?
                error_msg = "local variable already defined locally"
                print_analyzer_error(text, name_token, error_msg)
                raise ValueError(error_msg)
            if name in global_var:
                error_msg = "WARNING: local variable already defined globally"
                print_analyzer_error(text, name_token, error_msg)
                # This is not a fatal error to overwrite a global variable
            expr = statement.expression
            # TODO(dchu): analyze expression
            local_var[name] = expr
        elif isinstance(statement, BinOpNode):
            # TODO(dchu): refactor this out so we can reuse this!
            op = statement.op
            lhs = statement.lhs
            rhs = statement.rhs
            type_lhs = get_expression_type(lhs)
            type_rhs = get_expression_type(rhs)
            assert type_lhs != type_rhs

            pass
        elif isinstance(statement, FunctionCallNode):
            pass
        elif isinstance(statement, ReturnNode):
            pass
        elif isinstance(statement, LiteralLeaf):
            # This is just a random literal without anything acting on it.
            continue
        else:
            # TODO(dchu): accept new scopes, if/else, while, for, do-while, etc.
            raise ValueError("not yet accepted!")


def analyze_module(text: str, asts: List[ASTNode]) -> None:
    """Analyze module for namespace and type compliance."""
    global_var_names = ensure_unique_variables(text, asts)
    namespace_names = ensure_unique_namespaces(text, asts)
    func_names = get_function_names(text, asts)
    print(global_var_names)
    print("---")
    print(namespace_names)
    print("---")
    print(func_names)
    print("---")

    # Hoist functions to the top.
    functions: Dict[str, FunctionPrototypeNode] = func_names
    # Only include namespaces and global var for the rest of the file
    namespaces: Dict[str, ASTNode] = {}
    global_var: Dict[str, ASTNode] = {}
    for i, ast in enumerate(asts):
        if isinstance(ast, ImportNode):
            name = ast.identifier.token.lexeme
            expr = ast.expression
            # Assume namespace is unique since we checked for it above.
            assert name not in namespaces
            namespaces[name] = expr
        elif isinstance(ast, DefinitionNode):
            name = ast.identifier.token.lexeme
            expr = ast.expression
            # Assume global variable is unique since we checked for it above.
            assert name not in global_var
            global_var[name] = expr
        elif isinstance(ast, FunctionDefinitionNode):
            analyze_function(text, functions, namespaces, global_var, ast)

