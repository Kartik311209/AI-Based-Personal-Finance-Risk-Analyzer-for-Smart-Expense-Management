import sqlite3
import pandas as pd
import os

DB_PATH = "data/expenses.db"

def get_connection():
    os.makedirs("data", exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        date TEXT,
        category TEXT,
        amount REAL,
        note TEXT
    )
    """)

    conn.commit()
    conn.close()

def add_expense(username, date, category, amount, note=""):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO expenses (username, date, category, amount, note)
    VALUES (?, ?, ?, ?, ?)
    """, (username, date, category, amount, note))

    conn.commit()
    conn.close()

def load_expenses(username):
    conn = get_connection()
    df = pd.read_sql(
        "SELECT date, category, amount, note FROM expenses WHERE username = ?",
        conn,
        params=(username,)
    )
    conn.close()

    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
        df["amount"] = pd.to_numeric(df["amount"])

    return df
