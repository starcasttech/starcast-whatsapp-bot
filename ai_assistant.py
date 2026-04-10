"""
AI assistant for Starcast WhatsApp bot.
Uses Amazon Nova Micro via AWS Bedrock — cheap, fast, no extra API keys.
Answers general customer questions automatically.
Escalates to Leonard for account/billing/sensitive issues.
Also drives step-by-step technical troubleshooting for internet faults.
"""

import os
import boto3
from botocore.exceptions import ClientError

AWS_REGION   = os.environ.get("AWS_REGION", "us-east-1")
AWS_KEY      = os.environ.get("AWS_ACCESS_KEY_ID", "")
AWS_SECRET   = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
MODEL_ID     = "amazon.nova-micro-v1:0"

SYSTEM_PROMPT = """You are a helpful customer service assistant for Starcast Technologies, a South African ISP reseller based in Friemersheim, George (Garden Route).

COMPANY INFO:
- Name: Starcast Technologies (Pty) Ltd
- Reg: 2023/770423/07
- Location: 325 Dahlia St, Friemersheim, 6526
- WhatsApp: +27 87 250 2788
- Email: starcast.tech@gmail.com
- NOT VAT registered

SERVICES WE OFFER:
1. Fibre Internet (via Octotel, Openserve, Frogfoot, MetroFibre, Vumatel, Zoomfibre)
2. LTE/5G Internet (via MTN, Vodacom, Telkom)
3. CCTV Installations
4. Gate & Garage Motor installations and repairs
5. Solar solutions

ABOUT FIBRE:
- We are a reseller — we use established fibre network providers to deliver internet
- Coverage depends on area and which fibre network is installed
- Speeds range from 10Mbps to 1Gbps depending on package and provider
- Customers contact us to sign up, we handle the order with the network provider

HOW TO HELP CUSTOMERS:
- For sign-up enquiries: tell them to type 4 on the main menu or visit starcast.co.za
- For technical support/faults: tell them to type 1 on the main menu
- For quotes: tell them to type 2 on the main menu
- For account/billing questions: tell them to type 5 on the main menu
- For ISP outages: tell them to type 6 on the main menu

RULES:
- Keep answers SHORT and friendly — this is WhatsApp, not email
- Never make up specific pricing (tell them to request a quote via option 2)
- Never discuss specific client account details
- If asked about payment status or balances — direct to option 5 (My Account)
- If the question is a complaint or urgent fault — direct to option 1 (Technical Support)
- Sign off with "Type *0* to return to the main menu." on every response
- If you genuinely cannot answer or it requires human judgement — say ESCALATE

Respond in plain text only — no markdown headers, no bullet lists with dashes. Use WhatsApp formatting: *bold* for emphasis."""

# Topics that should always go to Leonard
ESCALATE_KEYWORDS = {
    "cancel", "cancelled", "cancellation",
    "refund", "credit", "overcharged",
    "legal", "lawsuit", "complaint",
    "password", "login", "account number",
    "contract", "breach",
}


def _should_escalate_immediately(text: str) -> bool:
    """Flag messages that must go straight to Leonard without AI attempt."""
    lower = text.lower()
    return any(kw in lower for kw in ESCALATE_KEYWORDS)


def _get_bedrock_client():
    if AWS_KEY and AWS_SECRET:
        return boto3.client(
            "bedrock-runtime",
            region_name=AWS_REGION,
            aws_access_key_id=AWS_KEY,
            aws_secret_access_key=AWS_SECRET,
        )
    # Fall back to instance profile / env credentials
    return boto3.client("bedrock-runtime", region_name=AWS_REGION)


_TROUBLESHOOT_PROMPT = """You are a technical support assistant for Starcast Technologies, a South African ISP reseller.
Your job is to guide a customer through troubleshooting their internet connection via WhatsApp.

EQUIPMENT IN SA:
- ONT (Optical Network Terminal) = the white/grey box where the fibre cable enters the house. Has indicator lights.
- Router = the WiFi device (often a separate unit from the ONT, sometimes combined).
- Common ONT brands: ZTE, Huawei, Nokia/Alcatel-Lucent.

ONT LIGHTS (typical SA setup):
- PWR (Power) — must be solid green
- LOS / LOS (Loss of Signal) — must be OFF. If RED/blinking = fibre signal problem, likely ISP or cable issue
- PON / GPON — solid green = connected to exchange
- LAN / DATA — blinking = traffic flowing (good sign)
- INTERNET / SVC — solid green = authenticated and online

REBOOT SEQUENCE (always do ONT first):
1. Unplug ONT power → wait 30 seconds → plug back in → wait 2 minutes
2. Then reboot router → wait 1 minute
3. Test connection

RULES:
- Give ONE concise troubleshooting step per response
- Use plain text (no markdown headers). Bold with *asterisks* for WhatsApp.
- Keep it SHORT — max 5 lines. This is WhatsApp.
- Step 1 = gentlest fix (reboot sequence / check lights)
- Step 2 = deeper check (cable connections, reset to defaults, isolate ONT vs router)
- Always end step with: "Did that fix it? Reply *yes* or *no*"
- If ISP has an outage, mention it briefly at the start so the customer knows it may not be their fault.
- Do NOT suggest calling Leonard or logging a fault — that happens automatically if steps fail."""


