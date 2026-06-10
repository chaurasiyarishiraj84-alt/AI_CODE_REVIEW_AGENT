"""Extract Python code entities (functions, classes, imports) via AST."""

from __future__ import annotations

import ast
from typing import Any, Dict, List

from app.logger import get_logger
from parser.metadata_extractor import extract_complexity

logger = get_logger(__name__)


def _get_docstring(node: ast.AST) -> str:
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
        return ast.get_docstring(node) or ""
    return ""


def _collect_imports(tree: ast.Module) -> List[str]:
    imports: List[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                imports.append(f"{module}.{alias.name}")
    return imports


def parse_python_file(source: str, filepath: str = "<unknown>") -> Dict[str, Any]:
    """Parse Python source and return a structured metadata dict."""
    entities: List[Dict[str, Any]] = []

    try:
        tree = ast.parse(source, filename=filepath)
    except SyntaxError as exc:
        logger.warning("SyntaxError in %s: %s", filepath, exc)
        return {
            "source": source,
            "language": "python",
            "entities": [],
            "imports": [],
            "parse_error": str(exc),
        }

    imports = _collect_imports(tree)

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            entities.append({
                "type": "function",
                "name": node.name,
                "lineno": node.lineno,
                "end_lineno": getattr(node, "end_lineno", node.lineno),
                "docstring": _get_docstring(node),
                "complexity": extract_complexity(node),
                "is_async": isinstance(node, ast.AsyncFunctionDef),
            })
        elif isinstance(node, ast.ClassDef):
            entities.append({
                "type": "class",
                "name": node.name,
                "lineno": node.lineno,
                "end_lineno": getattr(node, "end_lineno", node.lineno),
                "docstring": _get_docstring(node),
                "bases": [ast.unparse(b) for b in node.bases],
            })

    return {
        "source": source,
        "language": "python",
        "entities": entities,
        "imports": imports,
    }