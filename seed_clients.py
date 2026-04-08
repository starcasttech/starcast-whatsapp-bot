"""
Seed / refresh the clients table from the Starcast ISP Address Book + Userlist.
Run:  python3 seed_clients.py
Safe to re-run — uses INSERT OR REPLACE (preserves paid status if --keep-paid flag set).
"""
import sqlite3, json, sys
import os as _os

DB_PATH = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "starcast.db")

KEEP_PAID = "--keep-paid" in sys.argv   # preserve existing paid/paid_period values

# ── Client data ────────────────────────────────────────────────────────────
# package_amt = what Starcast invoices the client (what they owe)
# services    = list of services on the account (name, provider, retail amount)
# vip         = True means R0 due regardless of services
# paid        = default for new records (overridden by --keep-paid for existing)

CLIENTS = [
    {
        "phone":       "+27632693699",
        "id_number":   "8003220150086",
        "name":        "Semone Jansen",
        "email":       "semonejansen92@gmail.com",
        "address":     "7510 Eve Crescent, Pacaltsdorp, George, 6534",
        "package_amt": "R525",
        "services":    [{"name": "Uncapped Octotel 25/25Mbps", "provider": "Octotel", "amount": 525}],
        "vip": False, "paid": False,
    },
    {
        "phone":       "+27733137471",
        "id_number":   "9206200095085",
        "name":        "Patricia Witbooi",
        "email":       "patricia.witbooi30@gmail.com",
        "address":     "23 Heather Road, Harmony Park, George, 6530",
        "package_amt": "R525",
        "services":    [{"name": "Uncapped Octotel 25/25Mbps", "provider": "Octotel", "amount": 525}],
        "vip": False, "paid": False,
    },
    {
        "phone":       "+27634235549",
        "id_number":   "7109290010083",
        "name":        "Jennifer Van Coller",
        "email":       "roneys@wispernet.co.za",
        "address":     "7 Truter St, Rossmore, George, 6529",
        "package_amt": "R525",
        "services":    [{"name": "Uncapped Octotel 25/25Mbps", "provider": "Octotel", "amount": 525}],
        "vip": False, "paid": False,
    },
    {
        "phone":       "+27711593211",
        "id_number":   "9511225239083",
        "name":        "Robert Khumalo",
        "email":       "boeboekhumalo26@gmail.com",
        "address":     "19 George Moore St, Rosemore, George, 6529",
        "package_amt": "R525",
        "services":    [{"name": "Uncapped Octotel 25/25Mbps", "provider": "Octotel", "amount": 525}],
        "vip": False, "paid": False,
    },
    {
        "phone":       "+27671364187",
        "id_number":   "9801195168085",
        "name":        "Rick Van Niekerk",
        "email":       "rickgodwinvanniekerk214@gmail.com",
        "address":     "3 Back Street, Pacaltsdorp, George, 6529",
        "package_amt": "R525",
        "services":    [{"name": "Uncapped Octotel 25/25Mbps", "provider": "Octotel", "amount": 525}],
        "vip": False, "paid": False,
    },
    {
        "phone":       "+27835937542",
        "id_number":   "9009020031086",
        "name":        "Melany Arries",
        "email":       "melanylottering@yahoo.com",
        "address":     "108 Beukes Street, Pacaltsdorp, George, 6534",
        "package_amt": "R525",
        "services":    [{"name": "Uncapped Octotel 25/25Mbps", "provider": "Octotel", "amount": 525}],
        "vip": False, "paid": False,
    },
    {
        "phone":       "+27638671556",
        "id_number":   "9601200107080",
        "name":        "Raylene Jonck",
        "email":       "apptv109@gmail.com",
        "address":     "7513 Eve Crescent, Rosedale, George, 6529",
        "package_amt": "R525",
        "services":    [{"name": "Uncapped Octotel 25/25Mbps", "provider": "Octotel", "amount": 525}],
        "vip": False, "paid": False,
    },
    {
        "phone":       "+27626767939",
        "id_number":   "8612115132080",
        "name":        "Earl David Veldman",
        "email":       "earl.velman@gmail.com",
        "address":     "14 Carnation St, Sea View, George, 6529",
        "package_amt": "R525",
        "services":    [{"name": "Uncapped Octotel 25/25Mbps", "provider": "Octotel", "amount": 525}],
        "vip": False, "paid": False,
    },
    {
        "phone":       "+27611632525",
        "id_number":   "8703135185081",
        "name":        "Lincoln Lottering",
        "email":       "lincolnlottering87@gmail.com",
        "address":     "9 Truter St, George, 6534",
        "package_amt": "R350",
        "services":    [{"name": "Uncapped Octotel 25/25Mbps", "provider": "Octotel", "amount": 350}],
        "vip": False, "paid": False,
    },
    {
        "phone":       "+27613007423",
        "id_number":   "9409020218081",
        "name":        "Shanadia Matolla",
        "email":       "Shanadiajonck3@gmail.com",
        "address":     "6314 Loerie Crescent, New Dawn Park, Pacaltsdorp, 6529",
        "package_amt": "R525",
        "services":    [{"name": "Uncapped Octotel 25/25Mbps", "provider": "Octotel", "amount": 525}],
        "vip": False, "paid": False,
    },
    {
        "phone":       "+27722297791",
        "id_number":   "8612230030086",
        "name":        "Sheree Raubenheimer",
        "email":       "sheree.raubenheimer86@gmail.com",
        "address":     "18 Acacia St, Pacaltsdorp, George, 6534",
        "package_amt": "R525",
        "services":    [{"name": "Uncapped Octotel 25/25Mbps", "provider": "Octotel", "amount": 525}],
        "vip": False, "paid": False,
    },
    {
        "phone":       "+27747959408",
        "id_number":   "8801045033084",
        "name":        "Danzel Jerome Koeries",
        "email":       "danzelkoeries1@gmail.com",
        "address":     "16 Schubert St, Pacaltsdorp, George, 6534",
        "package_amt": "R525",
        "services":    [{"name": "Uncapped Octotel 25/25Mbps", "provider": "Octotel", "amount": 525}],
        "vip": False, "paid": False,
    },
    {
        "phone":       "+27742588890",
        "id_number":   "7410255131082",
        "name":        "Vernon Meyer",
        "email":       "vernon2meyer@gmail.com",
        "address":     "12 Geelhout St, Pacaltsdorp, George, 6534",
        "package_amt": "R525",
        "services":    [{"name": "Uncapped Octotel 25/25Mbps", "provider": "Octotel", "amount": 525}],
        "vip": False, "paid": False,
    },
    # Keanu Jonck — no phone/ID on file; cannot use self-service
    {
        "phone":       "+27817047153",
        "id_number":   "8106085209085",  # from userlist
        "name":        "Llewellyn Simpson",
        "email":       "simpson737@hotmail.com",
        "address":     "68 Lang Street, De Bakke, Mossel Bay, 6506",
        "package_amt": "R0",
        "services":    [{"name": "Uncapped Frogfoot 1000/500Mbps", "provider": "Frogfoot", "amount": 1350}],
        "vip": True, "paid": True,
    },
    {
        "phone":       "+27829213451",
        "id_number":   "6408175162089",
        "name":        "David Meyer",
        "email":       "brado.meyer@gmail.com",
        "address":     "27 Markotter St, The Reeds, Centurion, 0058",
        "package_amt": "R785",
        "services":    [{"name": "Uncapped MetroFibre 75/75Mbps", "provider": "MetroFibre", "amount": 785}],
        "vip": False, "paid": False,
    },
    {
        "phone":       "+27661587323",
        "id_number":   "6409170609082",
        "name":        "Kristien Willemse",
        "email":       "ethanwillemse16@gmail.com",
        "address":     "7876 Noah St, Rosedale, Pacaltsdorp, 6529",
        "package_amt": "R640",
        "services":    [{"name": "Uncapped Octotel 55/25Mbps", "provider": "Octotel", "amount": 640}],
        "vip": False, "paid": False,
    },
    {
        "phone":       "+27814911200",
        "id_number":   "8608050083080",
        "name":        "Adri Stoffels",
        "email":       "adricandice86@gmail.com",
        "address":     "32 Agter Straat, Pacaltsdorp, George, 6534",
        "package_amt": "R0",
        "services":    [{"name": "Uncapped Octotel 55/25Mbps", "provider": "Octotel", "amount": 640}],
        "vip": True, "paid": True,
    },
    {
        "phone":       "+27834621182",
        "id_number":   "6306215184082",
        "name":        "Gerald de Jager",
        "email":       "dejagergerald9@gmail.com",
        "address":     "8 Hibiscus Avenue, Ext 6, Mossel Bay, 6500",
        "package_amt": "R499",
        "services":    [{"name": "Uncapped Openserve 30/30Mbps", "provider": "Openserve", "amount": 499}],
        "vip": False, "paid": False,
    },
    {
        "phone":       "+27722900330",
        "id_number":   "7409265082087",  # from userlist
        "name":        "Jerome Ockhuis",
        "email":       "jockhuis@yahoo.com",
        "address":     "31 Robbe St, De Bakke, Mossel Bay, 6500",
        "package_amt": "R0",
        "services":    [{"name": "Uncapped Openserve 50/25Mbps", "provider": "Openserve", "amount": 640}],
        "vip": True, "paid": True,
    },
    {
        # VIP — Zoomfibre + MTN LTE, both fully discounted
        "phone":       "+27713841638",
        "id_number":   "6908175220084",
        "name":        "Irvin Esau",
        "email":       "iresau7395@gmail.com",
        "address":     "5 Albatros St, Parkersdorp, Saldanha, 7395",
        "package_amt": "R0",
        "services":    [
            {"name": "Uncapped Zoomfibre 50/50Mbps", "provider": "Zoomfibre", "amount": 690},
            {"name": "Uncapped MTN LTE",             "provider": "MTN LTE",    "amount": 409},
        ],
        "vip": True, "paid": True,
    },
    {
        "phone":       "+27794937698",
        "id_number":   "6511065908089",
        "name":        "Berty De Laan",
        "email":       "bertydelaan@gmail.com",
        "address":     "4 Bromvoelslot, Andersonville, Pacaltsdorp, 6529",
        "package_amt": "R499",
        "services":    [{"name": "Uncapped Openserve 30/30Mbps", "provider": "Openserve", "amount": 499}],
        "vip": False, "paid": False,
    },
    # Enrico Gertse — no phone/ID; skipped
    {
        "phone":       "+27679889241",
        "id_number":   "6801275213085",
        "name":        "Arthur Frederick Pekeur",
        "email":       "arthurpekeur@gmail.com",
        "address":     "",
        "package_amt": "R799",
        "services":    [{"name": "2TB Telkom LTE Combo", "provider": "Telkom LTE", "amount": 799}],
        "vip": False, "paid": False,
    },
    {
        "phone":       "+27815082450",   # WhatsApp number
        "id_number":   "8702155132080",
        "name":        "Leonard Roelofse",
        "email":       "starcast.tech@gmail.com",
        "address":     "325 Dahlia, Grootbrak Rivier, Friemersheim, 6526",
        "package_amt": "R1572",
        "services":    [{"name": "Uncapped Octotel 300/200Mbps", "provider": "Octotel", "amount": 1572}],
        "vip": False, "paid": False,
    },
]


