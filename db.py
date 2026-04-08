import sqlite3
import json
from datetime import datetime

import os as _os
DB_PATH = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "starcast.db")

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
        conn.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                phone       TEXT PRIMARY KEY,
                id_number   TEXT NOT NULL,
                name        TEXT NOT NULL,
                email       TEXT NOT NULL DEFAULT '',
                package_amt TEXT NOT NULL DEFAULT 'R0',
                paid        INTEGER NOT NULL DEFAULT 0,
                updated_at  TEXT NOT NULL
            )
        """)
        conn.commit()

# ── Session helpers ────────────────────────────────────────────────────────

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

# ── Client account helpers ─────────────────────────────────────────────────

def _clean_phone(phone):
    """Normalise phone: strip whatsapp: prefix and fix space-for-plus encoding."""
    p = phone.replace("whatsapp:", "").strip()
    if p.startswith(" "):          # URL-decoded '+' becomes ' '
        p = "+" + p[1:]
    return p

def _row_to_client(row):
    if not row:
        return None
    return {
        "phone":        row[0],
        "id_number":    row[1],
        "name":         row[2],
        "email":        row[3],
        "package_amt":  row[4],
        "paid":         bool(row[5]),
        "vip":          bool(row[6]),
        "services":     json.loads(row[7]) if row[7] else [],
        "paid_period":  row[8] or "",
    }

def get_client_by_phone(phone):
    """Look up a client by their WhatsApp phone number."""
    phone = _clean_phone(phone)
    with get_conn() as conn:
        row = conn.execute(
            "SELECT phone,id_number,name,email,package_amt,paid,vip,services_json,paid_period "
            "FROM clients WHERE phone = ?", (phone,)
        ).fetchone()
    return _row_to_client(row)

def get_client_by_id(id_number):
    """Look up a client by ID number alone."""
    with get_conn() as conn:
        row = conn.execute(
            "SELECT phone,id_number,name,email,package_amt,paid,vip,services_json,paid_period "
            "FROM clients WHERE id_number = ?", (id_number.strip(),)
        ).fetchone()
    return _row_to_client(row)

def verify_client(phone, id_number):
    """Return client dict if phone+ID match, else None."""
    phone = _clean_phone(phone)
    client = get_client_by_phone(phone)
    if client and client["id_number"] == id_number.strip():
        return client
    return None

def update_client_phone(old_phone, new_phone):
    """Update a client's phone number (primary key — careful)."""
    old_phone = _clean_phone(old_phone)
    # Normalise new number: convert 08x → +278x
    new_phone = new_phone.strip().replace(" ", "")
    if new_phone.startswith("0"):
        new_phone = "+27" + new_phone[1:]
    with get_conn() as conn:
        conn.execute(
            "UPDATE clients SET phone=?, updated_at=? WHERE phone=?",
            (new_phone, datetime.utcnow().isoformat(), old_phone)
        )
        conn.commit()
    return new_phone

def update_client_details(phone, name=None, email=None):
    """Update client name and/or email."""
    phone = _clean_phone(phone)
    fields, values = [], []
    if name:
        fields.append("name = ?")
        values.append(name)
    if email:
        fields.append("email = ?")
        values.append(email)
    if not fields:
        return
    fields.append("updated_at = ?")
    values.append(datetime.utcnow().isoformat())
    values.append(phone)
    with get_conn() as conn:
        conn.execute(f"UPDATE clients SET {', '.join(fields)} WHERE phone = ?", values)
        conn.commit()

def set_client_paid(phone, paid: bool):
    with get_conn() as conn:
        conn.execute(
            "UPDATE clients SET paid = ?, updated_at = ? WHERE phone = ?",
            (1 if paid else 0, datetime.utcnow().isoformat(), phone)
        )
        conn.commit()
