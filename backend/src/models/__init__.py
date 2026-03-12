"""Database models for the financial assistant."""
from typing import Literal
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Date, ForeignKey, text, UniqueConstraint
from datetime import datetime


Base = declarative_base()

Category = Literal[
    "food", "transport", "shopping", "entertainment",
    "health", "bills", "education", "other"
]


class UserInfo(Base):
    __tablename__ = "user_info"

    email = Column(String(255), primary_key=True, unique=True, index=True, nullable=False)
    username = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class ApiKey(Base):
    __tablename__ = "api_keys"

    api_key = Column(String(255), primary_key=True, unique=True, nullable=False)
    email = Column(String(255), ForeignKey("user_info.email"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True, nullable=False)


class TelegramUser(Base):
    __tablename__ = "telegram_users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), ForeignKey("user_info.email"), nullable=False)
    telegram_chat_id = Column(Integer, unique=True)
    telegram_user_id = Column(Integer, unique=True)
    is_authenticated = Column(Boolean, default=False)
    last_interaction = Column(DateTime, default=datetime.utcnow)


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), ForeignKey("user_info.email"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    description = Column(String(500))
    category = Column(String(100), index=True)
    type = Column(String(20), nullable=False, default="expense")
    payment_method = Column(String(50), nullable=True)
    date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Budget(Base):
    __tablename__ = "budgets"
    __table_args__ = (
        UniqueConstraint('email', 'category', 'month', 'year', name='uq_budget_email_category_period'),
    )

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), ForeignKey("user_info.email"), nullable=False, index=True)
    category = Column(String(100), index=True)
    amount = Column(Float, nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
