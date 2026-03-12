from pydantic import BaseModel
from typing import Any, Optional
from datetime import datetime

class TelegramChat(BaseModel):
    id: int
    type: str = "private"

class TelegramMessage(BaseModel):
    message_id: int | None = None
    chat: TelegramChat
    text: str | None = None
    caption: str | None = None
    photo: list[dict[str, Any]] | None = None
    document: dict[str, Any] | None = None
    voice: dict[str, Any] | None = None
    audio: dict[str, Any] | None = None

class TelegramUpdate(BaseModel):
    """Telegram webhook update payload."""
    update_id: int | None = None
    message: TelegramMessage | None = None

    model_config = {"extra": "allow"}

class WebhookResponse(BaseModel):
    """Standard webhook response."""
    ok: bool = True

class UserCreateRequest(BaseModel):
    username: str
    email: Optional[str] = None
    invite_code: Optional[str] = None

class APIKeyResponse(BaseModel):
    api_key: str
    user_id: int
    created_at: datetime
    expires_at: Optional[datetime] = None

class UserResponse(BaseModel):
    id: int  # Will be 0 since email is the primary key
    username: str
    email: str  # Required field now
    created_at: datetime

class AuthRequest(BaseModel):
    api_key: str

class APIKeyValidationResponse(BaseModel):
    valid: bool
    user_id: Optional[int] = None
    username: Optional[str] = None
    email: Optional[str] = None

class TransactionResponse(BaseModel):
    id: int
    email: str
    amount: float
    description: Optional[str] = None
    category: Optional[str] = None
    type: str
    payment_method: Optional[str] = None
    date: str  # YYYY-MM-DD
    created_at: datetime

class BudgetResponse(BaseModel):
    id: int
    email: str
    category: Optional[str] = None
    amount: float
    month: int
    year: int
    created_at: datetime

class ApiKeyListItem(BaseModel):
    api_key_masked: str  # e.g. "abc...xyz"
    created_at: datetime
    is_active: bool

class SummaryCategory(BaseModel):
    category: str
    total: float
    budget: Optional[float] = None
    percentage: Optional[float] = None  # spending / budget * 100

class SummaryResponse(BaseModel):
    email: str
    month: int
    year: int
    total_income: float
    total_expense: float
    categories: list[SummaryCategory]

class ChatRequest(BaseModel):
    message: str
    session_id: str
    user_id: str
    stream: bool = False

class ChatResponse(BaseModel):
    response: str
    source: str
    token_usage: Optional[dict] = None
    agent_latency_ms: Optional[float] = None