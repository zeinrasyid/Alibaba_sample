import json
import re
from decimal import Decimal
from sqlalchemy import text
from strands import tool, ToolContext
from src.core import logger
from src.tools.sql_db.client import get_engine
from src.utils.rds_helper import is_read_only

# Tables that contain user data and must be scoped by email
_SCOPED_TABLES = ["transactions", "budgets"]


def _serialize(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    return str(obj)


def _wrap_with_email_scope(query: str, email: str) -> str:
    """
    Wrap the query with CTEs that shadow scoped tables, filtering by email.

    For each table in _SCOPED_TABLES that appears in the query, we prepend:
        <table> AS (SELECT * FROM public.<table> WHERE email = :email)

    This ensures the LLM's query can only see rows belonging to the user,
    regardless of what WHERE clause it writes.
    """
    ctes = []
    for table in _SCOPED_TABLES:
        # Check if the table name appears in the query (word boundary match)
        if re.search(rf"\b{table}\b", query, re.IGNORECASE):
            ctes.append(
                f"{table} AS (SELECT * FROM public.{table} WHERE email = :email)"
            )

    if not ctes:
        return query

    cte_block = "WITH " + ",\n     ".join(ctes)
    return f"{cte_block}\n{query}"


@tool(context=True)
def query_db(
    query: str,
    max_rows: int = 100,
    tool_context=ToolContext
) -> str:
    """
    Execute a read-only SQL query against the PostgreSQL database and return results as JSON.
    Queries on 'transactions' and 'budgets' tables are automatically scoped to the current user's email.

    IMPORTANT:
      - Only SELECT, SHOW, DESCRIBE, and EXPLAIN queries are allowed.
      - Always use LIMIT to avoid returning too many rows.
      - Use get_db_schema tool first to discover tables and columns.
      - No need to filter by email — it is enforced automatically.

    Args:
        query: SQL query to execute. Must be read-only (SELECT, SHOW, DESCRIBE, EXPLAIN).
        max_rows: Maximum number of rows to return. Defaults to 100. Max 1000.
    """
    logger.info("invoke tool")

    if not is_read_only(query):
        raise ValueError("Only read-only queries (SELECT, SHOW, DESCRIBE, EXPLAIN) are allowed.")

    email = tool_context.agent.state.get('user_id')
    if not email:
        raise ValueError("user_id has not been set in agent state")

    max_rows = min(max_rows, 1000)
    engine = get_engine()

    # Wrap query with email-scoped CTEs for data isolation
    scoped_query = _wrap_with_email_scope(query, email)
    logger.debug(f"scoped query: {scoped_query}")

    try:
        with engine.connect() as conn:
            conn.execute(text("SET search_path TO public"))
            result = conn.execute(text(scoped_query), {"email": email})
            rows = [dict(row._mapping) for row in result.fetchmany(max_rows)]
            logger.debug(f"query returned {len(rows)} rows")
            return json.dumps(rows, default=_serialize)
    except Exception as e:
        logger.error(f"query failed: {e}")
        raise
