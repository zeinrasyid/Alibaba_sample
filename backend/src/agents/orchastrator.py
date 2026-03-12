from src.utils.agent_helper import create_agent
from src.tools import indonesian_current_time
from src.tools.chart import generate_chart
from src.tools.sql_db import query_db, get_db_schema, write_transactions, write_budgets

def orchastrator_agent(
    session_id:str,
    user_id:str
):
    agent_name = 'orchastrator'
    return create_agent(
        agent_name=agent_name,
        session_id=session_id,
        user_id=user_id,
        tools=[
            indonesian_current_time,
            generate_chart,
            query_db,
            get_db_schema,
            write_transactions,
            write_budgets
        ],
        preserve_messages=25)
