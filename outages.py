"""
Live ISP outage checker for South African providers.

Primary sources (free JSON, no auth):
  - status.octotel.co.za  → Octotel (direct, region-level detail)
  - status.atomic.co.za   → Frogfoot, Openserve, Vumatel
  - netnotice.rsaweb.co.za → MetroFibre, Frogfoot, Openserve

Fallback (Brave Search) for: Zoomfibre, MTN, Vodacom, Telkom
"""

import os
import time
import requests
from datetime import datetime, timezone, timedelta

SAST = timezone(timedelta(hours=2))  # South Africa Standard Time

BRAVE_KEY = os.environ.get("BRAVE_KEY", "")

# ── Source endpoints ───────────────────────────────────────────────────────

ATOMIC  = "https://status.atomic.co.za"
RSAWEB  = "https://netnotice.rsaweb.co.za"
OCTOTEL = "https://status.octotel.co.za"

# Which sources carry which ISP (lowercase match against component names)
ISP_SOURCES = {
    "octotel":    [OCTOTEL],        # Use Octotel's own page (region-level detail)
    "openserve":  [ATOMIC, RSAWEB],
    "frogfoot":   [ATOMIC, RSAWEB],
    "metrofibre": [RSAWEB],
    "vumatel":    [ATOMIC],
    "vuma":       [ATOMIC],
}

# ISPs we fall back to Brave Search for
BRAVE_ISPS = {"zoomfibre", "mtn", "vodacom", "telkom"}

# ── Simple in-memory cache (2-minute TTL per source) ──────────────────────

_cache = {}   # key → (timestamp, data)
_TTL   = 120  # seconds

def _get_cached(key, fetch_fn):
    now = time.time()
    if key in _cache and now - _cache[key][0] < _TTL:
        return _cache[key][1]
    data = fetch_fn()
    _cache[key] = (now, data)
    return data

# ── Data fetchers ─────────────────────────────────────────────────────────

def _fetch_components(base_url):
    try:
        r = requests.get(f"{base_url}/components.json", timeout=5)
        r.raise_for_status()
        return r.json().get("components", [])
    except Exception:
        return []

