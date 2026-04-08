from db import get_session, set_session, save_submission, get_all_submissions, get_client_by_phone, get_client_by_id, verify_client, update_client_details, update_client_phone

ADMIN_PHONES = {"+27815082450"}  # Leonard — add more if needed
from notify import notify

# ── Menu text ──────────────────────────────────────────────────────────────

WELCOME = (
    "👋 Welcome to *Starcast Technologies*!\n\n"
    "Please choose an option:\n\n"
    "1️⃣  Technical Support\n"
    "2️⃣  Get a Quote\n"
    "3️⃣  General Question\n"
    "4️⃣  Sign Up\n"
    "5️⃣  My Account\n\n"
    "Reply with a number (1-5)"
)

FIBRE_MENU = (
    "Which fibre network is in your area?\n\n"
    "1️⃣  Openserve\n"
    "2️⃣  Frogfoot\n"
    "3️⃣  Octotel\n"
    "4️⃣  Not sure — check my coverage\n\n"
    "Reply with a number (1-4)"
)

LTE_MENU = (
    "Which LTE provider?\n\n"
    "1️⃣  MTN\n"
    "2️⃣  Vodacom\n"
    "3️⃣  Telkom\n\n"
    "Reply with a number (1-3)"
)

QUOTE_MENU = (
    "📋 *Get a Quote*\n\n"
    "What are you interested in?\n\n"
    "1️⃣  Fibre Internet\n"
    "2️⃣  LTE / Mobile Internet\n"
    "3️⃣  CCTV & Security Cameras\n"
    "4️⃣  Gate & Garage Automation\n\n"
    "Reply with a number (1-4)"
)

FIBRE_PROVIDER_MENU = (
    "Which fibre network is in your area?\n\n"
    "1️⃣  Octotel\n"
    "2️⃣  Openserve\n"
    "3️⃣  Frogfoot\n"
    "4️⃣  Vuma\n"
    "5️⃣  MetroFibre\n"
    "6️⃣  Zoomfibre\n"
    "7️⃣  Not sure\n\n"
    "Reply with a number (1-7)"
)

LTE_PROVIDER_MENU = (
    "Which LTE network do you prefer?\n\n"
    "1️⃣  MTN\n"
    "2️⃣  Vodacom\n"
    "3️⃣  Telkom\n"
    "4️⃣  Not sure — best in my area\n\n"
    "Reply with a number (1-4)"
)

CONN_MENU = (
    "What type of connection are you interested in?\n\n"
    "1️⃣  Fibre\n"
    "2️⃣  LTE / Mobile\n\n"
    "Reply 1 or 2"
)

SUPPORT_MENU = (
    "🛠 *Technical Support*\n\n"
    "What is your issue?\n\n"
    "1️⃣  No internet\n"
    "2️⃣  Router offline\n"
    "3️⃣  No WiFi signal\n"
    "4️⃣  Internet dropping\n"
    "5️⃣  Other\n\n"
    "Reply with a number (1-5)"
)

DONE_MSG = (
    "✅ Thanks! We've received your message.\n"
    "A Starcast team member will be in touch shortly.\n\n"
    "Type *hi* to start again."
)

SIGNUP_DONE = (
    "✅ *Sign-up received!*\n\n"
    "Thank you for choosing Starcast Technologies.\n"
    "We will review your details and contact you within 24 hours to get you connected.\n\n"
    "Questions? Email us at starcast.tech@gmail.com\n"
    "Type *hi* to start again."
)

COVERAGE_MSG = (
    "📍 To check coverage in your area, please visit:\n"
    "https://starcast.co.za\n\n"
    "Or send us your physical address and we'll check for you.\n"
    "Type *hi* to start again."
)


# ── Main dispatcher ────────────────────────────────────────────────────────

