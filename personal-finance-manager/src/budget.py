"""
Budget management module for setting budgets and checking budget status.
"""

from datetime import date
from typing import List, Dict, Optional
from src.database import get_db_connection
from src.transactions import get_total_expenses, get_transactions
from src.models import ALL_CATEGORIES


def set_budget(
    user_id: int,
    category: str,
    monthly_limit: float,
    month: int,
    year: int
) -> tuple[bool, str]:
    """
    Set or update a monthly budget for a category.
    
    Args:
        user_id: User ID
        category: Budget category
        monthly_limit: Monthly spending limit
        month: Month (1-12)
        year: Year
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    if category not in ALL_CATEGORIES:
        return False, f"Invalid category. Must be one of: {', '.join(ALL_CATEGORIES)}"
    
    if monthly_limit <= 0:
        return False, "Monthly limit must be greater than 0."
    
    if not (1 <= month <= 12):
        return False, "Month must be between 1 and 12."
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check if budget already exists
            cursor.execute(
                """SELECT id FROM budgets 
                   WHERE user_id = ? AND category = ? AND month = ? AND year = ?""",
                (user_id, category, month, year)
            )
            existing = cursor.fetchone()
            
            if existing:
                # Update existing budget
                cursor.execute(
                    """UPDATE budgets SET monthly_limit = ?
                       WHERE user_id = ? AND category = ? AND month = ? AND year = ?""",
                    (monthly_limit, user_id, category, month, year)
                )
                return True, f"Budget updated for {category} in {month}/{year}: ${monthly_limit:,.2f}"
            else:
                # Insert new budget
                cursor.execute(
                    """INSERT INTO budgets (user_id, category, monthly_limit, month, year)
                       VALUES (?, ?, ?, ?, ?)""",
                    (user_id, category, monthly_limit, month, year)
                )
                return True, f"Budget set for {category} in {month}/{year}: ${monthly_limit:,.2f}"
    
    except Exception as e:
        return False, f"Failed to set budget: {str(e)}"


def get_budget(user_id: int, category: str, month: int, year: int) -> Optional[dict]:
    """
    Get budget for a specific category and month.
    
    Args:
        user_id: User ID
        category: Budget category
        month: Month (1-12)
        year: Year
    
    Returns:
        Budget dictionary or None if not found
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT * FROM budgets 
                   WHERE user_id = ? AND category = ? AND month = ? AND year = ?""",
                (user_id, category, month, year)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
    except Exception:
        return None


def get_all_budgets(user_id: int, month: int, year: int) -> List[dict]:
    """
    Get all budgets for a user for a specific month.
    
    Args:
        user_id: User ID
        month: Month (1-12)
        year: Year
    
    Returns:
        List of budget dictionaries
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT * FROM budgets 
                   WHERE user_id = ? AND month = ? AND year = ?
                   ORDER BY category""",
                (user_id, month, year)
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    except Exception:
        return []


def check_budget_status(user_id: int, month: int, year: int) -> Dict:
    """
    Check budget status for all categories in a month.
    
    Args:
        user_id: User ID
        month: Month (1-12)
        year: Year
    
    Returns:
        Dictionary containing budget status information
    """
    budgets = get_all_budgets(user_id, month, year)
    
    # Calculate start and end dates for the month
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month + 1, 1)
    
    from datetime import timedelta
    end_date = end_date - timedelta(days=1)
    
    status_list = []
    
    for budget in budgets:
        category = budget['category']
        limit = budget['monthly_limit']
        
        # Get expenses for this category in this month
        transactions = get_transactions(user_id, start_date, end_date, category=category, transaction_type='expense')
        spent = sum(t['amount'] for t in transactions)
        
        remaining = limit - spent
        percentage = (spent / limit * 100) if limit > 0 else 0
        exceeded = spent > limit
        
        status_list.append({
            'category': category,
            'limit': limit,
            'spent': spent,
            'remaining': remaining,
            'percentage': percentage,
            'exceeded': exceeded
        })
    
    return {
        'month': month,
        'year': year,
        'budgets': status_list
    }


def get_budget_alerts(user_id: int, month: int, year: int) -> List[Dict]:
    """
    Get budget alerts for categories that have exceeded their limits.
    
    Args:
        user_id: User ID
        month: Month (1-12)
        year: Year
    
    Returns:
        List of alert dictionaries for exceeded budgets
    """
    status = check_budget_status(user_id, month, year)
    alerts = []
    
    for budget_status in status['budgets']:
        if budget_status['exceeded']:
            alerts.append({
                'category': budget_status['category'],
                'limit': budget_status['limit'],
                'spent': budget_status['spent'],
                'over_budget': budget_status['spent'] - budget_status['limit'],
                'percentage': budget_status['percentage']
            })
    
    return alerts


def format_budget_status(status: Dict) -> str:
    """
    Format budget status as a readable string.
    
    Args:
        status: Budget status dictionary from check_budget_status
    
    Returns:
        Formatted status string
    """
    month_names = [
        '', 'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    
    month_name = month_names[status['month']]
    year = status['year']
    
    lines = [
        f"\n{'='*70}",
        f"BUDGET STATUS - {month_name.upper()} {year}",
        f"{'='*70}",
        "",
        f"{'Category':<20s} {'Limit':>15s} {'Spent':>15s} {'Remaining':>15s} {'%':>5s}",
        "-" * 70,
    ]
    
    for budget in status['budgets']:
        category = budget['category']
        limit = budget['limit']
        spent = budget['spent']
        remaining = budget['remaining']
        percentage = budget['percentage']
        
        # Add warning indicator if exceeded
        indicator = "⚠️ " if budget['exceeded'] else "  "
        
        lines.append(
            f"{indicator}{category:<18s} ${limit:>14,.2f} ${spent:>14,.2f} "
            f"${remaining:>14,.2f} {percentage:>4.1f}%"
        )
    
    lines.append("")
    lines.append("=" * 70)
    
    return "\n".join(lines)


def format_budget_alerts(alerts: List[Dict]) -> str:
    """
    Format budget alerts as a readable string.
    
    Args:
        alerts: List of alert dictionaries from get_budget_alerts
    
    Returns:
        Formatted alerts string
    """
    if not alerts:
        return "\n✅ No budget alerts. All budgets are within limits!\n"
    
    lines = [
        f"\n{'='*70}",
        "⚠️  BUDGET ALERTS - CATEGORIES EXCEEDED",
        f"{'='*70}",
        "",
    ]
    
    for alert in alerts:
        lines.append(f"Category: {alert['category']}")
        lines.append(f"  Budget Limit:     ${alert['limit']:,.2f}")
        lines.append(f"  Amount Spent:     ${alert['spent']:,.2f}")
        lines.append(f"  Over Budget:      ${alert['over_budget']:,.2f}")
        lines.append(f"  Percentage Used:  {alert['percentage']:.1f}%")
        lines.append("")
    
    lines.append("=" * 70)
    
    return "\n".join(lines)