def _fetch_summary(base_url):
    try:
        r = requests.get(f"{base_url}/summary.json", timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception:
        return {}

def _get_components(base_url):
    return _get_cached(f"comp:{base_url}", lambda: _fetch_components(base_url))

def _get_summary(base_url):
    return _get_cached(f"summ:{base_url}", lambda: _fetch_summary(base_url))

# ── Status logic ──────────────────────────────────────────────────────────

_STATUS_RANK = {
    "MAJOROUTAGE":        4,
    "PARTIALOUTAGE":      3,
    "DEGRADEDPERFORMANCE":2,
    "UNDERMAINTENANCE":   1,
    "OPERATIONAL":        0,
}

_STATUS_EMOJI = {
    "MAJOROUTAGE":        "🔴",
    "PARTIALOUTAGE":      "🟠",
    "DEGRADEDPERFORMANCE":"⚠️",
    "UNDERMAINTENANCE":   "🔧",
    "OPERATIONAL":        "✅",
}

def _worst(statuses):
    """Return the most severe status from a list."""
    ranked = [(s, _STATUS_RANK.get(s.upper(), -1)) for s in statuses]
    ranked.sort(key=lambda x: x[1], reverse=True)
    return ranked[0][0].upper() if ranked else "UNKNOWN"


def check_isp(isp_name: str) -> dict:
    """
    Returns:
        {
            "isp": str,
            "status": str,          # OPERATIONAL / UNDERMAINTENANCE / etc.
            "incidents": [str],
            "maintenances": [str],
            "source": str,          # "live" | "search" | "unknown"
        }
    """
    key = isp_name.lower().strip()
    sources = ISP_SOURCES.get(key)

    if sources:
        component_statuses = []
        incidents     = []
        maintenances  = []

        seen_ids = set()
        for base in sources:
            components = _get_components(base)
            # Octotel's own page: every component is an Octotel region — match all
            # Other sources: match by ISP name in component name
            direct = (base == OCTOTEL and key == "octotel")
            for comp in components:
                name_match = direct or key in comp.get("name", "").lower()
                if name_match:
                    status_val = comp.get("status", "UNKNOWN")
                    # For direct pages, only count non-group (leaf) components
                    is_group = comp.get("group") is None and any(
                        c.get("group", {}) and c["group"].get("id") == comp.get("id")
                        for c in components
                    )
                    if not is_group:
                        component_statuses.append(status_val)
                    # Extract embedded incidents/maintenances
                    for inc in comp.get("activeIncidents", []):
                        if inc.get("id") not in seen_ids:
                            seen_ids.add(inc.get("id"))
                            incidents.append(_clean_event(inc, isp_name))
                    for maint in comp.get("activeMaintenances", []):
                        if maint.get("id") not in seen_ids:
                            seen_ids.add(maint.get("id"))
                            maintenances.append(_clean_event(maint, isp_name))

        # Pull from the source's summary.json (catches events not embedded in components)
        for base in sources:
            summary = _get_summary(base)
            for m in summary.get("activeMaintenances", []):
                if (key in m.get("name", "").lower() or base == OCTOTEL) and m.get("id") not in seen_ids:
                    seen_ids.add(m.get("id"))
                    maintenances.append(_clean_event(m, isp_name))
            for i in summary.get("activeIncidents", []):
                if (key in i.get("name", "").lower() or base == OCTOTEL) and i.get("id") not in seen_ids:
                    seen_ids.add(i.get("id"))
                    incidents.append(_clean_event(i, isp_name))

        status = _worst(component_statuses) if component_statuses else "UNKNOWN"

        return {
            "isp":          isp_name,
            "status":       status,
            "incidents":    incidents,
            "maintenances": maintenances,
            "source":       "live",
        }

    elif key in BRAVE_ISPS:
        return _brave_search_status(isp_name)

    else:
        return {
            "isp":         isp_name,
            "status":      "UNKNOWN",
            "incidents":   [],
            "maintenances":[],
            "source":      "unknown",
        }


def _brave_search_status(isp_name: str) -> dict:
    """Fallback: search for recent outage reports via Brave."""
    try:
        r = requests.get(
            "https://api.search.brave.com/res/v1/web/search",
            params={"q": f"{isp_name} outage South Africa", "count": 3, "freshness": "pd"},
            headers={"X-Subscription-Token": BRAVE_KEY, "Accept": "application/json"},
            timeout=5
        )
        results = r.json().get("web", {}).get("results", [])
        keywords = ["outage", "down", "offline", "not working", "issues"]
        hits = [res for res in results
                if any(k in (res.get("title","") + res.get("description","")).lower()
                       for k in keywords)]
        status = "POSSIBLEOUTAGE" if hits else "NOREPORTS"
        notes  = [res.get("title", "") for res in hits[:2]]
        return {
            "isp":          isp_name,
            "status":       status,
            "incidents":    notes,
            "maintenances": [],
            "source":       "search",
        }
    except Exception:
        return {
            "isp":          isp_name,
            "status":       "UNKNOWN",
            "incidents":    [],
            "maintenances": [],
            "source":       "search",
        }


def _clean_event(event: dict, isp_name: str) -> dict:
    """Strip third-party ISP prefixes from event names (e.g. 'RSAWEB Network Notice | ')."""
    import re
    event = dict(event)
    name = event.get("name", "")
    # Remove patterns like "RSAWEB Network Notice | " or "RSAWEB ... | "
    name = re.sub(r'^RSAWEB[^|]*\|\s*', '', name).strip()
    # Remove "Octotel - " prefix if ISP name is already shown in header
    name = re.sub(r'^Octotel\s*[-–]\s*', '', name, flags=re.IGNORECASE).strip()
    event["name"] = name
    return event


def _format_event(event) -> str:
    """Format a maintenance/incident dict with name, date, time, duration."""
    if isinstance(event, str):
        return f"  • {event}"
    name     = event.get("name", "Unknown")
    start_str= event.get("start", "") or event.get("started", "")
    duration = event.get("duration")   # minutes
    status   = event.get("status", "")

    lines = [f"  • *{name}*"]

    if start_str:
        try:
            dt = datetime.fromisoformat(start_str.replace("Z", "+00:00")).astimezone(SAST)
            lines.append(f"    📅 {dt.strftime('%d %b %Y')}  🕐 {dt.strftime('%H:%M')} SAST")
        except Exception:
            pass

    if duration:
        hrs, mins = divmod(int(duration), 60)
        dur_str = f"{hrs}h" if hrs and not mins else f"{hrs}h {mins}m" if hrs else f"{mins}m"
        lines.append(f"    ⏱ Duration: {dur_str}")

    if status == "INPROGRESS":
        lines.append("    🔴 In progress now")
    elif status == "NOTSTARTEDYET":
        lines.append("    🟡 Not started yet")

    return "\n".join(lines)


def format_status(result: dict) -> str:
    """Format an outage check result as a WhatsApp message."""
    isp    = result["isp"]
    status = result["status"]
    source = result["source"]

    if source == "unknown":
        return (
            f"❓ *{isp}*\n\n"
            "We don't have a live status feed for this provider yet.\n"
            "Check downdetector.co.za or contact your ISP directly.\n\n"
            "Type *hi* to return to the menu."
        )

    if source == "search":
        if status == "POSSIBLEOUTAGE":
            lines = [f"⚠️ *{isp}* — Possible issues reported in the last 24 hours\n"]
            for note in result["incidents"]:
                lines.append(f"  • {note}")
            lines.append("\nFor confirmed status, check downdetector.co.za")
        else:
            lines = [f"✅ *{isp}* — No outage reports found in the last 24 hours"]
        lines.append("\nType *hi* to return to the menu.")
        return "\n".join(lines)

    # Live source
    emoji = _STATUS_EMOJI.get(status, "❓")
    status_label = {
        "OPERATIONAL":        "All systems operational",
        "UNDERMAINTENANCE":   "Scheduled maintenance in progress",
        "DEGRADEDPERFORMANCE":"Degraded performance",
        "PARTIALOUTAGE":      "Partial outage",
        "MAJOROUTAGE":        "Major outage",
        "UNKNOWN":            "Status unknown",
    }.get(status, status)

    lines = [f"{emoji} *{isp}* — {status_label}\n"]

    if result["incidents"]:
        lines.append("🚨 *Active incidents:*")
        for i in result["incidents"]:
            lines.append(_format_event(i))
        lines.append("")

    if result["maintenances"]:
        lines.append("🔧 *Scheduled maintenance:*")
        for m in result["maintenances"]:
            lines.append(_format_event(m))
        lines.append("")

    if status == "OPERATIONAL" and not result["incidents"] and not result["maintenances"]:
        lines.append("No active incidents or maintenance reported.")
    elif status not in ("OPERATIONAL", "UNKNOWN") and not result["incidents"] and not result["maintenances"]:
        lines.append("⚠️ The network status feed shows an issue but no detailed incident report has been published by this provider yet.")
        lines.append("Please check back shortly or contact Starcast for assistance.")

    lines.append("\n_Source: live network status feed_")
    lines.append("Type *hi* to return to the menu.")
    return "\n".join(lines)


# ── Provider name normalisation ───────────────────────────────────────────

# Maps what a user might type → canonical name
PROVIDER_ALIASES = {
    "octotel":    "Octotel",
    "openserve":  "Openserve",
    "telkom openserve": "Openserve",
    "frogfoot":   "Frogfoot",
    "frog foot":  "Frogfoot",
    "metrofibre": "MetroFibre",
    "metro fibre":"MetroFibre",
    "metro":      "MetroFibre",
    "vumatel":    "Vumatel",
    "vuma":       "Vumatel",
    "zoomfibre":  "Zoomfibre",
    "zoom fibre": "Zoomfibre",
    "zoom":       "Zoomfibre",
    "mtn":        "MTN",
    "vodacom":    "Vodacom",
    "telkom":     "Telkom",
}

OUTAGE_MENU = (
    "📡 *Check ISP Outages*\n\n"
    "Select your provider:\n\n"
    "1️⃣  Octotel\n"
    "2️⃣  Openserve\n"
    "3️⃣  Frogfoot\n"
    "4️⃣  MetroFibre\n"
    "5️⃣  Vumatel\n"
    "6️⃣  Zoomfibre\n"
    "7️⃣  MTN\n"
    "8️⃣  Vodacom\n"
    "9️⃣  Telkom\n\n"
    "Reply with a number (1-9) or *0* to go back."
)

OUTAGE_NUMBER_MAP = {
    "1": "Octotel",
    "2": "Openserve",
    "3": "Frogfoot",
    "4": "MetroFibre",
    "5": "Vumatel",
    "6": "Zoomfibre",
    "7": "MTN",
    "8": "Vodacom",
    "9": "Telkom",
}

def resolve_provider(text: str):
    """Return canonical provider name from number or name, or None."""
    t = text.strip()
    if t in OUTAGE_NUMBER_MAP:
        return OUTAGE_NUMBER_MAP[t]
    return PROVIDER_ALIASES.get(t.lower())
