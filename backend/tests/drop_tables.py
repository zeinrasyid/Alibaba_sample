#!/usr/bin/env python3
"""
Database cleanup script for Financial Assistant
Drops old tables to prepare for new schema
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

def drop_old_tables():
    """Drop old tables that are no longer used in new schema"""
    engine = connect_to_db()
    
    # Tables to drop (old schema)
    old_tables = [
        "telegram_users",
        "transactions", 
        "api_keys",  # old version
        "users"      # old version
    ]
    
    with engine.connect() as conn:
        # Need to use autocommit for DDL statements
        trans = conn.begin()
        
        for table in old_tables:
            try:
                # Check if table exists first
                result = conn.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = :table_name
                    );
                """), {"table_name": table})
                
                table_exists = result.scalar()
                
                if table_exists:
                    print(f"Dropping table: {table}")
                    conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE;"))
                    print(f"✓ Table {table} dropped successfully")
                else:
                    print(f"- Table {table} does not exist, skipping")
            except Exception as e:
                print(f"✗ Error dropping table {table}: {e}")
        
        trans.commit()
        print("\nTable cleanup completed!")

def show_remaining_tables():
    """Show tables that remain in the database"""
    engine = connect_to_db()
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """))
        
        print("\nTables remaining in database:")
        for row in result:
            print(f"  - {row[0]}")

def main():
    """Main function to run cleanup"""
    print("Financial Assistant Database Cleanup Tool")
    print("=" * 50)
    print(f"Database: {DATABASE_URL}")
    print()
    
    print("This will drop old tables that are no longer used in the new schema.")
    print("New tables (user_info, api_keys) will remain intact.")
    print()
    
    confirm = input("Do you want to proceed? (yes/no): ")
    if confirm.lower() in ['yes', 'y']:
        drop_old_tables()
        show_remaining_tables()
        print("\nNote: After cleanup, run the application to create new tables if needed.")
    else:
        print("Operation cancelled.")

if __name__ == "__main__":
    main()