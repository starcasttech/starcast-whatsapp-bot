import os
from flask import Flask, request, Response
from db import init_db
from bot import handle_message

app = Flask(__name__)

def twiml_reply(text):
    # Escape XML special chars
    safe = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    xml = f'<?xml version="1.0"?><Response><Message>{safe}</Message></Response>'
    return Response(xml, mimetype="text/xml")

@app.route("/webhook", methods=["POST"])
def webhook():
    phone = request.form.get("From", "unknown")
    body  = request.form.get("Body", "").strip()
    reply = handle_message(phone, body)
    return twiml_reply(reply)

@app.route("/health", methods=["GET"])
def health():
    return {"status": "ok", "service": "starcast-whatsapp-bot"}

@app.route("/submissions", methods=["GET"])
def submissions():
    from db import get_all_submissions
    token = request.args.get("token", "")
    if token != os.environ.get("ADMIN_TOKEN", "starcast2026"):
        return {"error": "unauthorized"}, 401
    return {"submissions": get_all_submissions()}

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5001)), debug=False)

# For gunicorn (Railway)
init_db()
