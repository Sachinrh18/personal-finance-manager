"""
Main command-line interface for the Personal Finance Management Application.
"""

import sys
from datetime import date, datetime
from typing import Optional, List
from colorama import init, Fore, Style

from src.database import init_database
from src.auth import (
    register_user, login_user, logout_user, 
    get_current_user_id, is_authenticated
)
from src.transactions import (
    add_transaction, update_transaction, delete_transaction,
    get_transactions, get_transaction_by_id
)
from src.reports import (
    generate_monthly_report, generate_yearly_report,
    format_monthly_report, format_yearly_report
)
from src.budget import (
    set_budget, get_all_budgets, check_budget_status,
    get_budget_alerts, format_budget_status, format_budget_alerts
)
from src.backup import backup_database, restore_database, list_backups
from src.models import INCOME_CATEGORIES, EXPENSE_CATEGORIES, ALL_CATEGORIES

# Initialize colorama for Windows
init(autoreset=True)


def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}{text.center(70)}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")


def print_success(message: str):
    """Print a success message."""
    print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")


def print_error(message: str):
    """Print an error message."""
    print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")


def print_warning(message: str):
    """Print a warning message."""
    print(f"{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}")


def print_info(message: str):
    """Print an info message."""
    print(f"{Fore.BLUE}ℹ {message}{Style.RESET_ALL}")


def get_input(prompt: str, default: str = None) -> str:
    """Get user input with optional default value."""
    if default:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "
    
    value = input(prompt).strip()
    return value if value else default or ""


def get_float_input(prompt: str) -> Optional[float]:
    """Get a float input from user."""
    while True:
        try:
            value = input(f"{prompt}: ").strip()
            if not value:
                return None
            return float(value)
        except ValueError:
            print_error("Invalid input. Please enter a valid number.")


def get_int_input(prompt: str) -> Optional[int]:
    """Get an integer input from user."""
    while True:
        try:
            value = input(f"{prompt}: ").strip()
            if not value:
                return None
            return int(value)
        except ValueError:
            print_error("Invalid input. Please enter a valid integer.")


def get_date_input(prompt: str, default: date = None) -> Optional[date]:
    """Get a date input from user."""
    while True:
        if default:
            date_str = input(f"{prompt} [YYYY-MM-DD, default: {default}]: ").strip()
        else:
            date_str = input(f"{prompt} [YYYY-MM-DD]: ").strip()
        
        if not date_str and default:
            return default
        
        if not date_str:
            return None
        
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            print_error("Invalid date format. Please use YYYY-MM-DD.")


def select_category(categories: List[str], prompt: str = "Select category") -> Optional[str]:
    """Display categories and get user selection."""
    print(f"\n{prompt}:")
    for i, category in enumerate(categories, 1):
        print(f"  {i}. {category}")
    
    while True:
        try:
            choice = get_int_input(f"\nEnter choice (1-{len(categories)})")
            if choice and 1 <= choice <= len(categories):
                return categories[choice - 1]
            elif choice is None:
                return None
            else:
                print_error(f"Please enter a number between 1 and {len(categories)}")
        except ValueError:
            print_error("Invalid input. Please enter a number.")


def register_menu():
    """Handle user registration."""
    print_header("USER REGISTRATION")
    
    username = get_input("Enter username")
    if not username:
        print_error("Username cannot be empty.")
        return
    
    password = get_input("Enter password (min 4 characters)")
    if not password:
        print_error("Password cannot be empty.")
        return
    
    success, message = register_user(username, password)
    if success:
        print_success(message)
    else:
        print_error(message)


def login_menu():
    """Handle user login."""
    print_header("USER LOGIN")
    
    username = get_input("Enter username")
    password = get_input("Enter password")
    
    success, message, user_id = login_user(username, password)
    if success:
        print_success(message)
        return True
    else:
        print_error(message)
        return False


def add_transaction_menu():
    """Menu for adding a transaction."""
    user_id = get_current_user_id()
    if not user_id:
        print_error("Please login first.")
        return
    
    print_header("ADD TRANSACTION")
    
    # Select transaction type
    print("Transaction Type:")
    print("  1. Income")
    print("  2. Expense")
    
    type_choice = get_int_input("Select type (1-2)")
    if type_choice not in [1, 2]:
        print_error("Invalid choice.")
        return
    
    transaction_type = "income" if type_choice == 1 else "expense"
    
    # Select category
    categories = INCOME_CATEGORIES if transaction_type == "income" else EXPENSE_CATEGORIES
    category = select_category(categories, "Select category")
    if not category:
        print_error("Category selection cancelled.")
        return
    
    # Get amount
    amount = get_float_input("Enter amount")
    if amount is None or amount <= 0:
        print_error("Amount must be greater than 0.")
        return
    
    # Get description
    description = get_input("Enter description (optional)", "")
    
    # Get date
    transaction_date = get_date_input("Enter date", date.today())
    if not transaction_date:
        transaction_date = date.today()
    
    success, message, _ = add_transaction(
        user_id, transaction_type, category, amount, description, transaction_date
    )
    
    if success:
        print_success(message)
    else:
        print_error(message)


