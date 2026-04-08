from db import get_session, set_session, save_submission, get_client_by_phone, get_client_by_id, verify_client, update_client_details
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

CONN_MENU = (
    "What type of connection are you interested in?\n\n"
    "1️⃣  Fibre\n"
    "2️⃣  LTE / Mobile\n\n"
    "Reply 1 or 2"
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

    # Reset keywords always work
    if text.lower() in ("hi", "hello", "hey", "menu", "start", "0"):
        set_session(phone, "MENU", {})
        return WELCOME

    handlers = {
        "IDLE":                   _idle,
        "MENU":                   _menu,
        "SUPPORT_DESCRIBE":       _support_describe,
        "QUOTE_TYPE":             _quote_type,
        "QUOTE_FIBRE_PROVIDER":   _quote_fibre_provider,
        "QUOTE_LTE_PROVIDER":     _quote_lte_provider,
        "QUOTE_ADDRESS":          _quote_address,
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
        "ACCOUNT_UPDATE_NAME":    _account_update_name,
        "ACCOUNT_UPDATE_EMAIL":   _account_update_email,
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
        set_session(phone, "SUPPORT_DESCRIBE", {})
        return "🛠 *Technical Support*\n\nPlease describe your issue and we'll get someone to assist you."
    elif text == "2":
        set_session(phone, "QUOTE_TYPE", {})
        return "📋 *Get a Quote*\n\n" + CONN_MENU
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

def _support_describe(phone, text, data):
    data["issue"] = text
    save_submission(phone, "support", data)
    notify(
        f"🛠 <b>[SUPPORT]</b> Issue from {phone}\n\n"
        f"<b>Message:</b> {text}"
    )
    set_session(phone, "DONE", {})
    return DONE_MSG

def _general_question(phone, text, data):
    data["question"] = text
    save_submission(phone, "general", data)
    notify(
        f"💬 <b>[GENERAL]</b> Question from {phone}\n\n"
        f"<b>Question:</b> {text}"
    )
    set_session(phone, "DONE", {})
    return DONE_MSG

def _quote_type(phone, text, data):
    if text == "1":
        data["conn_type"] = "Fibre"
        set_session(phone, "QUOTE_FIBRE_PROVIDER", data)
        return "Which fibre network covers your area?\n\n" + FIBRE_MENU
    elif text == "2":
        data["conn_type"] = "LTE"
        set_session(phone, "QUOTE_LTE_PROVIDER", data)
        return LTE_MENU
    else:
        return "Please reply 1 for Fibre or 2 for LTE.\n\n" + CONN_MENU

def _quote_fibre_provider(phone, text, data):
    providers = {"1": "Openserve", "2": "Frogfoot", "3": "Octotel", "4": "Check Coverage"}
    if text in providers:
        if text == "4":
            set_session(phone, "DONE", {})
            return COVERAGE_MSG
        data["provider"] = providers[text]
        set_session(phone, "QUOTE_ADDRESS", data)
        return "📍 What is your *physical address*? (Street, suburb, city)"
    return "Please reply with a number 1-4.\n\n" + FIBRE_MENU

def _quote_lte_provider(phone, text, data):
    providers = {"1": "MTN", "2": "Vodacom", "3": "Telkom"}
    if text in providers:
        data["provider"] = providers[text]
        set_session(phone, "QUOTE_ADDRESS", data)
        return "📍 What is your *physical address*? (Street, suburb, city)"
    return "Please reply with a number 1-3.\n\n" + LTE_MENU

def _quote_address(phone, text, data):
    data["address"] = text
    save_submission(phone, "quote", data)
    notify(
        f"📋 <b>[QUOTE]</b> Quote request from {phone}\n\n"
        f"<b>Connection:</b> {data.get('conn_type', '?')} / {data.get('provider', '?')}\n"
        f"<b>Address:</b> {text}"
    )
    set_session(phone, "DONE", {})
    return DONE_MSG

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
    "2️⃣  Update my name\n"
    "3️⃣  Update my email\n"
    "0️⃣  Main menu\n\n"
    "Reply with a number"
)

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
    status = "✅ Paid" if client["paid"] else "⚠️ Unpaid"
    return (
        f"✅ *Verified!*\n\n"
        f"Welcome, {client['name'].split()[0]}!\n\n"
        f"📦 Package: {client['package_amt']}/month\n"
        f"💳 Status:  {status}\n\n"
        + _ACCOUNT_MENU_TEXT
    )

def _account_menu(phone, text, data):
    client = get_client_by_phone(data.get("client_phone", phone))
    if not client:
        set_session(phone, "DONE", {})
        return WELCOME

    if text == "1":
        status = "✅ Paid" if client["paid"] else "⚠️ Unpaid — please make your payment"
        return (
            f"👤 *Account Details*\n\n"
            f"Name:    {client['name']}\n"
            f"Email:   {client['email'] or 'not on file'}\n"
            f"Package: {client['package_amt']}/month\n"
            f"Status:  {status}\n\n"
            + _ACCOUNT_MENU_TEXT
        )
    elif text == "2":
        set_session(phone, "ACCOUNT_UPDATE_NAME", data)
        return "Please type your updated *full name*:"
    elif text == "3":
        set_session(phone, "ACCOUNT_UPDATE_EMAIL", data)
        return "Please type your updated *email address*:"
    elif text == "0":
        set_session(phone, "MENU", {})
        return WELCOME
    else:
        return "Please reply with 1, 2, 3 or 0.\n\n" + _ACCOUNT_MENU_TEXT

def _account_update_name(phone, text, data):
    client_phone = data.get("client_phone", phone)
    update_client_details(client_phone, name=text)
    notify(f"✏️ <b>[ACCOUNT]</b> Name updated for {client_phone}\n<b>New name:</b> {text}")
    set_session(phone, "ACCOUNT_MENU", data)
    return f"✅ Name updated to *{text}*.\n\n" + _ACCOUNT_MENU_TEXT

def _account_update_email(phone, text, data):
    client_phone = data.get("client_phone", phone)
    update_client_details(client_phone, email=text)
    notify(f"✏️ <b>[ACCOUNT]</b> Email updated for {client_phone}\n<b>New email:</b> {text}")
    set_session(phone, "ACCOUNT_MENU", data)
    return f"✅ Email updated to *{text}*.\n\n" + _ACCOUNT_MENU_TEXT