def seed():
    from datetime import datetime
    conn = sqlite3.connect(DB_PATH)

    # Ensure schema is up to date
    for col, defn in [
        ("address",      "TEXT DEFAULT ''"),
        ("services_json","TEXT DEFAULT '[]'"),
        ("vip",          "INTEGER NOT NULL DEFAULT 0"),
        ("paid_period",  "TEXT DEFAULT ''"),
    ]:
        try:
            conn.execute(f"ALTER TABLE clients ADD COLUMN {col} {defn}")
        except Exception:
            pass

    now = datetime.utcnow().isoformat()

    existing = {}
    if KEEP_PAID:
        for row in conn.execute("SELECT phone, paid, paid_period FROM clients").fetchall():
            existing[row[0]] = {"paid": row[1], "paid_period": row[2]}

    for c in CLIENTS:
        paid = existing.get(c["phone"], {}).get("paid", 1 if c["vip"] else 0) if KEEP_PAID else (1 if c["vip"] else 0)
        period = existing.get(c["phone"], {}).get("paid_period", "") if KEEP_PAID else ""

        conn.execute("""
            INSERT INTO clients
                (phone, id_number, name, email, address, package_amt, services_json, vip, paid, paid_period, updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(phone) DO UPDATE SET
                id_number    = excluded.id_number,
                name         = excluded.name,
                email        = excluded.email,
                address      = excluded.address,
                package_amt  = excluded.package_amt,
                services_json= excluded.services_json,
                vip          = excluded.vip,
                paid         = CASE WHEN ? THEN clients.paid ELSE excluded.paid END,
                paid_period  = CASE WHEN ? THEN clients.paid_period ELSE excluded.paid_period END,
                updated_at   = excluded.updated_at
        """, (
            c["phone"], c["id_number"], c["name"], c["email"], c["address"],
            c["package_amt"], json.dumps(c["services"]),
            1 if c["vip"] else 0, paid, period, now,
            KEEP_PAID, KEEP_PAID
        ))

    conn.commit()
    print(f"Seeded {len(CLIENTS)} clients (keep_paid={KEEP_PAID})")
    print()
    for row in conn.execute(
        "SELECT name, package_amt, vip, paid, services_json FROM clients ORDER BY name"
    ).fetchall():
        svcs = json.loads(row[4])
        svc_str = ", ".join(f"{s['name']} R{s['amount']}" for s in svcs)
        flags = ("VIP " if row[2] else "") + ("✓PAID" if row[3] else "UNPAID")
        print(f"  {row[0]:30s}  {row[1]:6s}  {flags:12s}  {svc_str}")
    conn.close()


if __name__ == "__main__":
    seed()
