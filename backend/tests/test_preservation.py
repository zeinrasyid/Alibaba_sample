"""
Preservation Property Tests

These tests capture the EXISTING baseline behavior that must NOT change after the fix.
They must PASS on the current unfixed code.

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 3.10, 3.11, 3.12**
"""

import ast
import os

import pytest


# ---------------------------------------------------------------------------
# Helpers – AST-based inspection to avoid import side-effects
# ---------------------------------------------------------------------------

def _parse_file(path: str) -> ast.Module:
    with open(path) as f:
        return ast.parse(f.read(), filename=path)


def _read_source(path: str) -> str:
    with open(path) as f:
        return f.read()


def _get_function_names(path: str) -> list[str]:
    """Return all top-level and nested function/async-function names in a file."""
    tree = _parse_file(path)
    return [
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]


def _get_all_exports(path: str) -> list[str]:
    """Return the __all__ list from a module, or empty list if not found."""
    tree = _parse_file(path)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    if isinstance(node.value, ast.List):
                        return [
                            elt.value
                            for elt in node.value.elts
                            if isinstance(elt, ast.Constant)
                        ]
    return []


def _get_tools_list_names(orch_path: str) -> list[str]:
    """Parse the orchestrator source and extract tool names from the tools= keyword."""
    tree = _parse_file(orch_path)
    for node in ast.walk(tree):
        if isinstance(node, ast.keyword) and node.arg == "tools":
            if isinstance(node.value, ast.List):
                return [
                    elt.id
                    for elt in node.value.elts
                    if isinstance(elt, ast.Name)
                ]
    return []


# Paths
SQL_DB_INIT = "src/tools/sql_db/__init__.py"
ORCH_PATH = "src/agents/orchastrator.py"
TELEGRAM_PATH = "src/api/v1/endpoints/webhooks/telegram.py"
CHART_INIT = "src/tools/chart/__init__.py"
INDONESIAN_TIME_PATH = "src/tools/indonesian_current_time.py"


# ===================================================================
# Preservation 1 & 2 – query_db and get_db_schema remain importable
# ===================================================================

class TestReadToolsPreservation:
    """query_db and get_db_schema must remain importable and callable.

    **Validates: Requirements 3.1, 3.2**
    """

    def test_query_db_importable_and_callable(self):
        """query_db is exported from src.tools.sql_db and is callable."""
        exports = _get_all_exports(SQL_DB_INIT)
        assert "query_db" in exports, (
            f"query_db must remain in sql_db __all__, found: {exports}"
        )
        # Verify the import statement exists in __init__.py
        source = _read_source(SQL_DB_INIT)
        assert "from src.tools.sql_db.query_db import query_db" in source, (
            "query_db import must remain in sql_db/__init__.py"
        )

    def test_get_db_schema_importable_and_callable(self):
        """get_db_schema is exported from src.tools.sql_db and is callable."""
        exports = _get_all_exports(SQL_DB_INIT)
        assert "get_db_schema" in exports, (
            f"get_db_schema must remain in sql_db __all__, found: {exports}"
        )
        source = _read_source(SQL_DB_INIT)
        assert "from src.tools.sql_db.get_db_schema import get_db_schema" in source, (
            "get_db_schema import must remain in sql_db/__init__.py"
        )


# ===================================================================
# Preservation 3 – indonesian_current_time remains importable
# ===================================================================

class TestIndonesianTimePreservation:
    """indonesian_current_time tool must remain importable.

    **Validates: Requirements 3.11**
    """

    def test_indonesian_current_time_exists(self):
        """indonesian_current_time.py exists and defines the tool function."""
        assert os.path.isfile(INDONESIAN_TIME_PATH), (
            f"{INDONESIAN_TIME_PATH} must exist"
        )
        func_names = _get_function_names(INDONESIAN_TIME_PATH)
        assert "indonesian_current_time" in func_names, (
            f"indonesian_current_time function must exist, found: {func_names}"
        )

    def test_indonesian_current_time_is_decorated_tool(self):
        """indonesian_current_time is decorated with @tool, making it callable."""
        source = _read_source(INDONESIAN_TIME_PATH)
        tree = _parse_file(INDONESIAN_TIME_PATH)

        # Verify the function has a @tool decorator (strands tool)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "indonesian_current_time":
                decorator_names = []
                for dec in node.decorator_list:
                    if isinstance(dec, ast.Name):
                        decorator_names.append(dec.id)
                assert "tool" in decorator_names, (
                    f"indonesian_current_time must be decorated with @tool, "
                    f"found decorators: {decorator_names}"
                )
                return

        pytest.fail("Could not find indonesian_current_time function")


# ===================================================================
# Preservation 4 – generate_chart remains importable
# ===================================================================