def handle_message(phone, body):
    text  = body.strip()
    state, data = get_session(phone)

    # Admin command — Leonard only
    if text.lower() == "!tasks":
        return _admin_tasks(phone)

    # Reset keywords always work
    if text.lower() in ("hi", "hello", "hey", "menu", "start", "0"):
        set_session(phone, "MENU", {})
        return WELCOME

    handlers = {
        "IDLE":                   _idle,
        "MENU":                   _menu,
        "SUPPORT_TYPE":           _support_type,
        "SUPPORT_DESCRIBE":       _support_describe,
        "SUPPORT_VERIFY_ID":      _support_verify_id,
        "QUOTE_MENU":             _quote_menu,
        "QUOTE_TYPE":             _quote_menu,        # legacy alias
        "QUOTE_ADDRESS":          _quote_address,
        "QUOTE_FIBRE_PROVIDER":   _quote_fibre_provider,
        "QUOTE_LTE_PROVIDER":     _quote_lte_provider,
        "QUOTE_FIRSTNAME":        _quote_firstname,
        "QUOTE_SURNAME":          _quote_surname,
        "QUOTE_PHONE":            _quote_phone,
        "SECURITY_FIRSTNAME":     _security_firstname,
        "SECURITY_SURNAME":       _security_surname,
        "SECURITY_PHONE":         _security_phone,
        "SECURITY_EMAIL":         _security_email,
        "SECURITY_DESCRIBE":      _security_describe,
        "GENERAL_QUESTION":       _general_question,
        "SIGNUP_FIRSTNAME":       _signup_firstname,
        "SIGNUP_SURNAME":         _signup_surname,
        "SIGNUP_EMAIL":           _signup_email,
        "SIGNUP_ADDRESS":         _signup_address,
        "SIGNUP_CONNTYPE":        _signup_conntype,
        "SIGNUP_FIBRE_PROVIDER":  _signup_fibre_provider,
        "SIGNUP_LTE_PROVIDER":    _signup_lte_provider,
        "ACCOUNT_VERIFY_ID":      _account_verify_id,
        "ACCOUNT_MENU":           _account_menu,
        "ACCOUNT_UPDATE_EMAIL":   _account_update_email,
        "ACCOUNT_UPDATE_PHONE":   _account_update_phone,
        "ACCOUNT_MOVE_LOCATION":  _account_move_location,
        "ACCOUNT_CANCEL":         _account_cancel,
        "DONE":                   _done,
    }

    handler = handlers.get(state, _idle)
    return handler(phone, text, data)


# ── State handlers ─────────────────────────────────────────────────────────

def _idle(phone, text, data):
    set_session(phone, "MENU", {})
    return WELCOME

def _done(phone, text, data):
    set_session(phone, "MENU", {})
    return WELCOME

def _menu(phone, text, data):
    if text == "1":
        set_session(phone, "SUPPORT_TYPE", {})
        return SUPPORT_MENU
    elif text == "2":
        set_session(phone, "QUOTE_MENU", {})
        return QUOTE_MENU
    elif text == "3":
        set_session(phone, "GENERAL_QUESTION", {})
        return "💬 *General Question*\n\nPlease type your question."
    elif text == "4":
        set_session(phone, "SIGNUP_FIRSTNAME", {})
        return "🚀 *Sign Up for Starcast Internet*\n\nLet's get you connected! What is your *first name*?"
    elif text == "5":
        set_session(phone, "ACCOUNT_VERIFY_ID", {})
        return (
            "🔐 *My Account*\n\n"
            "Please enter your *ID number* to verify your account."
        )
    else:
        return "Please reply with a number 1-5.\n\n" + WELCOME

_SUPPORT_TYPES = {
    "1": "No internet",
    "2": "Router offline",
    "3": "No WiFi signal",
    "4": "Internet dropping",
    "5": "Other",
}

def _support_type(phone, text, data):
    if text not in _SUPPORT_TYPES:
        return "Please reply with a number 1-5.\n\n" + SUPPORT_MENU
    data["issue_type"] = _SUPPORT_TYPES[text]
    set_session(phone, "SUPPORT_DESCRIBE", data)
    return "Please briefly *describe your problem*:"

def _support_describe(phone, text, data):
    data["description"] = text
    set_session(phone, "SUPPORT_VERIFY_ID", data)
    return (
        "🔐 Please enter your *ID number* so we can pull up your account\n"
        "and have a consultant call you back."
    )

