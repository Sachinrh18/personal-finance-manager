"""
Unit tests for transaction management module.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from datetime import date, timedelta
from src.database import init_database, DB_PATH
from src.auth import register_user, login_user, logout_user
from src.transactions import (
    add_transaction, update_transaction, delete_transaction,
    get_transactions, get_transaction_by_id,
    get_total_income, get_total_expenses
)


class TestTransactions(unittest.TestCase):
    """Test cases for transaction functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database before all tests."""
        cls.test_dir = tempfile.mkdtemp()
        cls.original_db_path = DB_PATH
        
        import src.database
        test_db_path = Path(cls.test_dir) / "test_finance.db"
        src.database.DB_PATH = test_db_path
        
        init_database()
        
        # Create test user
        register_user("testuser", "password123")
        success, _, user_id = login_user("testuser", "password123")
        cls.user_id = user_id if success else None
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test database after all tests."""
        logout_user()
        import src.database
        src.database.DB_PATH = cls.original_db_path
        shutil.rmtree(cls.test_dir)
    
    def setUp(self):
        """Set up before each test."""
        if not self.user_id:
            self.skipTest("Test user not created")
        login_user("testuser", "password123")
        # Clear transactions
        import src.database
        with src.database.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM transactions")
    
    def tearDown(self):
        """Clean up after each test."""
        # Clear transactions
        import src.database
        with src.database.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM transactions")
    
    def test_add_income_transaction(self):
        """Test adding an income transaction."""
        success, message, trans_id = add_transaction(
            self.user_id, "income", "Salary", 5000.0, "Monthly salary", date.today()
        )
        self.assertTrue(success)
        self.assertIsNotNone(trans_id)
    
    def test_add_expense_transaction(self):
        """Test adding an expense transaction."""
        success, message, trans_id = add_transaction(
            self.user_id, "expense", "Food", 50.0, "Groceries", date.today()
        )
        self.assertTrue(success)
        self.assertIsNotNone(trans_id)
    
    def test_add_transaction_invalid_type(self):
        """Test adding transaction with invalid type."""
        success, message, trans_id = add_transaction(
            self.user_id, "invalid", "Food", 50.0, None, date.today()
        )
        self.assertFalse(success)
        self.assertIsNone(trans_id)
    
    def test_add_transaction_invalid_category(self):
        """Test adding transaction with invalid category."""
        success, message, trans_id = add_transaction(
            self.user_id, "expense", "InvalidCategory", 50.0, None, date.today()
        )
        self.assertFalse(success)
        self.assertIsNone(trans_id)
    
    def test_add_transaction_negative_amount(self):
        """Test adding transaction with negative amount."""
        success, message, trans_id = add_transaction(
            self.user_id, "expense", "Food", -50.0, None, date.today()
        )
        self.assertFalse(success)
        self.assertIsNone(trans_id)
    
    def test_get_transactions(self):
        """Test retrieving transactions."""
        add_transaction(self.user_id, "income", "Salary", 5000.0, None, date.today())
        add_transaction(self.user_id, "expense", "Food", 50.0, None, date.today())
        
        transactions = get_transactions(self.user_id)
        self.assertEqual(len(transactions), 2)
    
    def test_get_transactions_by_date_range(self):
        """Test retrieving transactions by date range."""
        today = date.today()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)
        
        add_transaction(self.user_id, "income", "Salary", 1000.0, None, yesterday)
        add_transaction(self.user_id, "expense", "Food", 50.0, None, today)
        add_transaction(self.user_id, "expense", "Food", 30.0, None, tomorrow)
        
        transactions = get_transactions(self.user_id, start_date=today, end_date=today)
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0]['date'], str(today))
    
    def test_get_transactions_by_category(self):
        """Test retrieving transactions by category."""
        add_transaction(self.user_id, "expense", "Food", 50.0, None, date.today())
        add_transaction(self.user_id, "expense", "Rent", 1000.0, None, date.today())
        
        transactions = get_transactions(self.user_id, category="Food")
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0]['category'], "Food")
    
    def test_update_transaction(self):
        """Test updating a transaction."""
        success, _, trans_id = add_transaction(
            self.user_id, "expense", "Food", 50.0, "Groceries", date.today()
        )
        
        success, message = update_transaction(trans_id, self.user_id, amount=75.0)
        self.assertTrue(success)
        
        transaction = get_transaction_by_id(trans_id, self.user_id)
        self.assertEqual(transaction['amount'], 75.0)
    
    def test_update_transaction_not_found(self):
        """Test updating a non-existent transaction."""
        success, message = update_transaction(99999, self.user_id, amount=100.0)
        self.assertFalse(success)
        self.assertIn("not found", message.lower())
    
    def test_delete_transaction(self):
        """Test deleting a transaction."""
        success, _, trans_id = add_transaction(
            self.user_id, "expense", "Food", 50.0, None, date.today()
        )
        
        success, message = delete_transaction(trans_id, self.user_id)
        self.assertTrue(success)
        
        transaction = get_transaction_by_id(trans_id, self.user_id)
        self.assertIsNone(transaction)
    
    def test_delete_transaction_not_found(self):
        """Test deleting a non-existent transaction."""
        success, message = delete_transaction(99999, self.user_id)
        self.assertFalse(success)
        self.assertIn("not found", message.lower())
    
    def test_get_total_income(self):
        """Test calculating total income."""
        add_transaction(self.user_id, "income", "Salary", 5000.0, None, date.today())
        add_transaction(self.user_id, "income", "Bonus", 1000.0, None, date.today())
        add_transaction(self.user_id, "expense", "Food", 50.0, None, date.today())
        
        total = get_total_income(self.user_id)
        self.assertEqual(total, 6000.0)
    
    def test_get_total_expenses(self):
        """Test calculating total expenses."""
        add_transaction(self.user_id, "expense", "Food", 50.0, None, date.today())
        add_transaction(self.user_id, "expense", "Rent", 1000.0, None, date.today())
        add_transaction(self.user_id, "income", "Salary", 5000.0, None, date.today())
        
        total = get_total_expenses(self.user_id)
        self.assertEqual(total, 1050.0)


if __name__ == "__main__":
    unittest.main()