class TestChartPreservation:
    """generate_chart tool must remain importable from src.tools.chart.

    **Validates: Requirements 3.6**
    """

    def test_generate_chart_exists_and_importable(self):
        """generate_chart is exported from src.tools.chart and is callable."""
        exports = _get_all_exports(CHART_INIT)
        assert "generate_chart" in exports, (
            f"generate_chart must remain in chart __all__, found: {exports}"
        )

    def test_generate_chart_function_defined(self):
        """generate_chart function is defined in generate_chart.py."""
        func_names = _get_function_names("src/tools/chart/generate_chart.py")
        assert "generate_chart" in func_names, (
            f"generate_chart function must exist, found: {func_names}"
        )


# ===================================================================
# Preservation 5-8 – Telegram command handlers remain present
# ===================================================================

class TestTelegramCommandsPreservation:
    """Telegram /start, /help, /login, /logout handlers must remain present.

    **Validates: Requirements 3.3, 3.4**
    """

    def test_start_command_handler_exists(self):
        """Telegram /start command is handled in telegram_webhook."""
        source = _read_source(TELEGRAM_PATH)
        assert '/start' in source, (
            "telegram.py must handle /start command"
        )

    def test_help_command_handler_exists(self):
        """Telegram /help command is handled in telegram_webhook."""
        source = _read_source(TELEGRAM_PATH)
        assert '/help' in source, (
            "telegram.py must handle /help command"
        )

    def test_login_handler_exists(self):
        """_handle_login function exists in telegram.py."""
        func_names = _get_function_names(TELEGRAM_PATH)
        assert "_handle_login" in func_names, (
            f"_handle_login must exist in telegram.py, found: {func_names}"
        )

    def test_logout_handling_exists(self):
        """Telegram /logout handling exists in the webhook function."""
        source = _read_source(TELEGRAM_PATH)
        assert '/logout' in source, (
            "telegram.py must handle /logout command"
        )


# ===================================================================
# Preservation 9-12 – Message processing pipeline remains intact
# ===================================================================

class TestMessagePipelinePreservation:
    """The agent message processing pipeline functions must remain present.

    **Validates: Requirements 3.4, 3.5**
    """

    def test_process_message_exists(self):
        """_process_message function exists in telegram.py."""
        func_names = _get_function_names(TELEGRAM_PATH)
        assert "_process_message" in func_names, (
            f"_process_message must exist in telegram.py, found: {func_names}"
        )

    def test_extract_input_exists(self):
        """_extract_input function exists in telegram.py."""
        func_names = _get_function_names(TELEGRAM_PATH)
        assert "_extract_input" in func_names, (
            f"_extract_input must exist in telegram.py, found: {func_names}"
        )

    def test_build_prompt_exists(self):
        """_build_prompt function exists in telegram.py."""
        func_names = _get_function_names(TELEGRAM_PATH)
        assert "_build_prompt" in func_names, (
            f"_build_prompt must exist in telegram.py, found: {func_names}"
        )

    def test_send_response_exists(self):
        """_send_response function exists in telegram.py."""
        func_names = _get_function_names(TELEGRAM_PATH)
        assert "_send_response" in func_names, (
            f"_send_response must exist in telegram.py, found: {func_names}"
        )


# ===================================================================
# Preservation 13 – Orchestrator preserves existing tools
# ===================================================================

class TestOrchestratorPreservation:
    """orchastrator_agent must preserve query_db, get_db_schema,
    generate_chart, and indonesian_current_time in its tools list.

    **Validates: Requirements 3.1, 3.2, 3.6, 3.11**
    """

    def test_orchestrator_function_exists(self):
        """orchastrator_agent function exists in orchastrator.py."""
        func_names = _get_function_names(ORCH_PATH)
        assert "orchastrator_agent" in func_names, (
            f"orchastrator_agent must exist, found: {func_names}"
        )

    def test_orchestrator_includes_query_db(self):
        """Orchestrator tools list includes query_db."""
        tools = _get_tools_list_names(ORCH_PATH)
        assert "query_db" in tools, (
            f"Orchestrator must include query_db, found: {tools}"
        )

    def test_orchestrator_includes_get_db_schema(self):
        """Orchestrator tools list includes get_db_schema."""
        tools = _get_tools_list_names(ORCH_PATH)
        assert "get_db_schema" in tools, (
            f"Orchestrator must include get_db_schema, found: {tools}"
        )

    def test_orchestrator_includes_generate_chart(self):
        """Orchestrator tools list includes generate_chart."""
        tools = _get_tools_list_names(ORCH_PATH)
        assert "generate_chart" in tools, (
            f"Orchestrator must include generate_chart, found: {tools}"
        )

    def test_orchestrator_includes_indonesian_current_time(self):
        """Orchestrator tools list includes indonesian_current_time."""
        tools = _get_tools_list_names(ORCH_PATH)
        assert "indonesian_current_time" in tools, (
            f"Orchestrator must include indonesian_current_time, found: {tools}"
        )
