"""
Data models for the Personal Finance Management Application.
"""

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class User:
    """User model."""
    id: int
    username: str
    password_hash: str
    created_at: str


@dataclass
class Transaction:
    """Transaction model."""
    id: int
    user_id: int
    type: str  # 'income' or 'expense'
    category: str
    amount: float
    description: Optional[str]
    date: date
    created_at: str


@dataclass
class Budget:
    """Budget model."""
    id: int
    user_id: int
    category: str
    monthly_limit: float
    month: int
    year: int
    created_at: str


# Predefined categories
INCOME_CATEGORIES = [
    "Salary",
    "Freelance",
    "Investment",
    "Bonus",
    "Other Income"
]

EXPENSE_CATEGORIES = [
    "Food",
    "Rent",
    "Utilities",
    "Transportation",
    "Entertainment",
    "Healthcare",
    "Education",
    "Shopping",
    "Bills",
    "Other Expense"
]

ALL_CATEGORIES = INCOME_CATEGORIES + EXPENSE_CATEGORIES

