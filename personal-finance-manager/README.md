# Personal Finance Management Application

A comprehensive command-line application for managing personal finances, tracking income and expenses, generating financial reports, and managing budgets.

## Features

### 1. User Registration and Authentication
- Secure user registration with unique usernames
- Password hashing using SHA-256 with salt
- User login and session management
- Secure authentication system

### 2. Income and Expense Tracking
- Add, update, and delete income and expense entries
- Categorize transactions (Food, Rent, Salary, etc.)
- Support for multiple predefined categories
- Date-based transaction tracking
- Transaction descriptions

### 3. Financial Reports
- Generate monthly financial reports with:
  - Total income and expenses
  - Savings calculation
  - Category-wise breakdown
  - Transaction count
- Generate yearly financial reports with:
  - Annual totals
  - Monthly breakdown
  - Category-wise analysis

### 4. Budgeting
- Set monthly budgets for different expense categories
- Track spending against budget limits
- Budget status monitoring
- Automatic alerts when budgets are exceeded
- Visual indicators for budget status

### 5. Data Persistence
- SQLite database for reliable data storage
- Automatic database initialization
- Data backup functionality with timestamped backups
- Database restore capability
- Transaction integrity and data validation

### 6. User-Friendly Interface
- Color-coded command-line interface
- Intuitive menu system
- Clear error messages
- Input validation
- Helpful prompts and guidance

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Steps

1. **Clone or download the project**
   ```bash
   cd innobyte
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

   Or install manually:
   ```bash
   pip install colorama pytest pytest-cov
   ```

3. **Initialize the database** (optional - done automatically on first run)
   ```bash
   python -m src.database
   ```

## Usage

### Starting the Application

Run the main application:
```bash
python -m src.cli
```

Or if installed as a package:
```bash
finance-manager
```

### First Time Setup

1. **Register a new user**
   - Select option `1` from the main menu
   - Enter a unique username
   - Enter a password (minimum 4 characters)

2. **Login**
   - Select option `2` from the main menu
   - Enter your username and password

### Main Menu Options (After Login)

1. **Add Transaction** - Record income or expense
2. **View Transactions** - Display recent transactions
3. **Update Transaction** - Modify existing transactions
4. **Delete Transaction** - Remove transactions
5. **View Monthly Report** - Generate monthly financial summary
6. **View Yearly Report** - Generate yearly financial summary
7. **Set Budget** - Define monthly spending limits
8. **View Budget Status** - Check budget progress and alerts
9. **Backup Database** - Create a backup of your data
10. **Restore Database** - Restore from a backup
11. **Logout** - Sign out of your account
12. **Exit** - Close the application

### Adding Transactions

1. Select "Add Transaction" from the main menu
2. Choose transaction type (Income or Expense)
3. Select a category from the list
4. Enter the amount
5. Optionally add a description
6. Enter the date (or press Enter for today)

**Available Categories:**

**Income Categories:**
- Salary
- Freelance
- Investment
- Bonus
- Other Income

**Expense Categories:**
- Food
- Rent
- Utilities
- Transportation
- Entertainment
- Healthcare
- Education
- Shopping
- Bills
- Other Expense

### Generating Reports

**Monthly Report:**
1. Select "View Monthly Report"
2. Enter the year (default: current year)
3. Enter the month (1-12, default: current month)
4. View the detailed report with income, expenses, savings, and category breakdown

**Yearly Report:**
1. Select "View Yearly Report"
2. Enter the year (default: current year)
3. View the comprehensive yearly summary with monthly breakdown

### Managing Budgets

**Setting a Budget:**
1. Select "Set Budget"
2. Choose an expense category
3. Enter the year and month
4. Enter the monthly spending limit

**Checking Budget Status:**
1. Select "View Budget Status"
2. Enter the year and month
3. View spending vs. budget limits
4. See alerts for exceeded budgets

### Backup and Restore

**Creating a Backup:**
1. Select "Backup Database"
2. A timestamped backup file will be created in the `data/backups/` directory

**Restoring from Backup:**
1. Select "Restore Database"
2. Choose from available backups or enter a backup file path
3. Confirm the restore operation
4. Your database will be restored from the backup

**Note:** The current database is automatically backed up before restoration.

## Project Structure

```
innobyte/
├── src/
│   ├── __init__.py
│   ├── database.py          # Database initialization and connection
│   ├── models.py            # Data models and categories
│   ├── auth.py              # User authentication
│   ├── transactions.py      # Transaction management
│   ├── reports.py           # Financial report generation
│   ├── budget.py            # Budget management
│   ├── backup.py            # Backup and restore
│   └── cli.py               # Main command-line interface
├── tests/
│   ├── __init__.py
│   ├── test_auth.py         # Authentication tests
│   ├── test_transactions.py # Transaction tests
│   ├── test_reports.py      # Report tests
│   ├── test_budget.py       # Budget tests
│   └── test_backup.py       # Backup tests
├── data/
│   ├── finance.db           # SQLite database (created automatically)
│   └── backups/             # Backup files directory
├── requirements.txt         # Python dependencies
├── setup.py                # Package setup
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## Testing

Run the test suite:
```bash
pytest tests/
```

Run tests with coverage:
```bash
pytest tests/ --cov=src --cov-report=html
```

Run specific test file:
```bash
pytest tests/test_auth.py
```

## Database Schema

### Users Table
- `id` - Primary key
- `username` - Unique username
- `password_hash` - Hashed password with salt
- `created_at` - Account creation timestamp

### Transactions Table
- `id` - Primary key
- `user_id` - Foreign key to users
- `type` - 'income' or 'expense'
- `category` - Transaction category
- `amount` - Transaction amount
- `description` - Optional description
- `date` - Transaction date
- `created_at` - Record creation timestamp

### Budgets Table
- `id` - Primary key
- `user_id` - Foreign key to users
- `category` - Budget category
- `monthly_limit` - Monthly spending limit
- `month` - Month (1-12)
- `year` - Year
- `created_at` - Record creation timestamp

## Security Features

- **Password Hashing**: Passwords are hashed using SHA-256 with unique salts
- **SQL Injection Prevention**: All database queries use parameterized statements
- **User Isolation**: Users can only access their own data
- **Input Validation**: All user inputs are validated before processing

## Error Handling

The application includes comprehensive error handling for:
- Invalid user input
- Database connection errors
- File I/O errors (backup/restore)
- Authentication failures
- Transaction validation errors

## Troubleshooting

### Database Issues
- If you encounter database errors, try deleting `data/finance.db` and restarting the application
- Ensure the `data/` directory has write permissions

### Import Errors
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Run from the project root directory

### Backup/Restore Issues
- Ensure backup files are valid SQLite databases
- Check file permissions for the backup directory
- Verify backup file paths are correct

## Development

### Adding New Categories
Edit `src/models.py` and add categories to `INCOME_CATEGORIES` or `EXPENSE_CATEGORIES` lists.

### Extending Functionality
- All modules are well-documented and follow clean code principles
- Database schema can be extended by modifying `src/database.py`
- New features can be added as separate modules following the existing pattern

## License

This project is provided as-is for educational and personal use.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the code documentation
3. Run the test suite to verify functionality

## Version History

- **v1.0.0** - Initial release with all core features

---

**Note:** This application stores financial data locally. Always maintain regular backups of your database file.

