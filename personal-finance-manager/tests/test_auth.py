"""
Unit tests for authentication module.
"""

import unittest
import os
import tempfile
import shutil
from pathlib import Path
from src.database import init_database, DB_PATH, get_db_path
from src.auth import (
    register_user, login_user, logout_user,
    get_current_user_id, is_authenticated, hash_password, verify_password
)


class TestAuth(unittest.TestCase):
    """Test cases for authentication functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database before all tests."""
        # Create a temporary directory for test database
        cls.test_dir = tempfile.mkdtemp()
        cls.original_db_path = DB_PATH
        
        # Override DB_PATH for testing
        test_db_path = Path(cls.test_dir) / "test_finance.db"
        import src.database
        src.database.DB_PATH = test_db_path
        
        # Initialize test database
        init_database()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test database after all tests."""
        # Restore original DB_PATH
        import src.database
        src.database.DB_PATH = cls.original_db_path
        
        # Remove test directory
        shutil.rmtree(cls.test_dir)
    
    def setUp(self):
        """Set up before each test."""
        logout_user()
    
    def tearDown(self):
        """Clean up after each test."""
        logout_user()
        # Clear test database
        import src.database
        with src.database.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users")
            cursor.execute("DELETE FROM transactions")
            cursor.execute("DELETE FROM budgets")
    
    def test_hash_password(self):
        """Test password hashing."""
        password = "testpassword123"
        hash1, salt1 = hash_password(password)
        hash2, salt2 = hash_password(password)
        
        # Different salts should produce different hashes
        self.assertNotEqual(hash1, hash2)
        self.assertNotEqual(salt1, salt2)
        
        # But both should verify correctly
        self.assertTrue(verify_password(password, hash1, salt1))
        self.assertTrue(verify_password(password, hash2, salt2))
    
    def test_verify_password(self):
        """Test password verification."""
        password = "testpassword123"
        hash_val, salt = hash_password(password)
        
        self.assertTrue(verify_password(password, hash_val, salt))
        self.assertFalse(verify_password("wrongpassword", hash_val, salt))
    
    def test_register_user_success(self):
        """Test successful user registration."""
        success, message = register_user("testuser", "password123")
        self.assertTrue(success)
        self.assertIn("successfully", message.lower())
    
    def test_register_user_duplicate(self):
        """Test registration with duplicate username."""
        register_user("testuser", "password123")
        success, message = register_user("testuser", "password456")
        self.assertFalse(success)
        self.assertIn("already exists", message.lower())
    
    def test_register_user_empty_username(self):
        """Test registration with empty username."""
        success, message = register_user("", "password123")
        self.assertFalse(success)
        self.assertIn("empty", message.lower())
    
    def test_register_user_short_password(self):
        """Test registration with short password."""
        success, message = register_user("testuser", "abc")
        self.assertFalse(success)
        self.assertIn("4 characters", message.lower())
    
    def test_login_user_success(self):
        """Test successful login."""
        register_user("testuser", "password123")
        success, message, user_id = login_user("testuser", "password123")
        self.assertTrue(success)
        self.assertIsNotNone(user_id)
        self.assertEqual(get_current_user_id(), user_id)
    
    def test_login_user_wrong_password(self):
        """Test login with wrong password."""
        register_user("testuser", "password123")
        success, message, user_id = login_user("testuser", "wrongpassword")
        self.assertFalse(success)
        self.assertIsNone(user_id)
    
    def test_login_user_nonexistent(self):
        """Test login with nonexistent user."""
        success, message, user_id = login_user("nonexistent", "password123")
        self.assertFalse(success)
        self.assertIsNone(user_id)
    
    def test_logout_user(self):
        """Test user logout."""
        register_user("testuser", "password123")
        login_user("testuser", "password123")
        self.assertTrue(is_authenticated())
        
        logout_user()
        self.assertFalse(is_authenticated())
        self.assertIsNone(get_current_user_id())


if __name__ == "__main__":
    unittest.main()