def _support_verify_id(phone, text, data):
    if text.strip() == "0":
        _submit_support(phone, data, client=None)
        set_session(phone, "DONE", {})
        return (
            "✅ *Fault logged.*\n\n"
            "A consultant will call you back on this number as soon as possible.\n\n"
            "Type *hi* to start again."
        )
    client = get_client_by_id(text)
    if not client:
        attempts = data.get("attempts", 0) + 1
        if attempts >= 2:
            # Still submit without account — use phone number as contact
            _submit_support(phone, data, client=None)
            set_session(phone, "DONE", {})
            return (
                "✅ *Fault logged.*\n\n"
                "We could not find your account but your fault has been logged.\n"
                "A consultant will call you back on this number as soon as possible.\n\n"
                "Type *hi* to start again."
            )
        data["attempts"] = attempts
        set_session(phone, "SUPPORT_VERIFY_ID", data)
        return "❌ ID number not found. Please try again or type *0* to skip."
    _submit_support(phone, data, client)
    set_session(phone, "DONE", {})
    return (
        f"✅ *Fault logged, {client['name'].split()[0]}!*\n\n"
        f"Issue: {data.get('issue_type', '')}\n\n"
        "A consultant will call you back as soon as possible.\n\n"
        "Type *hi* to start again."
    )

def _submit_support(phone, data, client):
    record = {**data, "whatsapp": phone}
    if client:
        record["name"]    = client["name"]
        record["address"] = client.get("address", "")
        record["service"] = ", ".join(s["name"] for s in client.get("services", []))
    save_submission(phone, "support", record)
    notify(
        f"🛠 <b>[SUPPORT]</b> Fault from "
        f"<b>{client['name'] if client else 'Unknown'}</b>\n\n"
        f"<b>Issue:</b> {data.get('issue_type', '?')}\n"
        f"<b>Description:</b> {data.get('description', '?')}\n"
        f"<b>Service:</b> {', '.join(s['name'] for s in client.get('services', [])) if client else 'unknown'}\n"
        f"<b>Address:</b> {client.get('address', 'unknown') if client else 'unknown'}\n"
        f"<b>Call back:</b> {phone}"
    )

def _general_question(phone, text, data):
    data["question"] = text
    save_submission(phone, "general", data)
    notify(
        f"💬 <b>[GENERAL]</b> Question from {phone}\n\n"
        f"<b>Question:</b> {text}"
    )
    set_session(phone, "DONE", {})
    return DONE_MSG

# ── Quote handlers ─────────────────────────────────────────────────────────

def _quote_menu(phone, text, data):
    if text == "1":
        data["quote_type"] = "Fibre Internet"
        set_session(phone, "QUOTE_FIBRE_PROVIDER", data)
        return FIBRE_PROVIDER_MENU
    elif text == "2":
        data["quote_type"] = "LTE Internet"
        set_session(phone, "QUOTE_LTE_PROVIDER", data)
        return LTE_PROVIDER_MENU
    elif text == "3":
        data["quote_type"] = "CCTV & Security"
        set_session(phone, "SECURITY_FIRSTNAME", data)
        return "📷 *CCTV & Security Quote*\n\nWhat is your *first name*?"
    elif text == "4":
        data["quote_type"] = "Gate & Garage Automation"
        set_session(phone, "SECURITY_FIRSTNAME", data)
        return "🔧 *Gate & Garage Automation Quote*\n\nWhat is your *first name*?"
    return "Please reply with a number 1-4.\n\n" + QUOTE_MENU

def _quote_fibre_provider(phone, text, data):
    providers = {"1": "Octotel", "2": "Openserve", "3": "Frogfoot",
                 "4": "Vuma", "5": "MetroFibre", "6": "Zoomfibre", "7": "Not sure"}
    if text not in providers:
        return "Please reply with a number 1-7.\n\n" + FIBRE_PROVIDER_MENU
    data["provider"] = providers[text]
    set_session(phone, "QUOTE_ADDRESS", data)
    return "📍 What is your *physical address*? (Street, suburb, city)"

def _quote_lte_provider(phone, text, data):
    providers = {"1": "MTN", "2": "Vodacom", "3": "Telkom", "4": "Not sure"}
    if text not in providers:
        return "Please reply with a number 1-4.\n\n" + LTE_PROVIDER_MENU
    data["provider"] = providers[text]
    set_session(phone, "QUOTE_ADDRESS", data)
    return "📍 What is your *physical address*? (Street, suburb, city)"

def _quote_address(phone, text, data):
    data["address"] = text
    set_session(phone, "QUOTE_FIRSTNAME", data)
    return "What is your *first name*?"

