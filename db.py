# db.py
import sqlite3
from datetime import datetime
from typing import List, Dict

DB_PATH = "chat_history.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        board TEXT,
        subject TEXT,
        started_at TEXT
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER,
        role TEXT,
        content TEXT,
        created_at TEXT,
        FOREIGN KEY(session_id) REFERENCES sessions(id)
    )""")
    conn.commit()
    conn.close()

def create_session(board: str, subject: str) -> int:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO sessions (board, subject, started_at) VALUES (?, ?, ?)",
                (board, subject, datetime.utcnow().isoformat()))
    sid = cur.lastrowid
    conn.commit()
    conn.close()
    return sid

def save_message(session_id: int, role: str, content: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO messages (session_id, role, content, created_at) VALUES (?, ?, ?, ?)",
                (session_id, role, content, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

def get_session_messages(session_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT role, content, created_at FROM messages WHERE session_id=? ORDER BY id", (session_id,))
    rows = cur.fetchall()
    conn.close()
    return [{"role": r[0], "content": r[1], "created_at": r[2]} for r in rows]
