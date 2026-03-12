from src.core import logger
from sqlalchemy import text
from datetime import datetime, timedelta


def validate_api_key(api_key: str) -> dict | None:
    """Validate API key and return user info if valid."""
    try:
        from sqlalchemy import create_engine
        from src.core.config import settings
        
        # Get database URL from settings
        db_url = settings.get("DATABASE_URL", "sqlite:///./financial_assistant.db")
        engine = create_engine(db_url)
        
        with engine.connect() as conn:
            # Query to validate API key
            result = conn.execute(text("""
                SELECT ui.email, ui.username
                FROM api_keys ak
                JOIN user_info ui ON ak.email = ui.email
                WHERE ak.api_key = :api_key
                AND ak.is_active = true
            """), {"api_key": api_key})
            
            row = result.fetchone()
            if row:
                return {
                    "email": row[0],
                    "username": row[1]
                }
            return None
    except Exception as e:
        logger.error(f"API key validation error: {e}")
        return None


def get_user_from_api_key(api_key: str) -> dict | None:
    """Get user info from API key."""
    return validate_api_key(api_key)


def store_session(chat_id: int, api_key: str):
    """Store authenticated session in local database."""
    try:
        user_info = validate_api_key(api_key)
        if not user_info:
            return False
            
        from sqlalchemy import create_engine
        from src.core.config import settings
        
        # Get database URL from settings
        db_url = settings.get("DATABASE_URL", "sqlite:///./financial_assistant.db")
        engine = create_engine(db_url)
        
        with engine.connect() as conn:
            # Check if Telegram user already exists (using email as identifier)
            result = conn.execute(text("""
                SELECT email FROM telegram_users WHERE telegram_chat_id = :chat_id
            """), {"chat_id": chat_id})
            
            row = result.fetchone()
            if row:
                # Update existing user
                conn.execute(text("""
                    UPDATE telegram_users 
                    SET email = :email, is_authenticated = true, last_interaction = NOW()
                    WHERE telegram_chat_id = :chat_id
                """), {
                    "email": user_info["email"],
                    "chat_id": chat_id
                })
            else:
                # Create new Telegram user
                conn.execute(text("""
                    INSERT INTO telegram_users (email, telegram_chat_id, telegram_user_id, is_authenticated, last_interaction)
                    VALUES (:email, :chat_id, :telegram_user_id, true, NOW())
                """), {
                    "email": user_info["email"],
                    "chat_id": chat_id,
                    "telegram_user_id": chat_id
                })
            
            conn.commit()
            return True
    except Exception as e:
        logger.error(f"Store session error: {e}")
        return False


def get_authenticated_api_key(chat_id: int) -> str | None:
    """Check if user has valid auth session. Returns actual API key if authenticated."""
    try:
        from sqlalchemy import create_engine
        from src.core.config import settings
        
        # Get database URL from settings
        db_url = settings.get("DATABASE_URL", "sqlite:///./financial_assistant.db")
        engine = create_engine(db_url)
        
        with engine.connect() as conn:
            # Get the authenticated Telegram user and their API key
            result = conn.execute(text("""
                SELECT ak.api_key, tu.last_interaction
                FROM telegram_users tu
                JOIN api_keys ak ON tu.email = ak.email
                WHERE tu.telegram_chat_id = :chat_id
                AND tu.is_authenticated = true
                AND ak.is_active = true
            """), {"chat_id": chat_id})
            
            row = result.fetchone()
            if not row or not row[0]:  # No authenticated user or no API key
                return None
                
            # Check if session is still valid (within expiry time)
            if row[1]:  # last_interaction is not null
                expiry_hours = int(settings.get("SESSION_EXPIRY_HOURS", 24))  # Default to 24 hours
                last_interaction = row[1]
                if (datetime.now() - last_interaction.replace(tzinfo=None)) > timedelta(hours=expiry_hours):
                    # Session expired, update the record
                    conn.execute(text("""
                        UPDATE telegram_users 
                        SET is_authenticated = false 
                        WHERE telegram_chat_id = :chat_id
                    """), {"chat_id": chat_id})
                    conn.commit()
                    return None
            
            # Return the actual API key
            return row[0]
    except Exception as e:
        logger.error(f"Get authenticated API key error: {e}")
        return None


def delete_session(chat_id: int):
    """Delete auth session for logout."""
    try:
        from sqlalchemy import create_engine
        from src.core.config import settings
        
        # Get database URL from settings
        db_url = settings.get("DATABASE_URL", "sqlite:///./financial_assistant.db")
        engine = create_engine(db_url)
        
        with engine.connect() as conn:
            # Find the Telegram user and set as unauthenticated
            conn.execute(text("""
                UPDATE telegram_users 
                SET is_authenticated = false, last_interaction = NOW()
                WHERE telegram_chat_id = :chat_id
            """), {"chat_id": chat_id})
            conn.commit()
    except Exception as e:
        logger.error(f"Delete session error: {e}")










