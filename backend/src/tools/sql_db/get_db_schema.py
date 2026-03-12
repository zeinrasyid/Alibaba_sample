import json
from sqlalchemy import inspect
from strands import tool
from src.core import logger
from src.tools.sql_db.client import get_engine
from typing import Literal, List


@tool()
def get_db_schema(
    table_names: List[Literal['transactions', 'budgets']] = ['transactions', 'budgets']
) -> str:
    """
    Get PostgreSQL database schema metadata including table descriptions, column names, types, and comments.

    Use this tool FIRST before writing any data query to understand the database structure.

    Args:
        table_names: List of specific table names to inspect. Allowed: 'transactions', 'budgets'.
    """
    logger.info("invoke tool")

    engine = get_engine()
    inspector = inspect(engine)

    try:
        all_tables = inspector.get_table_names(schema="public")
        targets = [t for t in all_tables if t in table_names] if table_names else all_tables

        tables = {}
        for table_name in targets:
            try:
                table_comment = inspector.get_table_comment(table_name, schema="public")
                description = table_comment.get("text", "") or ""
            except NotImplementedError:
                description = ""

            columns = []
            for col in inspector.get_columns(table_name, schema="public"):
                columns.append({
                    "name": col["name"],
                    "type": str(col["type"]),
                    "nullable": col.get("nullable", True),
                    "description": col.get("comment", "") or "",
                })

            tables[table_name] = {
                "description": description,
                "columns": columns,
                "column_count": len(columns),
            }

        result = {
            "dialect": "postgresql",
            "schema": "public",
            "tables": tables,
            "table_count": len(tables),
        }
        logger.debug(f"schema returned {len(tables)} tables")
        return json.dumps(result, default=str)
    except Exception as e:
        logger.error(f"schema discovery failed: {e}")
        raise
