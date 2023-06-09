from typing import Dict, List, Set
from enum import auto, Enum, unique

from prototype.error.lol_error import print_analyzer_error

from prototype.lexer.lol_lexer_types import Token
from prototype.parser.lol_parser import ASTNode, FunctionDefNode, ImportNode, DefinitionNode
from prototype.analyzer.types import Obj, DataType, DataVar, Function, Module


### HELPER FUNCTIONS
def extract_module_names(ast_nodes: List[ASTNode], raw_text: str) -> Module:
    """
    Extract names (only) of function definitions, global definitions, and
    imports.

    TODO
    ----
    1. Add struct/enum/monad
    """
    module = Module("__main__", raw_text)

    for i, node in enumerate(ast_nodes):
        if isinstance(node, FunctionDefNode):
            module.add_func_name(node)
        elif isinstance(node, DefinitionNode):
            module.add_defn_name(node)
        elif isinstance(node, ImportNode):
            # TODO(dchu) - recursively add members to this submodule!
            module.add_submod(node)
        # TODO(dchu): accept data structures
        else:
            # We will ignore anything outside of functions! This is an error
            raise ValueError(f"{node} cannot be outside of functions!")
    return module


def get_prototypes(module: Module, ast_nodes: List[ASTNode], raw_text: str):
    for i, node in enumerate(ast_nodes):
        if isinstance(node, FunctionDefNode):
            module.add_func_proto(node)
        elif isinstance(node, DefinitionNode):
            module.add_defn_proto(node)
        elif isinstance(node, ImportNode):
            pass
        else:
            # We will ignore anything outside of functions! This is an error
            raise ValueError(f"{node} cannot be outside of functions!")


def get_bodies(module: Module, ast_nodes: List[ASTNode], raw_text: str):
    for i, node in enumerate(ast_nodes):
        if isinstance(node, FunctionDefNode):
            module.add_func_body(node)
        elif isinstance(node, DefinitionNode):
            module.add_defn_body(node)
        elif isinstance(node, ImportNode):
            pass
        else:
            # We will ignore anything outside of functions! This is an error
            raise ValueError(f"{node} cannot be outside of functions!")

def analyze(asts: List[ASTNode], raw_text: str) -> Dict[str, Obj]:
    # Get names for functions, etc
    module: Module = extract_module_names(asts, raw_text)
    # Get prototypes for functions
    get_prototypes(module, asts, raw_text)

    return module
