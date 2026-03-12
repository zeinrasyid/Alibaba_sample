"""
Bug Condition Exploration Tests

These tests encode the EXPECTED (fixed) behavior for the financial assistant backend.
They should FAIL on the current unfixed code, proving the bugs exist.

**Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 1.10, 1.11, 1.12, 1.13**
"""

import ast
import inspect
import textwrap

import pytest


# ---------------------------------------------------------------------------
# Helpers – read source via AST so we never trigger the NameError on import
# ---------------------------------------------------------------------------

def _parse_file(path: str) -> ast.Module:
    with open(path) as f:
        return ast.parse(f.read(), filename=path)


def _read_source(path: str) -> str:
    with open(path) as f:
        return f.read()


# Paths to the buggy files
WRITE_TXN_PATH = "src/tools/sql_db/write_transactions.py"
WRITE_BUD_PATH = "src/tools/sql_db/write_budgets.py"
INIT_PATH = "src/tools/sql_db/__init__.py"
ORCH_PATH = "src/agents/orchastrator.py"
TELEGRAM_PATH = "src/api/v1/endpoints/webhooks/telegram.py"
TELEGRAM_AUTH_PATH = "src/api/v1/endpoints/webhooks/telegram_auth.py"


# ===================================================================
# Bug Cluster 1 – Missing Literal import
# ===================================================================

class TestLiteralImport:
    """write_transactions and write_budgets must import Literal from typing."""

    def test_write_transactions_imports_literal(self):
        """
        Expected: write_transactions.py imports Literal from typing.
        On unfixed code this FAILS because the import is missing.

        **Validates: Requirements 1.1**
        """
        source = _read_source(WRITE_TXN_PATH)
        tree = _parse_file(WRITE_TXN_PATH)

        # Check for 'from typing import ..., Literal, ...'
        has_literal_import = False
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == "typing":
                for alias in node.names:
                    if alias.name == "Literal":
                        has_literal_import = True
        assert has_literal_import, (
            "write_transactions.py must import Literal from typing"
        )

    def test_write_budgets_imports_literal(self):
        """
        Expected: write_budgets.py imports Literal from typing.
        On unfixed code this FAILS because the import is missing.

        **Validates: Requirements 1.3**
        """
        tree = _parse_file(WRITE_BUD_PATH)

        has_literal_import = False
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == "typing":
                for alias in node.names:
                    if alias.name == "Literal":
                        has_literal_import = True
        assert has_literal_import, (
            "write_budgets.py must import Literal from typing"
        )


# ===================================================================
# Bug Cluster 2 – Function name collision in write_budgets.py
# ===================================================================

