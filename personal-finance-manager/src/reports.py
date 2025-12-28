"""
Financial reports module for generating monthly and yearly reports.
"""

from datetime import date, datetime
from typing import Dict, List
from src.transactions import get_transactions, get_total_income, get_total_expenses
from src.models import ALL_CATEGORIES


def calculate_savings(user_id: int, start_date: date, end_date: date) -> float:
    """
    Calculate savings (income - expenses) for a date range.
    
    Args:
        user_id: User ID
        start_date: Start date
        end_date: End date
    
    Returns:
        Savings amount (can be negative)
    """
    income = get_total_income(user_id, start_date, end_date)
    expenses = get_total_expenses(user_id, start_date, end_date)
    return income - expenses


def generate_monthly_report(user_id: int, month: int, year: int) -> Dict:
    """
    Generate a monthly financial report.
    
    Args:
        user_id: User ID
        month: Month (1-12)
        year: Year
    
    Returns:
        Dictionary containing report data
    """
    start_date = date(year, month, 1)
    
    # Get last day of month
    if month == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month + 1, 1)
    
    # Subtract one day to get last day of current month
    from datetime import timedelta
    end_date = end_date - timedelta(days=1)
    
    # Get all transactions for the month
    transactions = get_transactions(user_id, start_date, end_date)
    
    # Calculate totals
    total_income = get_total_income(user_id, start_date, end_date)
    total_expenses = get_total_expenses(user_id, start_date, end_date)
    savings = total_income - total_expenses
    
    # Category breakdown
    income_by_category: Dict[str, float] = {}
    expenses_by_category: Dict[str, float] = {}
    
    for transaction in transactions:
        category = transaction['category']
        amount = transaction['amount']
        
        if transaction['type'] == 'income':
            income_by_category[category] = income_by_category.get(category, 0) + amount
        else:
            expenses_by_category[category] = expenses_by_category.get(category, 0) + amount
    
    return {
        'month': month,
        'year': year,
        'start_date': start_date,
        'end_date': end_date,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'savings': savings,
        'income_by_category': income_by_category,
        'expenses_by_category': expenses_by_category,
        'transaction_count': len(transactions)
    }


def generate_yearly_report(user_id: int, year: int) -> Dict:
    """
    Generate a yearly financial report with monthly breakdown.
    
    Args:
        user_id: User ID
        year: Year
    
    Returns:
        Dictionary containing report data
    """
    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)
    
    # Calculate yearly totals
    total_income = get_total_income(user_id, start_date, end_date)
    total_expenses = get_total_expenses(user_id, start_date, end_date)
    total_savings = total_income - total_expenses
    
    # Monthly breakdown
    monthly_reports = []
    for month in range(1, 13):
        monthly_report = generate_monthly_report(user_id, month, year)
        monthly_reports.append(monthly_report)
    
    # Category breakdown for the year
    transactions = get_transactions(user_id, start_date, end_date)
    income_by_category: Dict[str, float] = {}
    expenses_by_category: Dict[str, float] = {}
    
    for transaction in transactions:
        category = transaction['category']
        amount = transaction['amount']
        
        if transaction['type'] == 'income':
            income_by_category[category] = income_by_category.get(category, 0) + amount
        else:
            expenses_by_category[category] = expenses_by_category.get(category, 0) + amount
    
    return {
        'year': year,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'total_savings': total_savings,
        'monthly_reports': monthly_reports,
        'income_by_category': income_by_category,
        'expenses_by_category': expenses_by_category,
        'transaction_count': len(transactions)
    }


def format_monthly_report(report: Dict) -> str:
    """
    Format a monthly report as a readable string.
    
    Args:
        report: Report dictionary from generate_monthly_report
    
    Returns:
        Formatted report string
    """
    month_names = [
        '', 'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    
    month_name = month_names[report['month']]
    year = report['year']
    
    lines = [
        f"\n{'='*60}",
        f"MONTHLY FINANCIAL REPORT - {month_name.upper()} {year}",
        f"{'='*60}",
        "",
        f"Total Income:      ${report['total_income']:,.2f}",
        f"Total Expenses:    ${report['total_expenses']:,.2f}",
        f"Savings:           ${report['savings']:,.2f}",
        f"Transaction Count: {report['transaction_count']}",
        "",
    ]
    
    if report['income_by_category']:
        lines.append("INCOME BY CATEGORY:")
        lines.append("-" * 60)
        for category, amount in sorted(report['income_by_category'].items(), key=lambda x: x[1], reverse=True):
            lines.append(f"  {category:20s} ${amount:>12,.2f}")
        lines.append("")
    
    if report['expenses_by_category']:
        lines.append("EXPENSES BY CATEGORY:")
        lines.append("-" * 60)
        for category, amount in sorted(report['expenses_by_category'].items(), key=lambda x: x[1], reverse=True):
            lines.append(f"  {category:20s} ${amount:>12,.2f}")
        lines.append("")
    
    lines.append("=" * 60)
    
    return "\n".join(lines)


def format_yearly_report(report: Dict) -> str:
    """
    Format a yearly report as a readable string.
    
    Args:
        report: Report dictionary from generate_yearly_report
    
    Returns:
        Formatted report string
    """
    year = report['year']
    
    lines = [
        f"\n{'='*60}",
        f"YEARLY FINANCIAL REPORT - {year}",
        f"{'='*60}",
        "",
        f"Total Income:      ${report['total_income']:,.2f}",
        f"Total Expenses:    ${report['total_expenses']:,.2f}",
        f"Total Savings:     ${report['total_savings']:,.2f}",
        f"Transaction Count: {report['transaction_count']}",
        "",
        "MONTHLY BREAKDOWN:",
        "-" * 60,
        f"{'Month':<15s} {'Income':>15s} {'Expenses':>15s} {'Savings':>15s}",
        "-" * 60,
    ]
    
    month_names = [
        '', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
    ]
    
    for monthly_report in report['monthly_reports']:
        month_name = month_names[monthly_report['month']]
        income = monthly_report['total_income']
        expenses = monthly_report['total_expenses']
        savings = monthly_report['savings']
        lines.append(
            f"{month_name:<15s} ${income:>14,.2f} ${expenses:>14,.2f} ${savings:>14,.2f}"
        )
    
    lines.append("")
    
    if report['income_by_category']:
        lines.append("INCOME BY CATEGORY (YEAR):")
        lines.append("-" * 60)
        for category, amount in sorted(report['income_by_category'].items(), key=lambda x: x[1], reverse=True):
            lines.append(f"  {category:20s} ${amount:>12,.2f}")
        lines.append("")
    
    if report['expenses_by_category']:
        lines.append("EXPENSES BY CATEGORY (YEAR):")
        lines.append("-" * 60)
        for category, amount in sorted(report['expenses_by_category'].items(), key=lambda x: x[1], reverse=True):
            lines.append(f"  {category:20s} ${amount:>12,.2f}")
        lines.append("")
    
    lines.append("=" * 60)
    
    return "\n".join(lines)

