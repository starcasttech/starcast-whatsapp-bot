import os
import urllib.request
import urllib.parse

BOT_TOKEN = os.environ.get("TG_TOKEN", "")
CHAT_ID   = os.environ.get("TG_CHAT_ID", "")

def notify(message):
    if not BOT_TOKEN or not CHAT_ID:
        return
    url  = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = urllib.parse.urlencode({"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}).encode()
    req  = urllib.request.Request(url, data=data)
    try:
        urllib.request.urlopen(req, timeout=5)
    except Exception:
        pass  # Non-fatal — don't crash the bot if Telegram is unreachable