def view_transactions_menu():
    """Menu for viewing transactions."""
    user_id = get_current_user_id()
    if not user_id:
        print_error("Please login first.")
        return
    
    print_header("VIEW TRANSACTIONS")
    
    transactions = get_transactions(user_id, limit=50)
    
    if not transactions:
        print_info("No transactions found.")
        return
    
    print(f"\n{'ID':<6} {'Date':<12} {'Type':<10} {'Category':<20} {'Amount':>15} {'Description':<20}")
    print("-" * 100)
    
    for t in transactions:
        trans_date = datetime.strptime(t['date'], "%Y-%m-%d").date() if isinstance(t['date'], str) else t['date']
        amount_str = f"${t['amount']:,.2f}"
        type_str = t['type'].upper()
        desc = (t['description'] or "")[:20]
        
        print(f"{t['id']:<6} {str(trans_date):<12} {type_str:<10} {t['category']:<20} {amount_str:>15} {desc:<20}")


def update_transaction_menu():
    """Menu for updating a transaction."""
    user_id = get_current_user_id()
    if not user_id:
        print_error("Please login first.")
        return
    
    print_header("UPDATE TRANSACTION")
    
    transaction_id = get_int_input("Enter transaction ID to update")
    if not transaction_id:
        print_error("Transaction ID is required.")
        return
    
    transaction = get_transaction_by_id(transaction_id, user_id)
    if not transaction:
        print_error("Transaction not found.")
        return
    
    print(f"\nCurrent transaction details:")
    print(f"  Type: {transaction['type']}")
    print(f"  Category: {transaction['category']}")
    print(f"  Amount: ${transaction['amount']:,.2f}")
    print(f"  Description: {transaction['description']}")
    print(f"  Date: {transaction['date']}")
    
    print("\nEnter new values (press Enter to keep current value):")
    
    updates = {}
    
    # Update type
    print("\nTransaction Type:")
    print("  1. Income")
    print("  2. Expense")
    print("  3. Keep current")
    type_choice = get_int_input("Select type (1-3)")
    if type_choice in [1, 2]:
        updates['type'] = "income" if type_choice == 1 else "expense"
    
    # Update category
    if 'type' in updates:
        categories = INCOME_CATEGORIES if updates['type'] == "income" else EXPENSE_CATEGORIES
    else:
        categories = INCOME_CATEGORIES if transaction['type'] == "income" else EXPENSE_CATEGORIES
    
    print(f"\nCategory (current: {transaction['category']}):")
    category = select_category(categories, "Select new category (or cancel to keep current)")
    if category:
        updates['category'] = category
    
    # Update amount
    amount = get_float_input(f"Amount (current: ${transaction['amount']:,.2f})")
    if amount and amount > 0:
        updates['amount'] = amount
    
    # Update description
    description = get_input(f"Description (current: {transaction['description'] or 'None'})")
    if description:
        updates['description'] = description
    
    # Update date
    current_date = datetime.strptime(transaction['date'], "%Y-%m-%d").date() if isinstance(transaction['date'], str) else transaction['date']
    new_date = get_date_input(f"Date (current: {current_date})", current_date)
    if new_date and new_date != current_date:
        updates['date'] = new_date
    
    if not updates:
        print_info("No changes made.")
        return
    
    success, message = update_transaction(transaction_id, user_id, **updates)
    if success:
        print_success(message)
    else:
        print_error(message)


def delete_transaction_menu():
    """Menu for deleting a transaction."""
    user_id = get_current_user_id()
    if not user_id:
        print_error("Please login first.")
        return
    
    print_header("DELETE TRANSACTION")
    
    transaction_id = get_int_input("Enter transaction ID to delete")
    if not transaction_id:
        print_error("Transaction ID is required.")
        return
    
    transaction = get_transaction_by_id(transaction_id, user_id)
    if not transaction:
        print_error("Transaction not found.")
        return
    
    print(f"\nTransaction details:")
    print(f"  Type: {transaction['type']}")
    print(f"  Category: {transaction['category']}")
    print(f"  Amount: ${transaction['amount']:,.2f}")
    print(f"  Date: {transaction['date']}")
    
    confirm = get_input("Are you sure you want to delete this transaction? (yes/no)", "no")
    if confirm.lower() != "yes":
        print_info("Deletion cancelled.")
        return
    
    success, message = delete_transaction(transaction_id, user_id)
    if success:
        print_success(message)
    else:
        print_error(message)


def view_monthly_report_menu():
    """Menu for viewing monthly report."""
    user_id = get_current_user_id()
    if not user_id:
        print_error("Please login first.")
        return
    
    print_header("MONTHLY FINANCIAL REPORT")
    
    year = get_int_input("Enter year")
    if not year:
        year = date.today().year
    
    month = get_int_input("Enter month (1-12)")
    if not month or not (1 <= month <= 12):
        month = date.today().month
    
    report = generate_monthly_report(user_id, month, year)
    print(format_monthly_report(report))