def _quote_firstname(phone, text, data):
    data["first_name"] = text
    set_session(phone, "QUOTE_SURNAME", data)
    return "What is your *surname*?"

def _quote_surname(phone, text, data):
    data["surname"] = text
    set_session(phone, "QUOTE_PHONE", data)
    return "What is your *cell number*? A consultant will call you back."

def _quote_phone(phone, text, data):
    data["contact_number"] = text
    save_submission(phone, "quote", data)
    notify(
        f"📋 <b>[QUOTE — {data.get('quote_type','Internet')}]</b>\n\n"
        f"<b>Name:</b> {data.get('first_name','')} {data.get('surname','')}\n"
        f"<b>Provider:</b> {data.get('provider','?')}\n"
        f"<b>Address:</b> {data.get('address','?')}\n"
        f"<b>Call back:</b> {text}"
    )
    set_session(phone, "DONE", {})
    return (
        "✅ *Quote request received!*\n\n"
        "A Starcast consultant will call you back as soon as possible.\n\n"
        "Type *hi* to start again."
    )

# ── Security / Automation quote handlers ───────────────────────────────────

def _security_firstname(phone, text, data):
    data["first_name"] = text
    set_session(phone, "SECURITY_SURNAME", data)
    return "What is your *surname*?"

def _security_surname(phone, text, data):
    data["surname"] = text
    set_session(phone, "SECURITY_PHONE", data)
    return "What is your *cell number*?"

def _security_phone(phone, text, data):
    data["contact_number"] = text
    set_session(phone, "SECURITY_EMAIL", data)
    return "What is your *email address*?"

def _security_email(phone, text, data):
    data["email"] = text
    set_session(phone, "SECURITY_DESCRIBE", data)
    return "Please *describe what you need* (e.g. number of cameras, location, gate type, etc.):"

def _security_describe(phone, text, data):
    data["description"] = text
    save_submission(phone, "security_quote", data)
    notify(
        f"🔒 <b>[QUOTE — {data.get('quote_type','Security')}]</b>\n\n"
        f"<b>Name:</b> {data.get('first_name','')} {data.get('surname','')}\n"
        f"<b>Cell:</b> {data.get('contact_number','?')}\n"
        f"<b>Email:</b> {data.get('email','?')}\n"
        f"<b>Description:</b> {text}"
    )
    set_session(phone, "DONE", {})
    return (
        "✅ *Quote request received!*\n\n"
        "A Starcast consultant will get back to you as soon as possible.\n\n"
        "Type *hi* to start again."
    )

def _signup_firstname(phone, text, data):
    data["first_name"] = text
    set_session(phone, "SIGNUP_SURNAME", data)
    return f"Nice to meet you, {text}! 👋\n\nWhat is your *surname*?"

def _signup_surname(phone, text, data):
    data["surname"] = text
    set_session(phone, "SIGNUP_EMAIL", data)
    return "What is your *email address*?"

def _signup_email(phone, text, data):
    data["email"] = text
    set_session(phone, "SIGNUP_ADDRESS", data)
    return "What is your *physical address*? (Street, suburb, city)"

def _signup_address(phone, text, data):
    data["address"] = text
    set_session(phone, "SIGNUP_CONNTYPE", data)
    return CONN_MENU

def _signup_conntype(phone, text, data):
    if text == "1":
        data["conn_type"] = "Fibre"
        set_session(phone, "SIGNUP_FIBRE_PROVIDER", data)
        return FIBRE_MENU
    elif text == "2":
        data["conn_type"] = "LTE"
        set_session(phone, "SIGNUP_LTE_PROVIDER", data)
        return LTE_MENU
    else:
        return "Please reply 1 for Fibre or 2 for LTE.\n\n" + CONN_MENU

def _signup_fibre_provider(phone, text, data):
    providers = {"1": "Openserve", "2": "Frogfoot", "3": "Octotel", "4": "Check Coverage"}
    if text in providers:
        if text == "4":
            set_session(phone, "DONE", {})
            return (
                "📍 To check fibre coverage, visit https://starcast.co.za\n"
                "or send us your address and we'll check for you!\n\n"
                "Type *hi* to start again."
            )
        data["provider"] = providers[text]
        _complete_signup(phone, data)
        return SIGNUP_DONE
    return "Please reply with a number 1-4.\n\n" + FIBRE_MENU

