# ExpenseTracker
This is a simple and user-friendly web application that allows users to track their income and expenses. It helps individuals manage their personal finances by keeping a log of their transactions, calculating total income, total expenses, and current balance. The goal is to offer a clear and minimal way to understand spending habits and make better financial decisions.

Features
- User authentication
- Add expense entries with date, description, category, currency, and amount
- Auto-calculation of totals for each currency
- Accurate parsing of values including currency symbols (e.g., Rs., $)
- Clean tabular interface for visualizing expense data
- Generate and download a PDF report styled with headers, table rows, and bold totals using Helvetica font
- Handles multiple currencies gracefully and separates totals accordingly

## Technologies Used
- Python
- Flask API
- HTML5
- CSS3
- Vanilla JavaScript (ES6)
- [jsPDF](https://github.com/parallax/jsPDF) for PDF creation
- [jsPDF-AutoTable](https://github.com/simonbengtsson/jsPDF-AutoTable) for rendering tables in PDF

## File Structure :
ExpenseTracker
└── myenv
    ├── models
    │   ├── __pycache__/
    │   ├── __init__.py
    │   ├── expense.py
    │   └── user.py
    │
    ├── routes
    │   ├── __pycache__/
    │   ├── __init__.py
    │   ├── expenses.py
    │   ├── pages.py
    │   └── users.py
    │
    ├── Scripts/
    │
    ├── static
    │   ├── style.css
    │   └── styles.css
    │
    ├── templates
    │   ├── analyze.html
    │   ├── base.html
    │   ├── dashboard.html
    │   ├── home.html
    │   ├── login.html
    │   ├── signup.html
    │   ├── suggest.html
    │   └── thankyou.html
    │
    ├── utils
    │   ├── __pycache__/
    │   └── helpers.py
    │
    ├── app.py
    ├── db.py
    ├── pyvenv.cfg
    └── requirements.txt
