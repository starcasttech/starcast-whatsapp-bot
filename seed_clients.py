"""
Seed the clients table from the Starcast ISP Address Book.
Run once (or re-run to refresh data — uses INSERT OR REPLACE).
Usage:  python3 seed_clients.py
"""
import sqlite3
from datetime import datetime

import os as _os
DB_PATH = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "starcast.db")

# ID number extracted from Payment Ref (first 13 digits).
# Where ref is non-numeric (Simpson, Ockhuis, Enrico) no ID — leave blank so
# those clients can't use self-service yet (Leonard must add their ID manually).
CLIENTS = [
    # phone,             id_number,          name,                        email,                              package_amt
    ("+27632693699",  "8003220150086", "Semone Jansen",          "semonejansen92@gmail.com",          "R525"),
    ("+27733137471",  "9206200095085", "Patricia Witbooi",       "patricia.witbooi30@gmail.com",      "R525"),
    ("+27634235549",  "7109290010083", "Jennifer Van Coller",    "roneys@wispernet.co.za",            "R525"),
    ("+27711593211",  "9511225239083", "Robert Khumalo",         "boeboekhumalo26@gmail.com",         "R525"),
    ("+27671364187",  "9801195168085", "Rick Van Niekerk",       "rickgodwinvanniekerk214@gmail.com", "R525"),
    ("+27835937542",  "9009020031086", "Melany Arries",          "melanylottering@yahoo.com",         "R525"),
    ("+27638671556",  "9601200107080", "Raylene Jonck",          "apptv109@gmail.com",                "R525"),
    ("+27626767939",  "8612115132080", "Earl David Veldman",     "earl.velman@gmail.com",             "R525"),
    ("+27611632525",  "8703135185081", "Lincoln Lottering",      "lincolnlottering87@gmail.com",      "R350"),
    ("+27613007423",  "9409020218081", "Shanadia Matolla",       "Shanadiajonck3@gmail.com",          "R525"),
    ("+27722297791",  "8612230030086", "Sheree Raubenheimer",    "sheree.raubenheimer86@gmail.com",   "R525"),
    ("+27747959408",  "8801045033084", "Danzel Jerome Koeries",  "danzelkoeries1@gmail.com",          "R525"),
    ("+27742588890",  "7410255131082", "Vernon Meyer",           "vernon2meyer@gmail.com",            "R525"),
    # Keanu Jonck — no phone/email on file; skipped
    ("+27817047153",  "Simpson122025", "Llewellyn Simpson",      "simpson737@hotmail.com",            "R1,350"),
    ("+27829213451",  "6408175162089", "David Meyer",            "brado.meyer@gmail.com",             "R785"),
    ("+27661587323",  "6409170609082", "Kristien Willemse",      "ethanwillemse16@gmail.com",         "R640"),
    ("+27692264213",  "8608050083080", "Adri Stoffels",          "adricandice86@gmail.com",           "R640"),
    ("+27834621182",  "6306215184082", "Gerald de Jager",        "dejagergerald9@gmail.com",          "R499"),
    ("+27722900330",  "Ockhuis319",    "Jerome Ockhuis",         "jockhuis@yahoo.com",                "R640"),
    ("+27713841638",  "6908175220084", "Irvin Esau",             "iresau7395@gmail.com",              "R0"),
    ("+27794937698",  "6511065908089", "Berty De Laan",          "bertydelaan@gmail.com",             "R499"),
    # Enrico Gertse — no phone on file; skipped
    ("+27679889241",  "6801275213085", "Arthur Frederick Pekeur","arthurpekeur@gmail.com",            "R799"),
    ("+27834409624",  "8702155132080", "Leonard Roelofse",       "leonard508@outlook.com",            "R1,572"),
]

def seed():
    conn = sqlite3.connect(DB_PATH)
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
    now = datetime.utcnow().isoformat()
    for phone, id_number, name, email, pkg in CLIENTS:
        conn.execute("""
            INSERT INTO clients (phone, id_number, name, email, package_amt, paid, updated_at)
            VALUES (?, ?, ?, ?, ?, 0, ?)
            ON CONFLICT(phone) DO UPDATE SET
                id_number   = excluded.id_number,
                name        = excluded.name,
                email       = excluded.email,
                package_amt = excluded.package_amt,
                updated_at  = excluded.updated_at
        """, (phone, id_number, name, email, pkg, now))
    conn.commit()
    print(f"Seeded {len(CLIENTS)} clients.")
    # Show summary
    rows = conn.execute("SELECT phone, name, package_amt FROM clients ORDER BY name").fetchall()
    for r in rows:
        print(f"  {r[0]:16s}  {r[1]:30s}  {r[2]}")
    conn.close()

if __name__ == "__main__":
    seed()