class TestFunctionName:
    """write_budgets.py must define a function named write_budgets, not write_transactions."""

    def test_write_budgets_defines_write_budgets_function(self):
        """
        Expected: write_budgets.py defines a function called 'write_budgets'.
        On unfixed code this FAILS because the function is named 'write_transactions'.

        **Validates: Requirements 1.6**
        """
        tree = _parse_file(WRITE_BUD_PATH)

        func_names = [
            node.name
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        assert "write_budgets" in func_names, (
            f"write_budgets.py must define a function named 'write_budgets', "
            f"found: {func_names}"
        )


# ===================================================================
# Bug Cluster 3 – Variable name consistency (parameter vs body)
# ===================================================================

class TestVariableName:
    """Both tools must use a consistent ToolContext parameter name in signature and body."""

    def test_write_transactions_uses_context_not_tool_context(self):
        """
        Expected: write_transactions function body uses the same ToolContext
        parameter name as declared in the signature (no NameError at runtime).

        **Validates: Requirements 1.2**
        """
        source = _read_source(WRITE_TXN_PATH)
        tree = _parse_file(WRITE_TXN_PATH)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "write_transactions":
                # Find the ToolContext parameter name from the signature
                param_name = node.args.args[-1].arg  # last param is the context
                func_source = ast.get_source_segment(source, node)
                # Body must reference the same name used in the signature
                assert f"{param_name}.agent.state" in func_source, (
                    f"write_transactions body must use '{param_name}' (the declared parameter)"
                )
                break

    def test_write_budgets_uses_context_not_tool_context(self):
        """
        Expected: write_budgets function body uses the same ToolContext
        parameter name as declared in the signature (no NameError at runtime).

        **Validates: Requirements 1.4**
        """
        source = _read_source(WRITE_BUD_PATH)
        tree = _parse_file(WRITE_BUD_PATH)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "write_budgets":
                param_name = node.args.args[-1].arg
                func_source = ast.get_source_segment(source, node)
                assert f"{param_name}.agent.state" in func_source, (
                    f"write_budgets body must use '{param_name}' (the declared parameter)"
                )
                break


# ===================================================================
# Bug Cluster 4 – Missing exports in __init__.py
# ===================================================================

class TestExports:
    """write_transactions and write_budgets must be exported from sql_db __init__."""

    def test_init_exports_write_transactions(self):
        """
        Expected: sql_db/__init__.py exports write_transactions.
        On unfixed code this FAILS because only get_db_schema and query_db are exported.

        **Validates: Requirements 1.8**
        """
        source = _read_source(INIT_PATH)
        tree = _parse_file(INIT_PATH)

        # Check __all__ list
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "__all__":
                        if isinstance(node.value, ast.List):
                            elements = [
                                elt.value
                                for elt in node.value.elts
                                if isinstance(elt, ast.Constant)
                            ]
                            assert "write_transactions" in elements, (
                                f"__all__ must include 'write_transactions', "
                                f"found: {elements}"
                            )
                            return

        pytest.fail("Could not find __all__ in sql_db/__init__.py")

    def test_init_exports_write_budgets(self):
        """
        Expected: sql_db/__init__.py exports write_budgets.
        On unfixed code this FAILS because only get_db_schema and query_db are exported.

        **Validates: Requirements 1.8**
        """
        source = _read_source(INIT_PATH)
        tree = _parse_file(INIT_PATH)

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "__all__":
                        if isinstance(node.value, ast.List):
                            elements = [
                                elt.value
                                for elt in node.value.elts
                                if isinstance(elt, ast.Constant)
                            ]
                            assert "write_budgets" in elements, (
                                f"__all__ must include 'write_budgets', "
                                f"found: {elements}"
                            )
                            return

        pytest.fail("Could not find __all__ in sql_db/__init__.py")


# ===================================================================
# Bug Cluster 5 – Orchestrator missing write tools / has serper tools
# ===================================================================

class TestOrchestrator:
    """Orchestrator must include write tools and must NOT include serper tools."""

    def _get_tools_list_names(self) -> list[str]:
        """Parse the orchestrator source and extract tool names from the tools= list."""
        source = _read_source(ORCH_PATH)
        tree = _parse_file(ORCH_PATH)

        for node in ast.walk(tree):
            if isinstance(node, ast.keyword) and node.arg == "tools":
                if isinstance(node.value, ast.List):
                    return [
                        elt.id
                        for elt in node.value.elts
                        if isinstance(elt, ast.Name)
                    ]
        return []

    def test_orchestrator_includes_write_transactions(self):
        """
        Expected: orchestrator tools list includes write_transactions.
        On unfixed code this FAILS because write tools are not registered.

        **Validates: Requirements 1.7**
        """
        tools = self._get_tools_list_names()
        assert "write_transactions" in tools, (
            f"Orchestrator must include write_transactions in tools, found: {tools}"
        )

    def test_orchestrator_includes_write_budgets(self):
        """
        Expected: orchestrator tools list includes write_budgets.
        On unfixed code this FAILS because write tools are not registered.

        **Validates: Requirements 1.7**
        """
        tools = self._get_tools_list_names()
        assert "write_budgets" in tools, (
            f"Orchestrator must include write_budgets in tools, found: {tools}"
        )

    def test_orchestrator_does_not_include_serper_tools(self):
        """
        Expected: orchestrator tools list does NOT include serper tools.
        On unfixed code this FAILS because serper tools are still registered.

        **Validates: Requirements 1.10**
        """
        tools = self._get_tools_list_names()
        serper_tools = [t for t in tools if "serper" in t.lower()]
        assert len(serper_tools) == 0, (
            f"Orchestrator must NOT include serper tools, found: {serper_tools}"
        )


# ===================================================================
# Bug Cluster 6 – Telegram dead code (_handle_expenses, _handle_balance)
# ===================================================================

class TestTelegramDeadCode:
    """Telegram webhook must NOT define _handle_expenses or _handle_balance."""

    def test_no_handle_expenses_function(self):
        """
        Expected: telegram.py does NOT define _handle_expenses.
        On unfixed code this FAILS because the dead-code function exists.

        **Validates: Requirements 1.9**
        """
        tree = _parse_file(TELEGRAM_PATH)

        func_names = [
            node.name
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        assert "_handle_expenses" not in func_names, (
            "telegram.py must NOT define _handle_expenses (dead code calling "
            "non-existent auth.get_recent_expenses)"
        )

    def test_no_handle_balance_function(self):
        """
        Expected: telegram.py does NOT define _handle_balance.
        On unfixed code this FAILS because the dead-code function exists.

        **Validates: Requirements 1.9**
        """
        tree = _parse_file(TELEGRAM_PATH)

        func_names = [
            node.name
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        assert "_handle_balance" not in func_names, (
            "telegram.py must NOT define _handle_balance (dead code calling "
            "non-existent auth.get_user_balance)"
        )


# ===================================================================
# Bug Cluster 7 – Empty docstrings
# ===================================================================

class TestDocstrings:
    """Both write tools must have non-empty, meaningful docstrings."""

    def test_write_transactions_has_nonempty_docstring(self):
        """
        Expected: write_transactions has a non-empty docstring.
        On unfixed code this FAILS because the docstring is empty ('').

        **Validates: Requirements 1.11**
        """
        tree = _parse_file(WRITE_TXN_PATH)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "write_transactions":
                docstring = ast.get_docstring(node)
                assert docstring and docstring.strip(), (
                    "write_transactions must have a non-empty docstring"
                )
                return

        pytest.fail("Could not find write_transactions function")

    def test_write_budgets_has_nonempty_docstring(self):
        """
        Expected: write_budgets has a non-empty docstring.
        On unfixed code this FAILS because the docstring is empty ('').

        **Validates: Requirements 1.12**
        """
        tree = _parse_file(WRITE_BUD_PATH)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # The function might be named write_transactions (bug cluster 2)
                # or write_budgets (after fix). Check the first function with a
                # @tool decorator.
                docstring = ast.get_docstring(node)
                # We expect a meaningful docstring (not empty/whitespace-only)
                assert docstring and docstring.strip(), (
                    f"The tool function in write_budgets.py ('{node.name}') "
                    f"must have a non-empty docstring"
                )
                return

        pytest.fail("Could not find any function in write_budgets.py")
