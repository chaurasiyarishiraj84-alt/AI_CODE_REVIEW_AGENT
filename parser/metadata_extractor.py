"""Compute cyclomatic complexity and other metadata for AST nodes."""

from __future__ import annotations

import ast


def extract_complexity(node: ast.AST) -> int:
    """Estimate cyclomatic complexity of a function node."""
    complexity = 1
    branch_nodes = (
        ast.If, ast.For, ast.While, ast.ExceptHandler,
        ast.With, ast.Assert, ast.BoolOp,
        ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp,
    )
    for child in ast.walk(node):
        if isinstance(child, branch_nodes):
            complexity += 1
    return complexity