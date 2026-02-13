import sqlite3

def get_conn():
    return sqlite3.connect("expenses.db")

def create_table():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        category TEXT,
        description TEXT,
        amount REAL
    )
    """)

    conn.commit()
    conn.close()

create_table()


def add_expense(date, category, description, amount):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO expenses (date, category, description, amount) VALUES (?, ?, ?, ?)",
        (date, category, description, amount)
    )
    conn.commit()
    conn.close()


def get_expenses():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT date, category, description, amount FROM expenses ORDER BY date DESC")
    rows = cur.fetchall()
    conn.close()
    return rows