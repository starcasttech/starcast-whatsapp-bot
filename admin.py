"""
Starcast WhatsApp Bot — Admin CLI
Usage:
  python3 admin.py list                          # show all clients + paid status
  python3 admin.py paid <id_number> [period]     # mark client as paid (period default: current month)
  python3 admin.py unpaid <id_number>            # mark client as unpaid
  python3 admin.py reset-all-unpaid              # reset all non-VIP clients to unpaid (new month)
  python3 admin.py show <id_number>              # show full client record
"""
import sqlite3, json, sys
import os as _os
from datetime import datetime

DB_PATH = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "starcast.db")

def conn():
    return sqlite3.connect(DB_PATH)

def get_by_id(id_number):
    c = conn()
    row = c.execute(
        "SELECT phone,id_number,name,email,package_amt,paid,vip,services_json,paid_period "
        "FROM clients WHERE id_number = ?", (id_number,)
    ).fetchone()
    c.close()
    return row

def cmd_list():
    c = conn()
    rows = c.execute(
        "SELECT name, id_number, package_amt, vip, paid, paid_period FROM clients ORDER BY name"
    ).fetchall()
    c.close()
    print(f"\n{'Name':<30} {'ID Number':<15} {'Amount':<8} {'Status'}")
    print("-" * 72)
    for r in rows:
        name, id_nr, amt, vip, paid, period = r
        if vip:
            status = "VIP (nothing due)"
        elif paid:
            status = f"✓ Paid — {period}"
        else:
            status = "✗ Unpaid"
        print(f"{name:<30} {id_nr:<15} {amt:<8} {status}")
    print()

def cmd_paid(id_number, period=None):
    if not period:
        period = datetime.now().strftime("%B %Y")
    row = get_by_id(id_number)
    if not row:
        print(f"ERROR: No client with ID {id_number}")
        return
    c = conn()
    c.execute(
        "UPDATE clients SET paid=1, paid_period=?, updated_at=? WHERE id_number=?",
        (period, datetime.utcnow().isoformat(), id_number)
    )
    c.commit()
    c.close()
    print(f"✓ {row[2]} marked as PAID for {period}")

def cmd_unpaid(id_number):
    row = get_by_id(id_number)
    if not row:
        print(f"ERROR: No client with ID {id_number}")
        return
    c = conn()
    c.execute(
        "UPDATE clients SET paid=0, paid_period='', updated_at=? WHERE id_number=?",
        (datetime.utcnow().isoformat(), id_number)
    )
    c.commit()
    c.close()
    print(f"✓ {row[2]} marked as UNPAID")

def cmd_reset_all_unpaid():
    c = conn()
    result = c.execute(
        "UPDATE clients SET paid=0, paid_period='' WHERE vip=0"
    )
    c.commit()
    n = result.rowcount
    c.close()
    print(f"✓ Reset {n} non-VIP clients to UNPAID (new month)")

def cmd_show(id_number):
    row = get_by_id(id_number)
    if not row:
        print(f"ERROR: No client with ID {id_number}")
        return
    phone, id_nr, name, email, amt, paid, vip, svcs_json, period = row
    svcs = json.loads(svcs_json) if svcs_json else []
    print(f"\nClient:      {name}")
    print(f"ID Number:   {id_nr}")
    print(f"Phone:       {phone}")
    print(f"Email:       {email}")
    print(f"Amount:      {amt}/month")
    print(f"VIP:         {'Yes' if vip else 'No'}")
    print(f"Paid:        {'Yes — ' + period if paid else 'No'}")
    print(f"Services:")
    for s in svcs:
        print(f"  • {s['name']} ({s['provider']}) — R{s['amount']}/month")
    print()

if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] == "list":
        cmd_list()
    elif args[0] == "paid" and len(args) >= 2:
        cmd_paid(args[1], args[2] if len(args) > 2 else None)
    elif args[0] == "unpaid" and len(args) >= 2:
        cmd_unpaid(args[1])
    elif args[0] == "reset-all-unpaid":
        cmd_reset_all_unpaid()
    elif args[0] == "show" and len(args) >= 2:
        cmd_show(args[1])
    else:
        print(__doc__)
