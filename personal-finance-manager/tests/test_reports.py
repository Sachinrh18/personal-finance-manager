"""
Unit tests for financial reports module.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from datetime import date
from src.database import init_database, DB_PATH
from src.auth import register_user, login_user, logout_user
from src.transactions import add_transaction
from src.reports import (
    generate_monthly_report, generate_yearly_report,
    calculate_savings, format_monthly_report, format_yearly_report
)


class TestReports(unittest.TestCase):
    """Test cases for financial reports functionality."""
    
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
            cursor.execute("DELETE FROM transactions")
    
    def tearDown(self):
        """Clean up after each test."""
        import src.database
        with src.database.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM transactions")
    
    def test_generate_monthly_report(self):
        """Test generating monthly report."""
        test_date = date(2024, 6, 15)
        add_transaction(self.user_id, "income", "Salary", 5000.0, None, test_date)
        add_transaction(self.user_id, "expense", "Food", 500.0, None, test_date)
        add_transaction(self.user_id, "expense", "Rent", 1500.0, None, test_date)
        
        report = generate_monthly_report(self.user_id, 6, 2024)
        
        self.assertEqual(report['month'], 6)
        self.assertEqual(report['year'], 2024)
        self.assertEqual(report['total_income'], 5000.0)
        self.assertEqual(report['total_expenses'], 2000.0)
        self.assertEqual(report['savings'], 3000.0)
        self.assertEqual(report['transaction_count'], 3)
    
    def test_generate_yearly_report(self):
        """Test generating yearly report."""
        add_transaction(self.user_id, "income", "Salary", 5000.0, None, date(2024, 1, 15))
        add_transaction(self.user_id, "expense", "Food", 500.0, None, date(2024, 6, 15))
        add_transaction(self.user_id, "expense", "Rent", 1500.0, None, date(2024, 12, 15))
        
        report = generate_yearly_report(self.user_id, 2024)
        
        self.assertEqual(report['year'], 2024)
        self.assertEqual(report['total_income'], 5000.0)
        self.assertEqual(report['total_expenses'], 2000.0)
        self.assertEqual(report['total_savings'], 3000.0)
        self.assertEqual(len(report['monthly_reports']), 12)
    
    def test_calculate_savings(self):
        """Test calculating savings."""
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        
        add_transaction(self.user_id, "income", "Salary", 5000.0, None, date(2024, 1, 15))
        add_transaction(self.user_id, "expense", "Food", 500.0, None, date(2024, 1, 20))
        add_transaction(self.user_id, "expense", "Rent", 1500.0, None, date(2024, 1, 25))
        
        savings = calculate_savings(self.user_id, start_date, end_date)
        self.assertEqual(savings, 3000.0)
    
    def test_format_monthly_report(self):
        """Test formatting monthly report."""
        test_date = date(2024, 6, 15)
        add_transaction(self.user_id, "income", "Salary", 5000.0, None, test_date)
        add_transaction(self.user_id, "expense", "Food", 500.0, None, test_date)
        
        report = generate_monthly_report(self.user_id, 6, 2024)
        formatted = format_monthly_report(report)
        
        self.assertIn("MONTHLY FINANCIAL REPORT", formatted)
        self.assertIn("5000.00", formatted)
        self.assertIn("500.00", formatted)
    
    def test_format_yearly_report(self):
        """Test formatting yearly report."""
        add_transaction(self.user_id, "income", "Salary", 5000.0, None, date(2024, 1, 15))
        add_transaction(self.user_id, "expense", "Food", 500.0, None, date(2024, 6, 15))
        
        report = generate_yearly_report(self.user_id, 2024)
        formatted = format_yearly_report(report)
        
        self.assertIn("YEARLY FINANCIAL REPORT", formatted)
        self.assertIn("5000.00", formatted)
        self.assertIn("500.00", formatted)


if __name__ == "__main__":
    unittest.main()

