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
        role TEXT,
        email TEXT,
        phone TEXT
    )
    """)
    
    # Safely migrate existing table if needed
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")
    except sqlite3.OperationalError:
        pass
        
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN phone TEXT")
    except sqlite3.OperationalError:
        pass

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

    import dateutil.parser as dparser
    
    if not df.empty:
        def safe_parse(d):
            try:
                # Return standard python datetime natively to bypass Pandas entirely
                return pd.Timestamp(dparser.parse(str(d)))
            except:
                return pd.NaT
                
        df["date"] = df["date"].apply(safe_parse)
        df.dropna(subset=["date"], inplace=True)
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

    return df
