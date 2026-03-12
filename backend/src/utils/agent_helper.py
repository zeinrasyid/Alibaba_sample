from strands import Agent, ModelRetryStrategy
from strands.session.s3_session_manager import S3SessionManager
from strands.session.file_session_manager import FileSessionManager
from strands.agent.conversation_manager import SummarizingConversationManager
import os, re
from typing import Any, List
from src.llm.model_resolver import resolve
from src.core import settings


def load_instruction(file_name: str) -> str:
    """
    Load instruction file from the prompts directory.
    
    Args:
        file_name: Name of the instruction file
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompts_dir = os.path.join(current_dir, "..", "instructions")
    file_path = os.path.join(prompts_dir, file_name)
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Instruction file '{file_name}' not found in {prompts_dir}"
        )

def conversation_manager(summary_ratio: float = 0.3, preserve_messages: int = 10) -> SummarizingConversationManager:
    """Create conversation manager"""
    return SummarizingConversationManager(
        summary_ratio=summary_ratio,
        preserve_recent_messages=preserve_messages
    )

def session_manager(session_id: str, user_id:str) -> S3SessionManager | FileSessionManager:
    """
    Create session manager for agent
    - dev: Uses FileSessionManager (local storage)
    - production: Uses S3SessionManager (cloud storage)

    Args:
        session_id: unique session identifier
        user_id: user identifier for prefix
    """
    env = settings.current_env
    storage_path = settings.get('AGENT_SESSION')
    
    if not storage_path:
        raise ValueError("AGENT_SESSION variable must be set.")
    
    if env == "dev":
        storage_path = os.path.join(storage_path, user_id)
        if not os.path.exists(storage_path):
            os.makedirs(storage_path, exist_ok=True)
        return FileSessionManager(
            session_id=session_id,
            storage_dir=storage_path
        )
    return S3SessionManager(
        session_id=session_id,
        bucket=storage_path,
        prefix=user_id
    )

def create_agent(
    agent_name: str,
    session_id: str,
    user_id: str,
    tools: List[Any],
    model_name: str = settings.get("DEFAULT_MODEL"),
    summary_ratio: float = 0.3,
    preserve_messages: int = 10,
) -> Agent:
    model = resolve(model_name)
    return Agent(
        agent_id=agent_name,
        model=model,
        tools=tools,
        system_prompt=(load_instruction(f'{agent_name}.txt')),
        session_manager=session_manager(session_id=session_id, user_id=user_id),
        conversation_manager=conversation_manager(
            summary_ratio=summary_ratio,
            preserve_messages=preserve_messages,
        ),
        retry_strategy=ModelRetryStrategy(
            max_attempts=3,
            initial_delay=2,
            max_delay=10
        )
    )

# def strip_internal_reasoning(text: str) -> str:
#     """
#     Remove internal reasoning or chain-of-thought
#     from LLM output before returning it to the user.
#     """
#     _REASONING_PATTERN = re.compile(
#         r"<thinking>.*?</thinking>|<analysis>.*?</analysis>|<reasoning>.*?</reasoning>",
#         re.DOTALL | re.IGNORECASE,
#     )
#     return _REASONING_PATTERN.sub("", text).strip()