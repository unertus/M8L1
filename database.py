import sqlite3
from config import DB_NAME

def init_db():
    """Создаёт таблицу заявок"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            message TEXT,
            department TEXT,
            status TEXT DEFAULT 'New',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_request(user_id, username, message, department):
    """Сохраняет заявку в базу"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO requests (user_id, username, message, department) VALUES (?, ?, ?, ?)",
        (user_id, username, message, department)
    )
    conn.commit()
    conn.close()