def troubleshoot(issue_type: str, description: str, isp_name: str,
                 step: int, outage_status: str = None) -> str:
    """
    Generate a troubleshooting step for a customer internet fault.

    Returns a WhatsApp-ready string (or empty string on error).
    """
    try:
        bedrock = _get_bedrock_client()

        outage_note = ""
        if outage_status and outage_status not in ("OPERATIONAL", "UNKNOWN", "NOREPORTS", None):
            outage_note = f"\nNOTE: {isp_name} is currently showing a network issue ({outage_status}). Mention this briefly."

        user_msg = (
            f"Issue type: {issue_type}\n"
            f"Customer description: {description}\n"
            f"ISP / fibre provider: {isp_name or 'unknown'}\n"
            f"Troubleshooting step to generate: {step} of 2{outage_note}"
        )

        response = bedrock.converse(
            modelId=MODEL_ID,
            system=[{"text": _TROUBLESHOOT_PROMPT}],
            messages=[{"role": "user", "content": [{"text": user_msg}]}],
            inferenceConfig={"maxTokens": 250, "temperature": 0.3},
        )

        return response["output"]["message"]["content"][0]["text"].strip()

    except Exception:
        # Fallback hardcoded steps if AI fails
        if step == 1:
            outage_prefix = f"⚠️ Note: {isp_name} may have a network issue in your area right now.\n\n" if outage_status not in ("OPERATIONAL", "UNKNOWN", "NOREPORTS", None) else ""
            return (
                f"{outage_prefix}"
                "Let's start with a full reboot:\n\n"
                "*1.* Unplug your ONT (fibre box) → wait 30 sec → plug back in → wait 2 min\n"
                "*2.* Then reboot your router → wait 1 min\n"
                "*3.* Test your connection\n\n"
                "Did that fix it? Reply *yes* or *no*"
            )
        else:
            return (
                "Check the lights on your ONT (fibre box):\n\n"
                "• *PWR* — solid green ✅\n"
                "• *LOS* — must be OFF. If red/blinking = signal problem on ISP side 🔴\n"
                "• *PON/GPON* — solid green = connected ✅\n\n"
                "Also check all cables are firmly plugged in.\n\n"
                "Did that fix it? Reply *yes* or *no*"
            )


def ask(question: str, client_name: str = "Dear client") -> dict:
    """
    Ask Nova Micro a customer question.

    Returns:
        {
            "answered": bool,      # True = AI answered, False = escalate to Leonard
            "reply": str,          # The reply to send to customer (if answered)
            "reason": str,         # Why we escalated (if not answered)
        }
    """
    # Immediate escalation check
    if _should_escalate_immediately(question):
        return {
            "answered": False,
            "reply": "",
            "reason": "sensitive_keyword",
        }

    try:
        bedrock = _get_bedrock_client()

        user_msg = f"Customer name: {client_name}\nCustomer message: {question}"

        response = bedrock.converse(
            modelId=MODEL_ID,
            system=[{"text": SYSTEM_PROMPT}],
            messages=[{"role": "user", "content": [{"text": user_msg}]}],
            inferenceConfig={
                "maxTokens": 300,
                "temperature": 0.4,
            },
        )

        reply = response["output"]["message"]["content"][0]["text"].strip()

        # If the model itself decided to escalate
        if reply.strip().upper() == "ESCALATE" or reply.startswith("ESCALATE"):
            return {
                "answered": False,
                "reply": "",
                "reason": "ai_escalated",
            }

        return {
            "answered": True,
            "reply": reply,
            "reason": "",
        }

    except ClientError as e:
        return {
            "answered": False,
            "reply": "",
            "reason": f"bedrock_error: {e.response['Error']['Code']}",
        }
    except Exception as e:
        return {
            "answered": False,
            "reply": "",
            "reason": f"error: {str(e)}",
        }
