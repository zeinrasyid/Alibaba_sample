from src.utils.agent_helper import create_agent

def test_agent(
    session_id: str,
    user_id: str,
    tools: list
):
    agent_name = 'test'
    return create_agent(
        agent_name=agent_name,
        session_id=session_id,
        user_id=user_id,
        tools=tools)