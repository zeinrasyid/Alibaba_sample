from typing import Literal
from sqlalchemy import text
from strands import tool, ToolContext
from src.core import logger
from src.tools.sql_db.client import get_engine, Category


@tool(context=True)
def write_budgets(
    category: Category,
    amount: float,
    month: int,
    year: int,
    tool_context=ToolContext
) -> str:
    """
    Set a monthly budget for a specific spending category.

    Use this tool when the user wants to create or adjust a budget limit for a
    category in a given month and year.

    Args:
        category: The budget category. One of: food, transport, shopping,
                  entertainment, health, bills, education, other.
        amount: The budget amount to allocate for the category.
        month: The month number (1-12).
        year: The year (e.g. 2025).

    Returns:
        "True" if the budget was saved successfully, "False" otherwise.
    """
    email = tool_context.agent.state.get('user_id')
    if not email:
        raise ValueError("user_id has not been set in agent state")

    engine = get_engine()
    try:
        with engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO budgets (email, category, amount, month, year, created_at)
                VALUES (:email, :category, :amount, :month, :year, NOW())
            """), {
                "email": email,
                "category": category,
                "amount": amount,
                "month": month,
                "year": year
            })
            conn.commit()
            return True
    except Exception as e:
        logger.error(f"Add budget error: {e}")
        return False