from typing import Dict, List

from compiler.analyzer.lol_analyzer_types import (
    LolAnalysisObj,
    LolModule,
)
from compiler.parser.lol_parser import (
    ASTNode,
    FunctionDefinitionNode,
    ImportModuleNode,
    VariableDefinitionNode,
)


### HELPER FUNCTIONS
def extract_names_in_module(
    ast_nodes: List[ASTNode], raw_text: str
) -> LolModule:
    """
    Extract names (only) of function definitions, global definitions, and
    imports.

    TODO
    ----
    1. Add struct/enum/monad
    """
    module = LolModule("", raw_text)

    for i, node in enumerate(ast_nodes):
        if isinstance(node, FunctionDefinitionNode):
            module.add_function_name(node)
        elif isinstance(node, VariableDefinitionNode):
            module.add_variable_definition_name(node)
        elif isinstance(node, ImportModuleNode):
            # TODO(dchu) - recursively add members to this submodule!
            module.add_submodule(node)
        # TODO(dchu): accept data structures
        else:
            # We will ignore anything outside of functions! This is an error
            raise ValueError(f"{node} cannot be outside of functions!")
    return module


def get_prototypes(module: LolModule, ast_nodes: List[ASTNode], raw_text: str):
    """Get function and variable prototypes."""
    for i, node in enumerate(ast_nodes):
        if isinstance(node, FunctionDefinitionNode):
            module.add_function_prototype(node)
        elif isinstance(node, VariableDefinitionNode):
            module.add_variable_definition_prototype(node)
        elif isinstance(node, ImportModuleNode):
            pass
        else:
            # We will ignore anything outside of functions! This is an error
            raise ValueError(f"{node} cannot be outside of functions!")


def get_bodies(module: LolModule, ast_nodes: List[ASTNode], raw_text: str):
    for i, node in enumerate(ast_nodes):
        if isinstance(node, FunctionDefinitionNode):
            module.add_function_body(node)
        elif isinstance(node, VariableDefinitionNode):
            module.add_variable_definition_body(node)
        elif isinstance(node, ImportModuleNode):
            pass
        else:
            # We will ignore anything outside of functions! This is an error
            raise ValueError(f"{node} cannot be outside of functions!")


def analyze(asts: List[ASTNode], raw_text: str) -> Dict[str, LolAnalysisObj]:
    # Get names for functions, etc
    module: LolModule = extract_names_in_module(asts, raw_text)
    # Get prototypes for functions
    get_prototypes(module, asts, raw_text)

    return module