def view_yearly_report_menu():
    """Menu for viewing yearly report."""
    user_id = get_current_user_id()
    if not user_id:
        print_error("Please login first.")
        return
    
    print_header("YEARLY FINANCIAL REPORT")
    
    year = get_int_input("Enter year")
    if not year:
        year = date.today().year
    
    report = generate_yearly_report(user_id, year)
    print(format_yearly_report(report))


def set_budget_menu():
    """Menu for setting a budget."""
    user_id = get_current_user_id()
    if not user_id:
        print_error("Please login first.")
        return
    
    print_header("SET BUDGET")
    
    category = select_category(EXPENSE_CATEGORIES, "Select expense category for budget")
    if not category:
        print_error("Category selection cancelled.")
        return
    
    year = get_int_input("Enter year")
    if not year:
        year = date.today().year
    
    month = get_int_input("Enter month (1-12)")
    if not month or not (1 <= month <= 12):
        month = date.today().month
    
    limit = get_float_input("Enter monthly budget limit")
    if not limit or limit <= 0:
        print_error("Budget limit must be greater than 0.")
        return
    
    success, message = set_budget(user_id, category, limit, month, year)
    if success:
        print_success(message)
    else:
        print_error(message)


def view_budget_status_menu():
    """Menu for viewing budget status."""
    user_id = get_current_user_id()
    if not user_id:
        print_error("Please login first.")
        return
    
    print_header("BUDGET STATUS")
    
    year = get_int_input("Enter year")
    if not year:
        year = date.today().year
    
    month = get_int_input("Enter month (1-12)")
    if not month or not (1 <= month <= 12):
        month = date.today().month
    
    status = check_budget_status(user_id, month, year)
    print(format_budget_status(status))
    
    # Show alerts
    alerts = get_budget_alerts(user_id, month, year)
    if alerts:
        print(format_budget_alerts(alerts))


def backup_menu():
    """Menu for backing up database."""
    print_header("BACKUP DATABASE")
    
    success, message = backup_database()
    if success:
        print_success(message)
    else:
        print_error(message)


def restore_menu():
    """Menu for restoring database."""
    print_header("RESTORE DATABASE")
    
    backups = list_backups()
    if backups:
        print("Available backups:")
        for i, backup in enumerate(backups, 1):
            print(f"  {i}. {backup}")
        
        choice = get_int_input("\nSelect backup number")
        if choice and 1 <= choice <= len(backups):
            backup_path = backups[choice - 1]
        else:
            backup_path = get_input("Enter backup file path")
    else:
        backup_path = get_input("Enter backup file path")
    
    if not backup_path:
        print_error("Backup path is required.")
        return
    
    print_warning("This will replace your current database. Make sure you have a backup!")
    confirm = get_input("Are you sure? (yes/no)", "no")
    if confirm.lower() != "yes":
        print_info("Restore cancelled.")
        return
    
    success, message = restore_database(backup_path)
    if success:
        print_success(message)
    else:
        print_error(message)


def main_menu():
    """Display main menu and handle user choices."""
    while True:
        print_header("PERSONAL FINANCE MANAGER - MAIN MENU")
        
        if is_authenticated():
            user_id = get_current_user_id()
            print_info(f"Logged in as user ID: {user_id}")
            print("\nOptions:")
            print("  1. Add Transaction")
            print("  2. View Transactions")
            print("  3. Update Transaction")
            print("  4. Delete Transaction")
            print("  5. View Monthly Report")
            print("  6. View Yearly Report")
            print("  7. Set Budget")
            print("  8. View Budget Status")
            print("  9. Backup Database")
            print("  10. Restore Database")
            print("  11. Logout")
            print("  12. Exit")
        else:
            print("\nOptions:")
            print("  1. Register")
            print("  2. Login")
            print("  3. Exit")
        
        choice = get_int_input("\nSelect an option")
        
        if not is_authenticated():
            if choice == 1:
                register_menu()
            elif choice == 2:
                if login_menu():
                    continue
            elif choice == 3:
                print_info("Thank you for using Personal Finance Manager!")
                sys.exit(0)
            else:
                print_error("Invalid choice. Please try again.")
        else:
            if choice == 1:
                add_transaction_menu()
            elif choice == 2:
                view_transactions_menu()
            elif choice == 3:
                update_transaction_menu()
            elif choice == 4:
                delete_transaction_menu()
            elif choice == 5:
                view_monthly_report_menu()
            elif choice == 6:
                view_yearly_report_menu()
            elif choice == 7:
                set_budget_menu()
            elif choice == 8:
                view_budget_status_menu()
            elif choice == 9:
                backup_menu()
            elif choice == 10:
                restore_menu()
            elif choice == 11:
                logout_user()
                print_success("Logged out successfully.")
            elif choice == 12:
                print_info("Thank you for using Personal Finance Manager!")
                sys.exit(0)
            else:
                print_error("Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")


def main():
    """Main entry point for the application."""
    try:
        # Initialize database
        init_database()
        
        # Start main menu
        main_menu()
    
    except KeyboardInterrupt:
        print("\n\n" + Fore.YELLOW + "Application interrupted by user." + Style.RESET_ALL)
        sys.exit(0)
    except Exception as e:
        print_error(f"An unexpected error occurred: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

