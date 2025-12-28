"""
Authentication module for user registration and login.
"""

import hashlib
import secrets
from typing import Optional
from src.database import get_db_connection


# Global variable to store current logged-in user
_current_user_id: Optional[int] = None


def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    """
    Hash a password using SHA-256 with salt.
    
    Args:
        password: Plain text password
        salt: Optional salt (if None, generates a new one)
    
    Returns:
        Tuple of (hashed_password, salt)
    """
    if salt is None:
        salt = secrets.token_hex(16)
    
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return password_hash, salt


def verify_password(password: str, password_hash: str, salt: str) -> bool:
    """
    Verify a password against a hash and salt.
    
    Args:
        password: Plain text password to verify
        password_hash: Stored password hash
        salt: Salt used for hashing
    
    Returns:
        True if password matches, False otherwise
    """
    computed_hash, _ = hash_password(password, salt)
    return computed_hash == password_hash


def register_user(username: str, password: str) -> tuple[bool, str]:
    """
    Register a new user.
    
    Args:
        username: Unique username
        password: Plain text password
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    if not username or not username.strip():
        return False, "Username cannot be empty."
    
    if not password or len(password) < 4:
        return False, "Password must be at least 4 characters long."
    
    username = username.strip().lower()
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check if username already exists
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                return False, "Username already exists. Please choose a different one."
            
            # Hash password
            password_hash, salt = hash_password(password)
            # Store hash and salt together (format: hash:salt)
            stored_hash = f"{password_hash}:{salt}"
            
            # Insert new user
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, stored_hash)
            )
            
            return True, f"User '{username}' registered successfully!"
    
    except Exception as e:
        return False, f"Registration failed: {str(e)}"


def login_user(username: str, password: str) -> tuple[bool, str, Optional[int]]:
    """
    Authenticate a user and set current session.
    
    Args:
        username: Username
        password: Plain text password
    
    Returns:
        Tuple of (success: bool, message: str, user_id: Optional[int])
    """
    if not username or not password:
        return False, "Username and password are required.", None
    
    username = username.strip().lower()
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get user from database
            cursor.execute(
                "SELECT id, password_hash FROM users WHERE username = ?",
                (username,)
            )
            user = cursor.fetchone()
            
            if not user:
                return False, "Invalid username or password.", None
            
            user_id, stored_hash = user
            
            # Extract hash and salt
            if ':' not in stored_hash:
                return False, "Invalid password format in database.", None
            
            password_hash, salt = stored_hash.split(':', 1)
            
            # Verify password
            if not verify_password(password, password_hash, salt):
                return False, "Invalid username or password.", None
            
            # Set current user
            global _current_user_id
            _current_user_id = user_id
            
            return True, f"Welcome back, {username}!", user_id
    
    except Exception as e:
        return False, f"Login failed: {str(e)}", None


def logout_user():
    """Log out the current user."""
    global _current_user_id
    _current_user_id = None


def get_current_user_id() -> Optional[int]:
    """
    Get the current logged-in user ID.
    
    Returns:
        User ID if logged in, None otherwise
    """
    return _current_user_id


def is_authenticated() -> bool:
    """
    Check if a user is currently authenticated.
    
    Returns:
        True if user is logged in, False otherwise
    """
    return _current_user_id is not None


def get_user_by_id(user_id: int) -> Optional[dict]:
    """
    Get user information by ID.
    
    Args:
        user_id: User ID
    
    Returns:
        User dictionary or None if not found
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            return dict(user) if user else None
    except Exception:
        return None

