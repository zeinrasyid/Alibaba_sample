from typing import Literal, Optional
from sqlalchemy import text
from strands import tool, ToolContext
from src.core import logger
from src.tools.sql_db.client import get_engine, Category


@tool(context=True)
def write_transactions(
    amount: float,
    description: str,
    category: Category,
    date: str,
    type: Literal["income", "expense"] = "expense",
    payment_method: Optional[Literal['transfer', 'e-wallet', 'cash']] = None,
    tool_context=ToolContext
) -> str:
    """
    Record a financial transaction (income or expense) to the database.

    Use this tool when the user wants to log a new transaction such as a purchase,
    bill payment, salary, or any financial activity.

    Args:
        amount: The transaction amount as a positive number.
        description: A short description of the transaction (e.g. "Makan siang di warteg").
        category: The spending category. One of: food, transport, shopping,
                  entertainment, health, bills, education, other.
        date: The date of the transaction in YYYY-MM-DD format.
        type: Either "income" or "expense". Defaults to "expense".
        payment_method: Optional payment method (e.g. "e-wallet", "cash", "transfer").

    Returns:
        "True" if the transaction was recorded successfully, "False" otherwise.
    """
    email = tool_context.agent.state.get('user_id')
    if not email:
        raise ValueError("user_id has not been set in agent state")

    engine = get_engine()
    try:
        with engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO transactions (email, amount, description, category, type, payment_method, date, created_at)
                VALUES (:email, :amount, :description, :category, :type, :payment_method, :date, NOW())
            """), {
                "email": email,
                "amount": amount,
                "description": description,
                "category": category,
                "type": type,
                "payment_method": payment_method,
                "date": date
            })
            conn.commit()
            return True
    except Exception as e:
        logger.error(f"Add transaction error: {e}")
        return False
