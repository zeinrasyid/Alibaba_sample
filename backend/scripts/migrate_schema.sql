-- Migration script: Update transactions and budgets tables
-- Run against: financial_assistant database on alibaba-postgres container

BEGIN;

-- ============================================================
-- 1. Create tables if they don't exist yet (fresh setup)
-- ============================================================

CREATE TABLE IF NOT EXISTS user_info (
    email VARCHAR(255) PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS api_keys (
    api_key VARCHAR(255) PRIMARY KEY,
    email VARCHAR(255) NOT NULL REFERENCES user_info(email),
    created_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS telegram_users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL REFERENCES user_info(email),
    telegram_chat_id INTEGER UNIQUE,
    telegram_user_id INTEGER UNIQUE,
    is_authenticated BOOLEAN DEFAULT FALSE,
    last_interaction TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- 2. Drop old transactions table and recreate with new schema
-- ============================================================

DROP TABLE IF EXISTS transactions CASCADE;

CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL REFERENCES user_info(email),
    amount FLOAT NOT NULL,
    description VARCHAR(500),
    category VARCHAR(100),
    type VARCHAR(20) NOT NULL DEFAULT 'expense',
    payment_method VARCHAR(50),
    date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_transactions_email ON transactions(email);
CREATE INDEX idx_transactions_category ON transactions(category);

-- ============================================================
-- 3. Drop old budgets table and recreate with new schema
-- ============================================================

DROP TABLE IF EXISTS budgets CASCADE;

CREATE TABLE budgets (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL REFERENCES user_info(email),
    category VARCHAR(100),
    amount FLOAT NOT NULL,
    month INTEGER NOT NULL,
    year INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT uq_budget_email_category_period UNIQUE (email, category, month, year)
);

CREATE INDEX idx_budgets_email ON budgets(email);
CREATE INDEX idx_budgets_category ON budgets(category);

COMMIT;
