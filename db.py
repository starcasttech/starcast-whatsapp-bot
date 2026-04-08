import sqlite3
import json
from datetime import datetime

DB_PATH = "starcast.db"

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                phone       TEXT PRIMARY KEY,
                state       TEXT NOT NULL DEFAULT 'IDLE',
                data_json   TEXT NOT NULL DEFAULT '{}',
                updated_at  TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS submissions (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                phone       TEXT NOT NULL,
                type        TEXT NOT NULL,
                data_json   TEXT NOT NULL,
                created_at  TEXT NOT NULL
            )
        """)
        conn.commit()

def get_session(phone):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT state, data_json FROM sessions WHERE phone = ?", (phone,)
        ).fetchone()
    if row:
        return row[0], json.loads(row[1])
    return "IDLE", {}

def set_session(phone, state, data):
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO sessions (phone, state, data_json, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(phone) DO UPDATE SET
                state = excluded.state,
                data_json = excluded.data_json,
                updated_at = excluded.updated_at
        """, (phone, state, json.dumps(data), datetime.utcnow().isoformat()))
        conn.commit()

def save_submission(phone, type_, data):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO submissions (phone, type, data_json, created_at) VALUES (?, ?, ?, ?)",
            (phone, type_, json.dumps(data), datetime.utcnow().isoformat())
        )
        conn.commit()

def get_all_submissions():
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, phone, type, data_json, created_at FROM submissions ORDER BY created_at DESC"
        ).fetchall()
    return [{"id": r[0], "phone": r[1], "type": r[2], "data": json.loads(r[3]), "created_at": r[4]} for r in rows]