def _signup_lte_provider(phone, text, data):
    providers = {"1": "MTN", "2": "Vodacom", "3": "Telkom"}
    if text in providers:
        data["provider"] = providers[text]
        _complete_signup(phone, data)
        return SIGNUP_DONE
    return "Please reply with a number 1-3.\n\n" + LTE_MENU

def _complete_signup(phone, data):
    save_submission(phone, "signup", data)
    set_session(phone, "DONE", {})
    notify(
        f"🚀 <b>[SIGNUP]</b> New sign-up from {phone}\n\n"
        f"<b>Name:</b> {data.get('first_name', '')} {data.get('surname', '')}\n"
        f"<b>Email:</b> {data.get('email', '')}\n"
        f"<b>Address:</b> {data.get('address', '')}\n"
        f"<b>Connection:</b> {data.get('conn_type', '')} / {data.get('provider', '')}"
    )


# ── Account check handlers ─────────────────────────────────────────────────

_ACCOUNT_MENU_TEXT = (
    "What would you like to do?\n\n"
    "1️⃣  View my account details\n"
    "2️⃣  Update my email\n"
    "3️⃣  Update my phone number\n"
    "4️⃣  Request to move location\n"
    "5️⃣  Cancel my service\n"
    "0️⃣  Main menu\n\n"
    "Reply with a number"
)

def _format_account_summary(client):
    """Build the account summary block shown after verification and on view."""
    lines = [f"👤 *{client['name']}*\n"]

    services = client.get("services", [])
    if services:
        lines.append("📋 *Your Services:*")
        for s in services:
            lines.append(f"  • {s['name']} — R{s['amount']}/month")
        lines.append("")

    if client["vip"]:
        lines.append("💳 *Status: ✅ VIP — Nothing due*")
    else:
        total = client["package_amt"]
        period = client.get("paid_period", "")
        if client["paid"] and period:
            lines.append(f"💳 *Status: ✅ Paid ({period})*")
            lines.append(f"   Amount: {total}/month")
        else:
            lines.append(f"💳 *Status: ⚠️ Unpaid*")
            lines.append(f"   Amount due: {total}")
            lines.append(f"   Ref: use your ID number as payment reference")

    return "\n".join(lines)

def _account_verify_id(phone, text, data):
    client = get_client_by_id(text)
    if not client:
        attempts = data.get("attempts", 0) + 1
        if attempts >= 2:
            set_session(phone, "DONE", {})
            return (
                "❌ ID number not found in our records.\n"
                "Please contact us at starcast.tech@gmail.com\n\n"
                "Type *hi* to start again."
            )
        set_session(phone, "ACCOUNT_VERIFY_ID", {"attempts": attempts})
        return "❌ ID number not found. Please try again."
    # Verified — store the client's DB phone so updates go to the right record
    set_session(phone, "ACCOUNT_MENU", {"client_phone": client["phone"]})
    return (
        f"✅ *Verified! Welcome, {client['name'].split()[0]}!*\n\n"
        + _format_account_summary(client) + "\n\n"
        + _ACCOUNT_MENU_TEXT
    )

def _account_menu(phone, text, data):
    client = get_client_by_phone(data.get("client_phone", phone))
    if not client:
        set_session(phone, "DONE", {})
        return WELCOME

    if text == "1":
        return (
            _format_account_summary(client) + "\n\n"
            f"📧 Email: {client['email'] or 'not on file'}\n\n"
            + _ACCOUNT_MENU_TEXT
        )
    elif text == "2":
        set_session(phone, "ACCOUNT_UPDATE_EMAIL", data)
        return "Please type your updated *email address*:"
    elif text == "3":
        set_session(phone, "ACCOUNT_UPDATE_PHONE", data)
        return "Please type your updated *cell number* (e.g. 0821234567 or +27821234567):"
    elif text == "4":
        set_session(phone, "ACCOUNT_MOVE_LOCATION", data)
        return "📍 *Move Location Request*\n\nPlease type your *new address* (street, suburb, city) and we will check coverage and get back to you."
    elif text == "5":
        set_session(phone, "ACCOUNT_CANCEL", data)
        return "⚠️ *Cancel Service*\n\nAre you sure you want to cancel? Type *YES* to confirm or *NO* to go back."
    elif text == "0":
        set_session(phone, "MENU", {})
        return WELCOME
    else:
        return "Please reply with 1, 2, 3 or 0.\n\n" + _ACCOUNT_MENU_TEXT

