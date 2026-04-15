import hashlib
from database import get_connection

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password, email=None, phone=None):
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO users (username, password, role, email, phone) VALUES (?, ?, 'user', ?, ?)",
            (username, hash_password(password), email, phone)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Registration DB error: {e}")
        return False
    finally:
        conn.close()

def login_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Include email and phone in selection safely
        cursor.execute(
            "SELECT username, role, email, phone FROM users WHERE username=? AND password=?",
            (username, hash_password(password))
        )
        user = cursor.fetchone()
        
        if user:
            return {
                "username": user[0],
                "role": user[1],
                "email": user[2] if len(user) > 2 else None,
                "phone": user[3] if len(user) > 3 else None
            }
        return None
    except Exception as e:
        print(f"Login DB error: {e}")
        return None
    finally:
        conn.close()