"""
Unit tests for backup and restore module.
"""

import unittest
import os
import tempfile
import shutil
from pathlib import Path
from src.database import init_database, DB_PATH
from src.backup import backup_database, restore_database, list_backups


class TestBackup(unittest.TestCase):
    """Test cases for backup and restore functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database before all tests."""
        cls.test_dir = tempfile.mkdtemp()
        cls.original_db_path = DB_PATH
        
        import src.database
        test_db_path = Path(cls.test_dir) / "test_finance.db"
        src.database.DB_PATH = test_db_path
        
        init_database()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test database after all tests."""
        import src.database
        src.database.DB_PATH = cls.original_db_path
        shutil.rmtree(cls.test_dir)
    
    def test_backup_database(self):
        """Test backing up database."""
        success, message = backup_database()
        self.assertTrue(success)
        self.assertIn("backed up", message.lower())
        
        # Verify backup file exists
        backups = list_backups()
        self.assertGreater(len(backups), 0)
    
    def test_backup_database_custom_path(self):
        """Test backing up database to custom path."""
        backup_path = str(Path(self.test_dir) / "custom_backup.db")
        success, message = backup_database(backup_path)
        
        self.assertTrue(success)
        self.assertTrue(os.path.exists(backup_path))
    
    def test_restore_database(self):
        """Test restoring database from backup."""
        # Create a backup first
        backup_path = str(Path(self.test_dir) / "restore_test_backup.db")
        backup_success, _ = backup_database(backup_path)
        self.assertTrue(backup_success)
        
        # Restore from backup
        success, message = restore_database(backup_path)
        self.assertTrue(success)
        self.assertIn("restored", message.lower())
    
    def test_restore_database_invalid_path(self):
        """Test restoring from invalid backup path."""
        success, message = restore_database("/nonexistent/path/backup.db")
        self.assertFalse(success)
        self.assertIn("not found", message.lower())
    
    def test_list_backups(self):
        """Test listing backup files."""
        # Create multiple backups
        backup_database()
        backup_database()
        
        backups = list_backups()
        self.assertGreaterEqual(len(backups), 2)
        
        # Verify all are valid paths
        for backup in backups:
            self.assertTrue(os.path.exists(backup))


if __name__ == "__main__":
    unittest.main()

