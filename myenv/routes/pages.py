from collections import defaultdict
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, current_user
from models import Expense
from flask import jsonify
from db import get_db_connection


pages_bp = Blueprint("pages", __name__)
CURRENCIES = ["INR", "USD", "EUR", "GBP", "JPY"]

# ---------- Home ----------
@pages_bp.route("/")
def home():
    return render_template("home.html")

# ---------- Sign Up ----------
@pages_bp.route("/thankyou")
def thankyou():
    return render_template("thankyou.html")
@pages_bp.route("/signup", methods=["GET", "POST"])

def signup():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        if not username or not password:
            flash("Username and password required", "danger")
            return redirect(url_for("pages.signup"))

        conn = get_db_connection(); cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id FROM users WHERE username=%s", (username,))
        if cur.fetchone():
            flash("Username already exists", "warning")
        else:
            cur.execute(
                "INSERT INTO users (username, password_hash) VALUES (%s,%s)",
                (username, generate_password_hash(password))
            )
            conn.commit()
            return redirect(url_for("pages.thankyou"))
        cur.close(); conn.close()

    return render_template("signup.html")

# ---------- Log In ----------
@pages_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        conn = get_db_connection(); cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id, password_hash FROM users WHERE username=%s", (username,))
        user = cur.fetchone(); cur.close(); conn.close()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["username"] = username
            return redirect(url_for("pages.dashboard"))
        flash("Invalid credentials", "danger")

    return render_template("login.html")

# ---------- Dashboard ----------
def login_required(fn):
    from functools import wraps
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first", "warning")
            return redirect(url_for("pages.login"))
        return fn(*args, **kwargs)
    return wrapper


@pages_bp.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    user_id = session["user_id"]

    # Handle new-expense form submit
    if request.method == "POST":
        desc  = request.form["description"]
        amt   = request.form["amount"]
        cat   = request.form["category"]
        curcy = request.form["currency"]


        conn = get_db_connection(); cur = conn.cursor()
        cur.execute(
            "INSERT INTO expenses (description, amount, currency, category, user_id) VALUES (%s,%s,%s,%s,%s)",
            (desc, amt, curcy, cat, user_id)
        )   

        conn.commit(); cur.close(); conn.close()
        flash("Expense added", "success")
        return redirect(url_for("pages.dashboard"))

    # Show current expenses
    conn = get_db_connection(); cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM expenses WHERE user_id=%s ORDER BY created_at DESC", (user_id,))
    expenses = cur.fetchall(); cur.close(); conn.close()

    return render_template("dashboard.html", expenses=expenses, username=session["username"], currencies=CURRENCIES)

@pages_bp.route("/expense/<int:expense_id>/edit", methods=["POST"])
@login_required
def edit_expense(expense_id):
    user_id = session["user_id"]
    desc  = request.form["description"]
    amt   = request.form["amount"]
    curcy = request.form["currency"]
    cat   = request.form["category"]

    conn = get_db_connection(); cur = conn.cursor()
    cur.execute(
        "UPDATE expenses SET description=%s, amount=%s, currency=%s, category=%s WHERE id=%s AND user_id=%s",
        (desc, amt, curcy, cat, expense_id, user_id)
    )
    conn.commit(); cur.close(); conn.close()

    flash("Expense updated", "success")
    return redirect(url_for("pages.dashboard"))

@pages_bp.route('/delete/<int:expense_id>', methods=['POST'])
def delete_expense(expense_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM expenses WHERE id = %s', (expense_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('pages.dashboard'))


@pages_bp.route("/analyze")
@login_required
def analyze():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT category, amount FROM expenses WHERE user_id = %s", (session["user_id"],))
    expenses = cur.fetchall()
    cur.close()
    conn.close()

    totals = {}
    for row in expenses:
        # Normalize category: capitalize first letter only (or use lower() if preferred)
        cat = row["category"].strip().title()
        amt = float(row["amount"])
        totals[cat] = totals.get(cat, 0) + amt

    sorted_totals = dict(sorted(totals.items(), key=lambda item: item[1], reverse=True))

    return render_template('analyze.html', category_totals=sorted_totals)

@pages_bp.route('/suggest')
def suggest():
    import pandas as pd
    from sqlalchemy import create_engine

    user_id = session.get('user_id')
    if not user_id:
        return render_template("suggest.html", suggestions=["Please log in to view suggestions."])

    try:
        engine = create_engine('mysql+pymysql://root:harinipanigrahi11@localhost/finance_tracker')

        conn = engine.raw_connection()
        try:
            df = pd.read_sql(
                "SELECT category, amount FROM expenses WHERE user_id = %s",
                con=conn,
                params=(user_id,)
            )
        finally:
            conn.close()

        if df.empty:
            return render_template("suggest.html", suggestions=["No expenses found to analyze."])

        df['category'] = df['category'].astype(str).str.strip().str.lower()
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        df.dropna(subset=['amount'], inplace=True)

        category_totals = df.groupby("category")["amount"].sum()

        suggestions = []
        essential_categories = {"emergency", "medicine", "transport", "food"}

        for category, total in category_totals.items():
            if category in essential_categories:
                if category == "food" and total > 10000:
                    suggestions.append(
                        f"₹{total:,.0f} on food is understandable. If you're eating out often, maybe plan simple meals at home occasionally to save."
                    )
                continue

            if total > 10000:
                suggestions.append(
                    f"You're spending ₹{total:,.0f} on '{category.title()}'. Consider redirecting ₹{int(total * 0.25):,} into a SIP or emergency fund."
                )
            elif total > 7000:
                suggestions.append(
                    f"₹{total:,.0f} spent on '{category.title()}' seems high. Try cutting down and investing ₹{int(total * 0.2):,} in mutual funds or RDs."
                )
            elif total > 4000:
                suggestions.append(
                    f"₹{total:,.0f} in '{category.title()}'. Think about allocating ₹{int(total * 0.15):,} to savings or low-risk options."
                )
            elif total > 2000:
                suggestions.append(
                    f"₹{total:,.0f} spent on '{category.title()}' — consider setting aside ₹{int(total * 0.1):,} for future needs."
                )

        if not suggestions:
            suggestions.append("Your spending looks balanced. Great job!")

        return render_template("suggest.html", suggestions=suggestions)

    except Exception as e:
        return render_template("suggest.html", suggestions=[f"Error: {str(e)}"])

# ---------- Log Out ----------
@pages_bp.route("/logout")
@login_required
def logout():
    session.clear()
    flash("Logged out", "info")
    return redirect(url_for("pages.home"))
