"""
Unit tests for budget management module.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from datetime import date
from src.database import init_database, DB_PATH
from src.auth import register_user, login_user, logout_user
from src.transactions import add_transaction
from src.budget import (
    set_budget, get_budget, get_all_budgets,
    check_budget_status, get_budget_alerts,
    format_budget_status, format_budget_alerts
)


class TestBudget(unittest.TestCase):
    """Test cases for budget functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database before all tests."""
        cls.test_dir = tempfile.mkdtemp()
        cls.original_db_path = DB_PATH
        
        import src.database
        test_db_path = Path(cls.test_dir) / "test_finance.db"
        src.database.DB_PATH = test_db_path
        
        init_database()
        
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
        import src.database
        with src.database.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM budgets")
            cursor.execute("DELETE FROM transactions")
    
    def tearDown(self):
        """Clean up after each test."""
        import src.database
        with src.database.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM budgets")
            cursor.execute("DELETE FROM transactions")
    
    def test_set_budget(self):
        """Test setting a budget."""
        success, message = set_budget(self.user_id, "Food", 500.0, 6, 2024)
        self.assertTrue(success)
        self.assertIn("set", message.lower())
    
    def test_set_budget_update_existing(self):
        """Test updating an existing budget."""
        set_budget(self.user_id, "Food", 500.0, 6, 2024)
        success, message = set_budget(self.user_id, "Food", 600.0, 6, 2024)
        self.assertTrue(success)
        self.assertIn("updated", message.lower())
    
    def test_set_budget_invalid_category(self):
        """Test setting budget with invalid category."""
        success, message = set_budget(self.user_id, "InvalidCategory", 500.0, 6, 2024)
        self.assertFalse(success)
        self.assertIn("invalid", message.lower())
    
    def test_set_budget_invalid_amount(self):
        """Test setting budget with invalid amount."""
        success, message = set_budget(self.user_id, "Food", -100.0, 6, 2024)
        self.assertFalse(success)
        self.assertIn("greater than 0", message.lower())
    
    def test_get_budget(self):
        """Test retrieving a budget."""
        set_budget(self.user_id, "Food", 500.0, 6, 2024)
        budget = get_budget(self.user_id, "Food", 6, 2024)
        
        self.assertIsNotNone(budget)
        self.assertEqual(budget['category'], "Food")
        self.assertEqual(budget['monthly_limit'], 500.0)
    
    def test_get_all_budgets(self):
        """Test retrieving all budgets for a month."""
        set_budget(self.user_id, "Food", 500.0, 6, 2024)
        set_budget(self.user_id, "Rent", 1500.0, 6, 2024)
        
        budgets = get_all_budgets(self.user_id, 6, 2024)
        self.assertEqual(len(budgets), 2)
    
    def test_check_budget_status(self):
        """Test checking budget status."""
        set_budget(self.user_id, "Food", 500.0, 6, 2024)
        add_transaction(self.user_id, "expense", "Food", 300.0, None, date(2024, 6, 15))
        
        status = check_budget_status(self.user_id, 6, 2024)
        
        self.assertEqual(status['month'], 6)
        self.assertEqual(status['year'], 2024)
        self.assertEqual(len(status['budgets']), 1)
        self.assertEqual(status['budgets'][0]['spent'], 300.0)
        self.assertEqual(status['budgets'][0]['remaining'], 200.0)
    
    def test_get_budget_alerts_exceeded(self):
        """Test getting budget alerts for exceeded budgets."""
        set_budget(self.user_id, "Food", 500.0, 6, 2024)
        add_transaction(self.user_id, "expense", "Food", 600.0, None, date(2024, 6, 15))
        
        alerts = get_budget_alerts(self.user_id, 6, 2024)
        
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]['category'], "Food")
        self.assertEqual(alerts[0]['spent'], 600.0)
        self.assertGreater(alerts[0]['over_budget'], 0)
    
    def test_get_budget_alerts_not_exceeded(self):
        """Test getting budget alerts when budgets are not exceeded."""
        set_budget(self.user_id, "Food", 500.0, 6, 2024)
        add_transaction(self.user_id, "expense", "Food", 300.0, None, date(2024, 6, 15))
        
        alerts = get_budget_alerts(self.user_id, 6, 2024)
        
        self.assertEqual(len(alerts), 0)
    
    def test_format_budget_status(self):
        """Test formatting budget status."""
        set_budget(self.user_id, "Food", 500.0, 6, 2024)
        add_transaction(self.user_id, "expense", "Food", 300.0, None, date(2024, 6, 15))
        
        status = check_budget_status(self.user_id, 6, 2024)
        formatted = format_budget_status(status)
        
        self.assertIn("BUDGET STATUS", formatted)
        self.assertIn("Food", formatted)
        self.assertIn("500.00", formatted)
    
    def test_format_budget_alerts(self):
        """Test formatting budget alerts."""
        set_budget(self.user_id, "Food", 500.0, 6, 2024)
        add_transaction(self.user_id, "expense", "Food", 600.0, None, date(2024, 6, 15))
        
        alerts = get_budget_alerts(self.user_id, 6, 2024)
        formatted = format_budget_alerts(alerts)
        
        self.assertIn("BUDGET ALERTS", formatted)
        self.assertIn("Food", formatted)
        self.assertIn("600.00", formatted)


if __name__ == "__main__":
    unittest.main()

