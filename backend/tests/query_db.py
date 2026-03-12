#!/usr/bin/env python3
"""
Database query script for Financial Assistant
Allows direct querying of PostgreSQL database to check data
"""

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("Ali_DATABASE_URL", "postgresql://alibaba:alibaba@localhost:5432/financial_assistant")

def connect_to_db():
    """Create database engine connection"""
    engine = create_engine(DATABASE_URL)
    return engine

def show_tables():
    """Show all tables in the database"""
    engine = connect_to_db()
    with engine.connect() as conn:
        # For PostgreSQL
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """))
        
        print("Tables in database:")
        for row in result:
            print(f"  - {row[0]}")
        print()

def show_user_info():
    """Show all users in user_info table"""
    engine = connect_to_db()
    with engine.connect() as conn:
        try:
            result = conn.execute(text("SELECT * FROM user_info ORDER BY created_at DESC;"))
            
            print("Users in user_info table:")
            for row in result:
                print(f"  Email: {row[0]}")
                print(f"  Username: {row[1]}")
                print(f"  Created At: {row[2]}")
                print("  ---")
        except Exception as e:
            print(f"Error accessing user_info table: {e}")
            print("This table may not exist yet. Did you run the application to create tables?")
        print()

def show_api_keys():
    """Show all API keys in api_keys table"""
    engine = connect_to_db()
    with engine.connect() as conn:
        try:
            result = conn.execute(text("""
                SELECT ak.api_key, ak.email, ak.is_active, ak.created_at
                FROM api_keys ak
                ORDER BY ak.created_at DESC;
            """))
            
            print("API Keys in api_keys table:")
            for row in result:
                print(f"  API Key: {row[0][:8]}...{row[0][-4:]}")  # Show first 8 and last 4 chars
                print(f"  Email: {row[1]}")
                print(f"  Active: {row[2]}")
                print(f"  Created At: {row[3]}")
                print("  ---")
        except Exception as e:
            print(f"Error accessing api_keys table: {e}")
            print("This table may not exist yet. Did you run the application to create tables?")
        print()

def show_telegram_users():
    """Show all telegram users in telegram_users table"""
    engine = connect_to_db()
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT tu.telegram_chat_id, tu.email, tu.is_authenticated, tu.last_interaction
            FROM telegram_users tu
            ORDER BY tu.last_interaction DESC;
        """))
        
        print("Telegram Users in telegram_users table:")
        for row in result:
            print(f"  Chat ID: {row[0]}")
            print(f"  Email: {row[1]}")
            print(f"  Authenticated: {row[2]}")
            print(f"  Last Interaction: {row[3]}")
            print("  ---")
        print()

def search_by_email(email):
    """Search for user and their API keys by email"""
    engine = connect_to_db()
    with engine.connect() as conn:
        # Get user info
        user_result = conn.execute(text("""
            SELECT * FROM user_info WHERE email = :email;
        """), {"email": email})
        
        user_row = user_result.fetchone()
        if user_row:
            print(f"User found for email: {email}")
            print(f"  Username: {user_row[1]}")
            print(f"  Created At: {user_row[2]}")
        else:
            print(f"No user found for email: {email}")
        
        # Get API keys for this email
        api_result = conn.execute(text("""
            SELECT api_key, is_active, created_at 
            FROM api_keys 
            WHERE email = :email
            ORDER BY created_at DESC;
        """), {"email": email})
        
        print(f"\nAPI Keys for {email}:")
        for row in api_result:
            print(f"  API Key: {row[0][:8]}...{row[0][-4:]}")
            print(f"  Active: {row[1]}")
            print(f"  Created At: {row[2]}")
        print()

def main():
    """Main function to run queries"""
    print("Financial Assistant Database Query Tool")
    print("=" * 50)
    print(f"Database: {DATABASE_URL}")
    print()
    
    # Show all tables first
    show_tables()
    
    # Show user info
    show_user_info()
    
    # Show API keys
    show_api_keys()
    
    # Show telegram users
    show_telegram_users()
    
    # Example: Search for specific email if provided
    import sys
    if len(sys.argv) > 1:
        email = sys.argv[1]
        print(f"Searching for email: {email}")
        print("=" * 30)
        search_by_email(email)

if __name__ == "__main__":
    main()