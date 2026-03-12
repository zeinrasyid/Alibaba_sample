from pydantic import BaseModel, Field
from typing import Optional, Set
from src.core import logger


logger.info('invoke structured output')
# add latency
class FinalOutput(BaseModel):
    text: str = Field(description="Full text of agent answer only. remove their thinking output.")
    reference: Optional[Set[str]] = Field(default_factory=set, description="List of reference from KB")