def _account_update_email(phone, text, data):
    client_phone = data.get("client_phone", phone)
    update_client_details(client_phone, email=text)
    notify(f"✏️ <b>[ACCOUNT]</b> Email updated for {client_phone}\n<b>New email:</b> {text}")
    set_session(phone, "ACCOUNT_MENU", data)
    return f"✅ Email updated to *{text}*.\n\n" + _ACCOUNT_MENU_TEXT

def _account_update_phone(phone, text, data):
    client_phone = data.get("client_phone", phone)
    new_phone = update_client_phone(client_phone, text)
    data["client_phone"] = new_phone
    notify(f"✏️ <b>[ACCOUNT]</b> Phone updated for {client_phone}\n<b>New phone:</b> {new_phone}")
    set_session(phone, "ACCOUNT_MENU", data)
    return f"✅ Phone number updated to *{new_phone}*.\n\n" + _ACCOUNT_MENU_TEXT

def _account_move_location(phone, text, data):
    client_phone = data.get("client_phone", phone)
    client = get_client_by_phone(client_phone)
    save_submission(phone, "move_request", {"name": client["name"] if client else "", "new_address": text})
    notify(
        f"📍 <b>[MOVE REQUEST]</b> from {client['name'] if client else phone}\n\n"
        f"<b>New address:</b> {text}\n"
        f"<b>Current service:</b> {', '.join(s['name'] for s in (client.get('services') or []))}"
    )
    set_session(phone, "ACCOUNT_MENU", data)
    return (
        "✅ *Move request received!*\n\n"
        "We will check coverage at your new address and contact you within 24 hours.\n\n"
        + _ACCOUNT_MENU_TEXT
    )

def _account_cancel(phone, text, data):
    client_phone = data.get("client_phone", phone)
    client = get_client_by_phone(client_phone)
    if text.strip().upper() == "YES":
        save_submission(phone, "cancel_request", {"name": client["name"] if client else ""})
        notify(
            f"🚨 <b>[CANCEL REQUEST]</b> from {client['name'] if client else phone}\n\n"
            f"<b>Service:</b> {', '.join(s['name'] for s in (client.get('services') or []))}\n"
            f"<b>Amount:</b> {client['package_amt'] if client else '?'}/month\n\n"
            f"⚠️ Action required — contact client before cancelling."
        )
        set_session(phone, "DONE", {})
        return (
            "✅ *Cancellation request received.*\n\n"
            "A Starcast team member will contact you within 24 hours to process your cancellation.\n\n"
            "Type *hi* to return to the main menu."
        )
    else:
        set_session(phone, "ACCOUNT_MENU", data)
        return "No problem — your service continues as normal.\n\n" + _ACCOUNT_MENU_TEXT


# ── Admin task list ────────────────────────────────────────────────────────

def _admin_tasks(phone):
    from db import _clean_phone
    clean = _clean_phone(phone)
    if clean not in ADMIN_PHONES:
        return "Unknown command."

    subs = get_all_submissions()
    if not subs:
        return "✅ No pending submissions."

    # Group by type, show last 20
    recent = subs[:20]
    _type_icons = {
        "support":        "🛠",
        "quote":          "📋",
        "security_quote": "🔒",
        "general":        "💬",
        "signup":         "🚀",
        "move_request":   "📍",
        "cancel_request": "🚨",
    }
    lines = [f"📋 *Pending Tasks* — {len(subs)} total\n"]
    for s in recent:
        icon = _type_icons.get(s["type"], "📌")
        d = s["data"]
        name = d.get("name") or f"{d.get('first_name','')} {d.get('surname','')}".strip() or s["phone"]
        detail = (
            d.get("issue_type") or d.get("quote_type") or
            d.get("description","")[:40] or d.get("question","")[:40]
        )
        date = s["created_at"][:10]
        lines.append(f"{icon} *{s['type'].replace('_',' ').title()}* — {name}\n   {detail} ({date})")

    return "\n\n".join(lines)
