"""
Transaction management module for income and expense tracking.
"""

from datetime import date, datetime
from typing import Optional, List
from src.database import get_db_connection
from src.models import Transaction, ALL_CATEGORIES


def add_transaction(
    user_id: int,
    transaction_type: str,
    category: str,
    amount: float,
    description: Optional[str] = None,
    transaction_date: Optional[date] = None
) -> tuple[bool, str, Optional[int]]:
    """
    Add a new transaction (income or expense).
    
    Args:
        user_id: User ID
        transaction_type: 'income' or 'expense'
        category: Transaction category
        amount: Transaction amount (must be positive)
        description: Optional description
        transaction_date: Transaction date (defaults to today)
    
    Returns:
        Tuple of (success: bool, message: str, transaction_id: Optional[int])
    """
    if transaction_type not in ['income', 'expense']:
        return False, "Transaction type must be 'income' or 'expense'.", None
    
    if category not in ALL_CATEGORIES:
        return False, f"Invalid category. Must be one of: {', '.join(ALL_CATEGORIES)}", None
    
    if amount <= 0:
        return False, "Amount must be greater than 0.", None
    
    if transaction_date is None:
        transaction_date = date.today()
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO transactions 
                   (user_id, type, category, amount, description, date)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (user_id, transaction_type, category, amount, description or "", transaction_date)
            )
            transaction_id = cursor.lastrowid
            return True, f"{transaction_type.capitalize()} added successfully!", transaction_id
    
    except Exception as e:
        return False, f"Failed to add transaction: {str(e)}", None


def update_transaction(
    transaction_id: int,
    user_id: int,
    **kwargs
) -> tuple[bool, str]:
    """
    Update an existing transaction.
    
    Args:
        transaction_id: Transaction ID to update
        user_id: User ID (for authorization)
        **kwargs: Fields to update (type, category, amount, description, date)
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    allowed_fields = ['type', 'category', 'amount', 'description', 'date']
    updates = {k: v for k, v in kwargs.items() if k in allowed_fields and v is not None}
    
    if not updates:
        return False, "No valid fields to update."
    
    # Validate transaction type if provided
    if 'type' in updates and updates['type'] not in ['income', 'expense']:
        return False, "Transaction type must be 'income' or 'expense'."
    
    # Validate category if provided
    if 'category' in updates and updates['category'] not in ALL_CATEGORIES:
        return False, f"Invalid category. Must be one of: {', '.join(ALL_CATEGORIES)}"
    
    # Validate amount if provided
    if 'amount' in updates and updates['amount'] <= 0:
        return False, "Amount must be greater than 0."
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Verify transaction belongs to user
            cursor.execute(
                "SELECT id FROM transactions WHERE id = ? AND user_id = ?",
                (transaction_id, user_id)
            )
            if not cursor.fetchone():
                return False, "Transaction not found or access denied."
            
            # Build update query
            set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
            values = list(updates.values()) + [transaction_id, user_id]
            
            cursor.execute(
                f"UPDATE transactions SET {set_clause} WHERE id = ? AND user_id = ?",
                values
            )
            
            return True, "Transaction updated successfully!"
    
    except Exception as e:
        return False, f"Failed to update transaction: {str(e)}"


def delete_transaction(transaction_id: int, user_id: int) -> tuple[bool, str]:
    """
    Delete a transaction.
    
    Args:
        transaction_id: Transaction ID to delete
        user_id: User ID (for authorization)
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Verify transaction belongs to user
            cursor.execute(
                "SELECT id FROM transactions WHERE id = ? AND user_id = ?",
                (transaction_id, user_id)
            )
            if not cursor.fetchone():
                return False, "Transaction not found or access denied."
            
            cursor.execute(
                "DELETE FROM transactions WHERE id = ? AND user_id = ?",
                (transaction_id, user_id)
            )
            
            return True, "Transaction deleted successfully!"
    
    except Exception as e:
        return False, f"Failed to delete transaction: {str(e)}"


def get_transactions(
    user_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    category: Optional[str] = None,
    transaction_type: Optional[str] = None,
    limit: Optional[int] = None
) -> List[dict]:
    """
    Get transactions for a user with optional filters.
    
    Args:
        user_id: User ID
        start_date: Filter transactions from this date
        end_date: Filter transactions until this date
        category: Filter by category
        transaction_type: Filter by type ('income' or 'expense')
        limit: Maximum number of transactions to return
    
    Returns:
        List of transaction dictionaries
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM transactions WHERE user_id = ?"
            params = [user_id]
            
            if start_date:
                query += " AND date >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND date <= ?"
                params.append(end_date)
            
            if category:
                query += " AND category = ?"
                params.append(category)
            
            if transaction_type:
                query += " AND type = ?"
                params.append(transaction_type)
            
            query += " ORDER BY date DESC, created_at DESC"
            
            if limit:
                query += " LIMIT ?"
                params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
    
    except Exception as e:
        print(f"Error fetching transactions: {str(e)}")
        return []


def get_transaction_by_id(transaction_id: int, user_id: int) -> Optional[dict]:
    """
    Get a specific transaction by ID.
    
    Args:
        transaction_id: Transaction ID
        user_id: User ID (for authorization)
    
    Returns:
        Transaction dictionary or None if not found
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM transactions WHERE id = ? AND user_id = ?",
                (transaction_id, user_id)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
    except Exception:
        return None


def get_total_income(user_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None) -> float:
    """Get total income for a user within a date range."""
    transactions = get_transactions(user_id, start_date, end_date, transaction_type='income')
    return sum(t['amount'] for t in transactions)


def get_total_expenses(user_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None) -> float:
    """Get total expenses for a user within a date range."""
    transactions = get_transactions(user_id, start_date, end_date, transaction_type='expense')
    return sum(t['amount'] for t in transactions)

