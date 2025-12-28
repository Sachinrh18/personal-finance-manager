"""
Backup and restore module for database management.
"""

import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, List
from src.database import get_db_path, get_db_connection


def backup_database(backup_path: Optional[str] = None) -> tuple[bool, str]:
    """
    Create a backup of the database.
    
    Args:
        backup_path: Optional custom backup path. If None, uses timestamped filename.
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    db_path = Path(get_db_path())
    
    if not db_path.exists():
        return False, "Database file not found. Nothing to backup."
    
    try:
        # Create backup directory if it doesn't exist
        backup_dir = db_path.parent / "backups"
        backup_dir.mkdir(exist_ok=True)
        
        if backup_path is None:
            # Generate timestamped backup filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"finance_backup_{timestamp}.db"
            backup_path = str(backup_dir / backup_filename)
        else:
            backup_path = str(Path(backup_path))
        
        # Copy database file
        shutil.copy2(db_path, backup_path)
        
        return True, f"Database backed up successfully to: {backup_path}"
    
    except Exception as e:
        return False, f"Backup failed: {str(e)}"


def restore_database(backup_path: str) -> tuple[bool, str]:
    """
    Restore database from a backup file.
    
    Args:
        backup_path: Path to the backup file
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    backup_file = Path(backup_path)
    db_path = Path(get_db_path())
    
    if not backup_file.exists():
        return False, f"Backup file not found: {backup_path}"
    
    if not backup_file.is_file():
        return False, f"Invalid backup path: {backup_path}"
    
    try:
        # Verify it's a valid SQLite database
        import sqlite3
        test_conn = sqlite3.connect(str(backup_file))
        test_conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        test_conn.close()
        
        # Create backup of current database before restoring
        if db_path.exists():
            current_backup = str(db_path.parent / f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
            shutil.copy2(db_path, current_backup)
        
        # Ensure database directory exists
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Restore from backup
        shutil.copy2(backup_file, db_path)
        
        return True, f"Database restored successfully from: {backup_path}"
    
    except sqlite3.Error as e:
        return False, f"Invalid backup file (not a valid SQLite database): {str(e)}"
    except Exception as e:
        return False, f"Restore failed: {str(e)}"


def list_backups() -> List[str]:
    """
    List all available backup files.
    
    Returns:
        List of backup file paths
    """
    db_path = Path(get_db_path())
    backup_dir = db_path.parent / "backups"
    
    if not backup_dir.exists():
        return []
    
    backups = []
    for backup_file in sorted(backup_dir.glob("*.db"), reverse=True):
        backups.append(str(backup_file))
    
    return backups

