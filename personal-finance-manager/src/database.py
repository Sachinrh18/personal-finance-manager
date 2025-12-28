"""
Database module for managing SQLite database connections and schema.
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path


DB_PATH = Path(__file__).parent.parent / "data" / "finance.db"


def get_db_path():
    """Get the database file path."""
    return str(DB_PATH)


@contextmanager
def get_db_connection():
    """
    Context manager for database connections.
    Ensures proper connection handling and transaction management.
    """
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row  # Enable column access by name
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_database():
    """
    Initialize the database with required tables.
    Creates tables for users, transactions, and budgets if they don't exist.
    """
    # Ensure data directory exists
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create transactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
                category TEXT NOT NULL,
                amount REAL NOT NULL CHECK(amount > 0),
                description TEXT,
                date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Create budgets table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                category TEXT NOT NULL,
                monthly_limit REAL NOT NULL CHECK(monthly_limit > 0),
                month INTEGER NOT NULL CHECK(month >= 1 AND month <= 12),
                year INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE(user_id, category, month, year)
            )
        """)
        
        # Create indexes for better query performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_transactions_user_date 
            ON transactions(user_id, date)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_transactions_user_category 
            ON transactions(user_id, category)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_budgets_user_month_year 
            ON budgets(user_id, month, year)
        """)
        
        conn.commit()


if __name__ == "__main__":
    init_database()
    print("Database initialized successfully!")

