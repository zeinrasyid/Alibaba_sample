from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import secrets
import string
from datetime import datetime
from sqlalchemy import create_engine, text
from src.core.config import settings
from src.core import logger

from src.api.v1.schema import (
    UserCreateRequest, 
    APIKeyResponse, 
    UserResponse, 
    AuthRequest, 
    APIKeyValidationResponse,
    TransactionResponse,
    BudgetResponse,
    ApiKeyListItem,
    SummaryResponse,
    SummaryCategory,
)

api_router = APIRouter(prefix="/api/v1")

# Import telegram router
from src.api.v1.endpoints.webhooks import telegram_router
api_router.include_router(telegram_router, prefix="/webhook", tags=["webhooks"])


@api_router.post("/users/", response_model=UserResponse, tags=["users"])
def create_user(user_data: UserCreateRequest):
    """Create a new user account"""
    # Validate invite code
    valid_invite_code = settings.get("INVITE_CODE", "GRACE2026")
    if not user_data.invite_code or user_data.invite_code != valid_invite_code:
        raise HTTPException(status_code=403, detail="Invite code tidak valid")
    
    db_url = settings.get("DATABASE_URL", "sqlite:///./financial_assistant.db")
    engine = create_engine(db_url)
    
    try:
        with engine.connect() as conn:
            # Check if user already exists (email is the unique identifier)
            result = conn.execute(text("""
                SELECT email, username, created_at 
                FROM user_info 
                WHERE email = :email
            """), {"email": user_data.email})
            
            existing_user = result.fetchone()
            if existing_user:
                raise HTTPException(status_code=400, detail="Email already registered")
            
            # Create new user
            result = conn.execute(text("""
                INSERT INTO user_info (email, username, created_at) 
                VALUES (:email, :username, NOW())
                RETURNING email, username, created_at
            """), {
                "email": user_data.email,
                "username": user_data.username
            })
            
            conn.commit()
            user = result.fetchone()
            
            return UserResponse(
                id=0,  # Using 0 since email is the primary key now
                username=user[1],
                email=user[0],
                created_at=user[2]
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@api_router.post("/generate-api-key/", response_model=APIKeyResponse, tags=["users"])
def generate_api_key(user_data: UserCreateRequest):
    """Generate a new API key for an existing user"""
    db_url = settings.get("DATABASE_URL", "sqlite:///./financial_assistant.db")
    engine = create_engine(db_url)
    
    try:
        with engine.connect() as conn:
            # Check if user exists by email
            result = conn.execute(text("""
                SELECT email FROM user_info WHERE email = :email
            """), {"email": user_data.email})
            
            user = result.fetchone()
            if not user:
                # Return error if user doesn't exist
                raise HTTPException(status_code=404, detail="User not found. Please create user first.")
            
            email = user[0]
            
            # Generate a secure API key
            alphabet = string.ascii_letters + string.digits
            api_key = ''.join(secrets.choice(alphabet) for _ in range(32))
            
            # Create API key record
            result = conn.execute(text("""
                INSERT INTO api_keys (api_key, email, created_at, is_active) 
                VALUES (:api_key, :email, NOW(), true)
                RETURNING api_key, created_at
            """), {
                "api_key": api_key,
                "email": email
            })
            
            conn.commit()
            api_key_record = result.fetchone()
            
            return APIKeyResponse(
                api_key=api_key_record[0],
                user_id=0,  # Using 0 since email is the primary identifier now
                created_at=api_key_record[1],
                expires_at=None
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating API key: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")




@api_router.post("/validate-api-key/", response_model=APIKeyValidationResponse, tags=["users"])
def validate_api_key(auth_request: AuthRequest):
    """Validate an API key and return user info if valid"""
    db_url = settings.get("DATABASE_URL", "sqlite:///./financial_assistant.db")
    engine = create_engine(db_url)
    
    try:
        with engine.connect() as conn:
            # Find active API key
            result = conn.execute(text("""
                SELECT ui.email, ui.username
                FROM api_keys ak
                JOIN user_info ui ON ak.email = ui.email
                WHERE ak.api_key = :api_key
                AND ak.is_active = true
            """), {"api_key": auth_request.api_key})
            
            row = result.fetchone()
            if row:
                return APIKeyValidationResponse(
                    valid=True,
                    user_id=0,  # Using 0 since email is the primary identifier now
                    username=row[1],
                    email=row[0]  # Adding email to the response
                )
            else:
                return APIKeyValidationResponse(valid=False)
    except Exception as e:
        logger.error(f"Error validating API key: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


def _get_engine():
    db_url = settings.get("DATABASE_URL", "sqlite:///./financial_assistant.db")
    return create_engine(db_url)


@api_router.get("/users/{email}", response_model=UserResponse, tags=["users"])
def get_user(email: str):
    """Get user by email"""
    engine = _get_engine()
    try:
        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT email, username, created_at FROM user_info WHERE email = :email"
            ), {"email": email})
            row = result.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="User not found")
            return UserResponse(id=0, email=row[0], username=row[1], created_at=row[2])
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@api_router.get("/transactions/", response_model=list[TransactionResponse], tags=["transactions"])
def list_transactions(
    email: str,
    month: Optional[int] = None,
    year: Optional[int] = None,
    page: int = 1,
    per_page: int = 20,
):
    """List transactions for a user with optional month/year filter and pagination."""
    if per_page > 100:
        per_page = 100
    offset = (max(page, 1) - 1) * per_page

    engine = _get_engine()
    try:
        with engine.connect() as conn:
            conditions = ["email = :email"]
            params: dict = {"email": email, "limit": per_page, "offset": offset}

            if month is not None:
                conditions.append("EXTRACT(MONTH FROM date) = :month")
                params["month"] = month
            if year is not None:
                conditions.append("EXTRACT(YEAR FROM date) = :year")
                params["year"] = year

            where = " AND ".join(conditions)
            result = conn.execute(text(f"""
                SELECT id, email, amount, description, category, type, payment_method, date, created_at
                FROM transactions
                WHERE {where}
                ORDER BY date DESC, created_at DESC
                LIMIT :limit OFFSET :offset
            """), params)

            return [
                TransactionResponse(
                    id=r[0], email=r[1], amount=r[2], description=r[3],
                    category=r[4], type=r[5], payment_method=r[6],
                    date=str(r[7]), created_at=r[8],
                )
                for r in result.fetchall()
            ]
    except Exception as e:
        logger.error(f"Error listing transactions: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@api_router.get("/budgets/", response_model=list[BudgetResponse], tags=["budgets"])
def list_budgets(
    email: str,
    month: Optional[int] = None,
    year: Optional[int] = None,
):
    """List budgets for a user with optional month/year filter."""
    engine = _get_engine()
    try:
        with engine.connect() as conn:
            conditions = ["email = :email"]
            params: dict = {"email": email}

            if month is not None:
                conditions.append("month = :month")
                params["month"] = month
            if year is not None:
                conditions.append("year = :year")
                params["year"] = year

            where = " AND ".join(conditions)
            result = conn.execute(text(f"""
                SELECT id, email, category, amount, month, year, created_at
                FROM budgets
                WHERE {where}
                ORDER BY year DESC, month DESC, category
            """), params)

            return [
                BudgetResponse(
                    id=r[0], email=r[1], category=r[2], amount=r[3],
                    month=r[4], year=r[5], created_at=r[6],
                )
                for r in result.fetchall()
            ]
    except Exception as e:
        logger.error(f"Error listing budgets: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@api_router.get("/api-keys/", response_model=list[ApiKeyListItem], tags=["users"])
def list_api_keys(email: str):
    """List API keys for a user (keys are partially masked)."""
    engine = _get_engine()
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT api_key, created_at, is_active
                FROM api_keys
                WHERE email = :email
                ORDER BY created_at DESC
            """), {"email": email})

            items = []
            for r in result.fetchall():
                key = r[0]
                masked = f"{key[:4]}...{key[-4:]}" if len(key) > 8 else "****"
                items.append(ApiKeyListItem(
                    api_key_masked=masked, created_at=r[1], is_active=r[2],
                ))
            return items
    except Exception as e:
        logger.error(f"Error listing API keys: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@api_router.delete("/api-keys/{api_key}", tags=["users"])
def revoke_api_key(api_key: str):
    """Deactivate (revoke) an API key."""
    engine = _get_engine()
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                UPDATE api_keys SET is_active = false
                WHERE api_key = :api_key AND is_active = true
            """), {"api_key": api_key})
            conn.commit()
            if result.rowcount == 0:
                raise HTTPException(status_code=404, detail="API key not found or already revoked")
            return {"ok": True, "detail": "API key revoked"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error revoking API key: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@api_router.get("/summary/", response_model=SummaryResponse, tags=["summary"])
def get_summary(email: str, month: int, year: int):
    """Get financial summary for a user in a given month/year."""
    engine = _get_engine()
    try:
        with engine.connect() as conn:
            # Income & expense totals
            totals = conn.execute(text("""
                SELECT type, COALESCE(SUM(amount), 0)
                FROM transactions
                WHERE email = :email
                  AND EXTRACT(MONTH FROM date) = :month
                  AND EXTRACT(YEAR FROM date) = :year
                GROUP BY type
            """), {"email": email, "month": month, "year": year})

            total_income = 0.0
            total_expense = 0.0
            for r in totals.fetchall():
                if r[0] == "income":
                    total_income = float(r[1])
                else:
                    total_expense = float(r[1])

            # Per-category spending
            cats = conn.execute(text("""
                SELECT category, COALESCE(SUM(amount), 0)
                FROM transactions
                WHERE email = :email
                  AND type = 'expense'
                  AND EXTRACT(MONTH FROM date) = :month
                  AND EXTRACT(YEAR FROM date) = :year
                GROUP BY category
                ORDER BY SUM(amount) DESC
            """), {"email": email, "month": month, "year": year})

            # Budgets for this month
            budgets_result = conn.execute(text("""
                SELECT category, amount
                FROM budgets
                WHERE email = :email AND month = :month AND year = :year
            """), {"email": email, "month": month, "year": year})
            budget_map = {r[0]: float(r[1]) for r in budgets_result.fetchall()}

            categories = []
            for r in cats.fetchall():
                cat, spent = r[0], float(r[1])
                budget_amt = budget_map.get(cat)
                pct = round(spent / budget_amt * 100, 1) if budget_amt else None
                categories.append(SummaryCategory(
                    category=cat, total=spent, budget=budget_amt, percentage=pct,
                ))

            return SummaryResponse(
                email=email, month=month, year=year,
                total_income=total_income, total_expense=total_expense,
                categories=categories,
            )
    except Exception as e:
        logger.error(f"Error getting summary: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


