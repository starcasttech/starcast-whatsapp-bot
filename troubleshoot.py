"""
Deterministic technical support troubleshooting for Starcast WhatsApp bot.
Provider-specific ONT knowledge for South African fibre networks.

Sources: Afrihost, Axxess, Mweb, Openserve, Octotel, home-connect.co.za

ONT brands by provider:
  Octotel    → Dasan ZNID series
  Openserve  → Huawei HG8145/8245/8240  OR  Nokia G-240/G-010
  Vumatel    → Raycore (aerial) OR CTC (trench)
  Frogfoot   → Calix
  MetroFibre → Calix
  Zoomfibre  → varies
  MTN/Vodacom/Telkom → LTE router (no ONT)
"""

# ── ISP selection menu ────────────────────────────────────────────────────────

ISP_MENU = (
    "Which internet provider do you have?\n\n"
    "1️⃣  Octotel\n"
    "2️⃣  Openserve\n"
    "3️⃣  Frogfoot\n"
    "4️⃣  MetroFibre\n"
    "5️⃣  Vumatel\n"
    "6️⃣  Zoomfibre\n"
    "7️⃣  MTN (LTE)\n"
    "8️⃣  Vodacom (LTE)\n"
    "9️⃣  Telkom (LTE)\n"
    "🔟  Not sure\n\n"
    "Reply with a number (1-10)"
)

ISP_MAP = {
    "1": "Octotel",    "2": "Openserve",  "3": "Frogfoot",
    "4": "MetroFibre", "5": "Vumatel",    "6": "Zoomfibre",
    "7": "MTN",        "8": "Vodacom",    "9": "Telkom",
    "10": "Not sure",
}

LTE_ISPS = {"MTN", "Vodacom", "Telkom"}

# ── Reboot sequences (provider-specific wait times) ───────────────────────────

_REBOOT = {
    "Octotel": (
        "*Octotel ONT reboot:*\n\n"
        "*1.* Unplug the ONT from the wall — wait *5–10 minutes* (Octotel ONTs need a longer reset)\n"
        "*2.* Unplug the router too while you wait\n"
        "*3.* Plug the *ONT* back in first — wait *5 minutes* for the PON light to turn solid green\n"
        "*4.* Then plug the router in — wait *1 minute*\n"
        "*5.* Test your connection\n\n"
        "Reply *done* once finished."
    ),
    "Openserve": (
        "*Openserve ONT reboot:*\n\n"
        "*1.* Unplug the ONT from the wall — wait *10–20 minutes*\n"
        "*2.* Unplug the router too while you wait\n"
        "*3.* Plug the *ONT* back in first — wait *3–5 minutes* for PON light to go solid green and LOS light to stay OFF\n"
        "*4.* Then plug the router in — wait *1 minute*\n"
        "*5.* Test your connection\n\n"
        "Reply *done* once finished."
    ),
    "Frogfoot": (
        "*Frogfoot ONT reboot:*\n\n"
        "*1.* Unplug the ONT from the wall — wait *30 seconds*\n"
        "*2.* Unplug the router too\n"
        "*3.* Plug the *ONT* back in first — wait *3–5 minutes* for the BROADBAND light to turn solid green\n"
        "*4.* Then plug the router in — wait *1 minute*\n"
        "*5.* Test your connection\n\n"
        "Reply *done* once finished."
    ),
    "MetroFibre": (
        "*MetroFibre ONT reboot:*\n\n"
        "*1.* Unplug the ONT from the wall — wait *30 seconds*\n"
        "*2.* Unplug the router too\n"
        "*3.* Plug the *ONT* back in first — wait *3–5 minutes* for the BROADBAND light to turn solid green\n"
        "*4.* Then plug the router in — wait *1 minute*\n"
        "*5.* Test your connection\n\n"
        "Reply *done* once finished."
    ),
    "Vumatel": (
        "*Vumatel ONT reboot:*\n\n"
        "*1.* Unplug the ONT from the wall — wait *5 minutes*\n"
        "*2.* Unplug the router too\n"
        "*3.* Plug the *ONT* back in first — wait *3 minutes* for the signal light to come on\n"
        "*4.* Then plug the router in — wait *1 minute*\n"
        "*5.* Test your connection\n\n"
        "Reply *done* once finished."
    ),
    "default": (
        "*Full reboot sequence:*\n\n"
        "*1.* Unplug the ONT (fibre box) from the wall — wait *5 minutes*\n"
        "*2.* Unplug the router too while you wait\n"
        "*3.* Plug the *ONT* back in first — wait *3–5 minutes* for all lights to stabilise\n"
        "*4.* Then plug the router in — wait *1 minute*\n"
        "*5.* Test your connection\n\n"
        "Reply *done* once finished."
    ),
}

LTE_REBOOT = (
    "*LTE router reboot:*\n\n"
    "*1.* Switch the router off (or unplug it) — wait *30 seconds*\n"
    "*2.* Switch it back on — wait *2 minutes* for the signal to reconnect\n"
    "*3.* Test your connection\n\n"
    "Reply *done* once finished."
)


def _reboot(isp: str) -> str:
    return _REBOOT.get(isp, _REBOOT["default"])


# ── ONT light prompts (provider-specific) ────────────────────────────────────

_LIGHTS_PROMPT = {
    "Octotel": (
        "📟 *Check your Octotel ONT (Dasan box)*\n\n"
        "Your ONT has these indicator lights:\n\n"
        "• *PWR* — power (should be solid green)\n"
        "• *PON* — connection to Octotel's network (solid green = good, *red = fault*)\n"
        "• *ALM* — alarm (should be OFF — red means a line problem)\n"
        "• *INTERNET* — internet active (green or blinking)\n"
        "• *LAN* — connection to your router\n\n"
        "Tell me what you see on each light — is it *green, red, blinking, or off*?\n\n"
        "_Example: \"PWR green, PON red, ALM red, internet off\"_"
    ),
    "Openserve": (
        "📟 *Check your Openserve ONT*\n\n"
        "Openserve uses either a *Huawei* or *Nokia* ONT. Check which yours is.\n\n"
        "*Huawei ONT lights:*\n"
        "• *PWR* — power (solid green = good)\n"
        "• *PON* — network connection (solid green = good, off = no signal)\n"
        "• *LOS* — loss of signal — ⚠️ this light should be *OFF* when working. Red or blinking = fault\n"
        "• *LAN* — router connection\n"
        "• *INTERNET* — internet active\n\n"
        "*Nokia ONT lights:*\n"
        "• *POWER* — solid green = good, red = hardware fault\n"
        "• *LINK / PON* — solid green = connected, off = no fibre signal\n"
        "• *AUTH* — solid green = authorised, flashing = syncing\n"
        "• *INTERNET* — solid green = online\n\n"
        "Tell me what you see on each light.\n\n"
        "_Example: \"PWR green, LOS red, PON off\"_"
    ),
    "Frogfoot": (
        "📟 *Check your Frogfoot ONT (Calix box)*\n\n"
        "Your ONT has these indicator lights:\n\n"
        "• *POWER* — solid or flashing green = good. Red = boot failure. Amber = firmware update (wait 10 min, do not unplug)\n"
        "• *BROADBAND* — this is the key light. Solid or flashing green = connected. *Off = fibre fault*. Flashing red-then-green = unstable\n"
        "• *SERVICE* — green = internet connection active\n"
        "• *ETHERNET* — connection to your router\n\n"
        "Tell me what you see on each light.\n\n"
        "_Example: \"Power green, Broadband off, Service off\"_"
    ),
    "MetroFibre": (
        "📟 *Check your MetroFibre ONT (Calix box)*\n\n"
        "Your ONT has these indicator lights:\n\n"
        "• *POWER* — solid or flashing green = good. Red = boot failure. Amber = firmware update\n"
        "• *BROADBAND* — solid or flashing green = connected. *Off = fibre fault*. Flashing red-then-green = unstable\n"
        "• *SERVICE* — green = internet active\n"
        "• *ETHERNET* — router connection\n\n"
        "Tell me what you see on each light.\n\n"
        "_Example: \"Power green, Broadband off, Service off\"_"
    ),
    "Vumatel": (
        "📟 *Check your Vumatel ONT*\n\n"
        "Vumatel uses two different ONT types — check which you have.\n\n"
        "*Raycore ONT (blue power light):*\n"
        "• *POWER* — solid blue = good. Flashing blue = contact support. Off = no power\n"
        "• *FX* — solid orange = fibre connected. *Off or red = fibre fault*\n"
        "• *LAN1* — orange = router connected (must use LAN1, not LAN2/3/4)\n\n"
        "*CTC ONT (green power icon):*\n"
        "• *Power icon* — green = good\n"
        "• *F (Fibre)* — green = connected. *Off = line problem*\n"
        "• *1 (LAN)* — green = router connected\n\n"
        "Tell me what you see on each light.\n\n"
        "_Example: \"Power blue solid, FX off, LAN1 off\"_"
    ),
    "default": (
        "📟 *Check the lights on your ONT (fibre box)*\n\n"
        "The ONT is the small white or grey box where the fibre cable enters your home.\n\n"
        "Common lights to check:\n"
        "• *PWR / POWER* — should be solid green (good)\n"
        "• *PON / GPON / BROADBAND / FX / F* — the network connection light. Should be solid green or orange\n"
        "• *LOS* — should be *OFF* (red or blinking = bad)\n"
        "• *LAN / ETH* — your router connection\n"
        "• *INTERNET / SVC* — internet status\n\n"
        "Tell me what you see on each light — is it *green, red, blinking, or off*?\n\n"
        "_Example: \"PWR green, PON off, LOS red\"_"
    ),
}


def get_lights_prompt(isp_name: str, is_lte: bool = False) -> str:
    if is_lte:
        return (
            "📶 *Check your LTE router*\n\n"
            "Tell me what you see — which lights are *on, off, red, or blinking*?\n\n"
            "Also, how many signal bars or dots does it show?\n\n"
            "_Example: \"Power on, internet light red, 1 bar\"_"
        )
    return _LIGHTS_PROMPT.get(isp_name, _LIGHTS_PROMPT["default"])


# ── Light interpretation — provider-aware ────────────────────────────────────

def interpret_lights(description: str, isp_name: str = "") -> str:
    """
    Interpret ONT light description, provider-aware.
    Returns WhatsApp-ready diagnosis + reboot steps.
    """
    d = description.lower()

    # ── No power ─────────────────────────────────────────────────────────────
    no_power = (
        any(x in d for x in ["no lights", "all off", "nothing", "no power", "dead",
                               "blank", "dark", "not on"])
        and not any(x in d for x in ["red", "blink", "orange", "amber"])
    )
    if no_power:
        return (
            "⚫ *No lights — the ONT has no power.*\n\n"
            "• Check the power cable is firmly plugged into the ONT and the wall socket\n"
            "• Try a different wall socket or extension cord\n"
            "• If connected to a UPS (battery backup), try plugging directly into the wall — the UPS battery may be flat\n"
            "• Look for a small power button on the side of the ONT and press it\n\n"
            "Once it powers on, reply *done* and describe what lights you see."
        )

    # ══ OCTOTEL (Dasan) — PON + ALM lights ═══════════════════════════════════
    if isp_name == "Octotel":
        # PON red or ALM red = fibre fault
        pon_red = "pon" in d and any(x in d for x in ["red", "amber", "orange"])
        alm_red = "alm" in d and any(x in d for x in ["red", "on"])
        if pon_red or alm_red:
            return (
                "🔴 *PON/ALM light is red — fibre fault on the Octotel network side.*\n\n"
                "This means the ONT cannot connect to Octotel's network. It is usually caused by:\n"
                "• A problem on Octotel's network in your area\n"
                "• A loose or damaged fibre cable between the street connection point and your ONT\n\n"
                "First, check the *thin fibre patch cable* plugged into the back of your ONT:\n"
                "• Is it clicked in firmly at both ends?\n"
                "• Is it bent, kinked, or pinched under furniture?\n\n"
                "Then try the reboot:\n\n"
                + _reboot("Octotel")
                + "\n\nIf the PON/ALM is *still red* after the reboot, the fault is on Octotel's side and needs to be logged. Reply *no* and we will take it from there."
            )
        # Internet off but PON green
        internet_off = any(x in d for x in ["internet off", "internet red", "svc off"]) and ("pon" not in d or "green" in d)
        if internet_off:
            return (
                "🟡 *PON is fine but no internet session* — this is usually an authentication or provisioning issue.\n\n"
                + _reboot("Octotel")
                + "\n\nIf the internet light is *still off* after the reboot, reply *no* and we will log a fault."
            )

    # ══ OPENSERVE (Huawei or Nokia) ═══════════════════════════════════════════
    elif isp_name == "Openserve":
        # Huawei: LOS red/blinking is BAD (LOS = off is good)
        los_bad = "los" in d and any(x in d for x in ["red", "blink", "amber", "orange", "flash", "on"])
        if los_bad:
            return (
                "🔴 *LOS light is red/blinking — no fibre signal coming into your home.*\n\n"
                "On your Huawei ONT, the LOS light should always be *OFF* when everything is working. "
                "Red or blinking means the ONT is not receiving a signal from Openserve's network.\n\n"
                "This is usually caused by:\n"
                "• A loose or damaged fibre patch cable (the thin cable from the wall box to the ONT)\n"
                "• A fibre break or fault outside your home on Openserve's network\n\n"
                "Check the *thin fibre cable* plugged into the ONT:\n"
                "• Is the green/blue connector clicked firmly into the port?\n"
                "• Is the cable bent sharply, pinched, or running under furniture?\n"
                "• ⚠️ Do NOT look into the end of the cable — it emits laser light\n\n"
                + _reboot("Openserve")
                + "\n\nIf LOS is *still red* after the reboot, the fault is outside your home and needs to be logged with Openserve. Reply *no* and we will take it from there."
            )
        # Nokia: LINK or PON off
        link_off = (
            any(x in d for x in ["link off", "pon off", "link not on", "pon not on"])
            or ("nokia" in d and "off" in d)
        )
        if link_off:
            return (
                "🟠 *LINK/PON light is off — no fibre signal.*\n\n"
                "On your Nokia ONT, LINK off means the ONT is not receiving a signal from Openserve.\n\n"
                "Check the fibre patch cable connections, then try the reboot:\n\n"
                + _reboot("Openserve")
                + "\n\nIf LINK is still off after the reboot, reply *no* and we will log the fault."
            )
        # Nokia: POWER red = hardware fault
        if "power" in d and "red" in d and "nokia" in d:
            return (
                "🔴 *POWER light is red — the Nokia ONT has a hardware failure.*\n\n"
                "This usually means the device itself needs to be replaced.\n\n"
                "Try a full factory reset first: hold the *RESET* button (pinhole on the back) "
                "for 10–15 seconds using a pin or paperclip.\n\n"
                "If it still shows red power after reset, the ONT needs replacement. "
                "Reply *no* and we will log the fault."
            )
        # PON off (Huawei)
        pon_off = "pon" in d and any(x in d for x in ["off", "not on", "no light"])
        if pon_off:
            return (
                "🟠 *PON light is off — the ONT is not connecting to Openserve's exchange.*\n\n"
                "• Check the *fibre patch cable* is clicked firmly into the back of the ONT\n"
                "• Check the other end at the wall socket or outdoor connection box\n\n"
                + _reboot("Openserve")
                + "\n\nIf PON stays off, reply *no* and we will log the fault."
            )

    # ══ FROGFOOT / METROFIBRE (Calix) ═════════════════════════════════════════
    elif isp_name in ("Frogfoot", "MetroFibre"):
        # BROADBAND off = fibre fault
        bb_off = "broadband" in d and any(x in d for x in ["off", "not on", "out"])
        bb_unstable = "broadband" in d and ("blink" in d or ("red" in d and "green" in d))
        if bb_off:
            return (
                f"🔴 *BROADBAND light is off — fibre fault on the {isp_name} network side.*\n\n"
                "The BROADBAND light being off means the ONT cannot detect the fibre signal. This is usually:\n"
                "• A loose fibre patch cable at the ONT or wall connection\n"
                f"• A fault on {isp_name}'s network in your area\n\n"
                "Check the fibre cable connections, then reboot:\n\n"
                + _reboot(isp_name)
                + "\n\nIf BROADBAND is *still off* after the reboot, reply *no* and we will log the fault."
            )
        if bb_unstable:
            return (
                "🟡 *BROADBAND light is flashing red-then-green — unstable fibre connection.*\n\n"
                "This means the fibre signal is present but weak or dropping.\n\n"
                "• Check the fibre patch cable for any bends or kinks\n"
                "• Make sure both ends of the cable are firmly connected\n\n"
                + _reboot(isp_name)
                + "\n\nIf it keeps flashing after the reboot, reply *no* and we will log the fault."
            )
        # POWER amber = firmware update in progress
        if "power" in d and "amber" in d:
            return (
                "🟡 *POWER light is amber — the ONT is doing a firmware update.*\n\n"
                "⚠️ *Do NOT unplug it* — this takes 5–10 minutes.\n\n"
                "Wait for it to complete and the light will return to green. "
                "Reply *done* once the amber light is gone and we will check if internet is back."
            )

    # ══ VUMATEL (Raycore or CTC) ══════════════════════════════════════════════
    elif isp_name == "Vumatel":
        # Raycore: FX off or red = fault
        fx_fault = "fx" in d and any(x in d for x in ["off", "red", "not on", "out"])
        if fx_fault:
            return (
                "🔴 *FX light is off/red — fibre fault on the Vumatel side.*\n\n"
                "The FX light (orange when working) shows the fibre signal. Off or red means there is no signal.\n\n"
                "Check the fibre cable at the back of the ONT, then reboot:\n\n"
                + _reboot("Vumatel")
                + "\n\nIf FX stays off/red, reply *no* and we will log the fault."
            )
        # Raycore: POWER flashing = hardware issue
        if "power" in d and "blink" in d and "blue" in d:
            return (
                "🔴 *POWER light is flashing blue — the Raycore ONT has a hardware problem.*\n\n"
                "A solid blue is normal. Flashing means the device needs attention.\n\n"
                "Try unplugging for 5 minutes and powering back on. "
                "If it still flashes, reply *no* and we will arrange a replacement."
            )
        # CTC: F light off = fault
        f_off = (
            (" f " in f" {d} " or d.startswith("f ") or d.endswith(" f"))
            and any(x in d for x in ["off", "not on", "out"])
        )
        if f_off:
            return (
                "🔴 *F (Fibre) light is off — fibre line problem.*\n\n"
                "Check the fibre cable connections, then reboot:\n\n"
                + _reboot("Vumatel")
                + "\n\nIf the F light stays off, reply *no* and we will log the fault."
            )
        # Raycore: must use LAN1
        if "lan" in d and any(x in d for x in ["2", "3", "4"]) and "no internet" in d:
            return (
                "⚠️ *Check your LAN cable connection.*\n\n"
                "On the Raycore ONT, the router *must be plugged into LAN1* — not LAN2, LAN3 or LAN4.\n\n"
                "Move the cable to *LAN1* and test again. Reply *done* when done."
            )

    # ══ UNIVERSAL FALLBACKS ════════════════════════════════════════════════════

    # LOS red/blinking (generic — Huawei terminology used by various ISPs)
    los_bad = (
        "los" in d and any(x in d for x in ["red", "blink", "amber", "orange", "flash", "on"])
    )
    if los_bad:
        isp_ref = f"*{isp_name}*" if isp_name else "your fibre provider"
        return (
            f"🔴 *LOS light is red/blinking — no fibre signal.*\n\n"
            "The LOS light should always be OFF when everything is working. "
            f"Red or blinking means the ONT is not receiving a signal from {isp_ref}.\n\n"
            "Check the fibre patch cable at the back of the ONT — make sure it is clicked in firmly "
            "and not bent or damaged.\n\n"
            + _reboot(isp_name)
            + "\n\nIf LOS is *still on* after the reboot, reply *no* and we will log the fault."
        )

    # PON/GPON off (generic)
    pon_off = (
        any(x in d for x in ["pon", "gpon"])
        and any(x in d for x in ["off", "not on", "no light", "out", "dark"])
    )
    if pon_off:
        return (
            "🟠 *PON/GPON light is off — not connecting to the network.*\n\n"
            "• Check the *fibre patch cable* is firmly clicked into the ONT and the wall box\n"
            "• Make sure the cable is not bent, kinked, or running under anything heavy\n\n"
            + _reboot(isp_name)
            + "\n\nIf PON stays off, reply *no* and we will log the fault."
        )

    # Internet/service light bad (but PON is fine)
    internet_bad = (
        any(x in d for x in ["internet", "svc", "service", "wan"])
        and any(x in d for x in ["red", "off", "blink"])
        and "los" not in d
        and "pon" not in d
    )
    if internet_bad:
        isp_ref = f"*{isp_name}*" if isp_name else "your ISP"
        return (
            f"🔴 *Internet light is off/red — fibre signal is present but no internet session.*\n\n"
            f"This usually means an authentication or provisioning issue between the ONT and {isp_ref}.\n\n"
            + _reboot(isp_name)
            + "\n\nIf the internet light is *still off* after the reboot, reply *no* and we will log the fault."
        )

    # All lights green / looks normal
    looks_fine = (
        any(x in d for x in ["all green", "all on", "looks fine", "looks normal",
                               "everything green", "all lights on", "normal", "fine", "all ok"])
        and "red" not in d and "blink" not in d
    ) or (
        "green" in d and d.count("green") >= 2
        and "red" not in d and "blink" not in d and "off" not in d
    )
    if looks_fine:
        return (
            "✅ *ONT lights look normal — fibre signal is present.*\n\n"
            "The problem is likely your *router*, or there is a temporary session issue.\n\n"
            + _reboot(isp_name)
            + "\n\nIf internet is still down after the reboot, reply *no* and we will log the fault."
        )

    # Default — not enough detail, do the reboot anyway
    return (
        "Let us start with a full reboot — this clears most connection faults:\n\n"
        + _reboot(isp_name)
        + "\n\nIf you are still offline after the reboot, reply *no* and describe what lights you see. We will log a fault."
    )


def interpret_lte_lights(description: str, isp_name: str = "") -> str:
    """Interpret LTE router lights/signal description."""
    d = description.lower()
    isp_ref = f"*{isp_name}*" if isp_name else "your mobile network"

    if any(x in d for x in ["no signal", "0 bar", "zero bar", "no bar", "no service", "no network"]):
        return (
            f"📵 *No LTE signal — the router cannot find {isp_ref}.*\n\n"
            "• Check that the SIM card is firmly seated (power off the router first)\n"
            "• Move the router to a window or a higher position — LTE signal can be blocked by walls\n"
            f"• Check if your {isp_ref} SIM is active and your data bundle is not expired\n\n"
            + LTE_REBOOT
            + "\n\nIf still no signal, reply *no* and we will log the fault."
        )

    if any(x in d for x in ["red", "blink", "offline", "error"]) and "internet" in d:
        return (
            f"🔴 *Internet light is red/blinking — could be a {isp_ref} network issue or SIM problem.*\n\n"
            + LTE_REBOOT
            + "\n\nIf still offline, reply *no* and we will log the fault."
        )

    if any(x in d for x in ["1 bar", "one bar", "weak signal", "poor signal"]):
        return (
            "📶 *Weak LTE signal — only 1 bar.*\n\n"
            "• Try moving the router to a window, or mount it higher on a wall\n"
            "• Avoid placing it near other electronics (TV, microwave, other routers)\n\n"
            + LTE_REBOOT
            + "\n\nIf speed is still very slow after moving it, reply *no* and we will log the fault."
        )

    return (
        "Let us reboot the router first — this clears most LTE issues:\n\n"
        + LTE_REBOOT
        + "\n\nIf you are still offline after the reboot, reply *no* and we will log the fault."
    )


def format_outage_note(outage_result: dict) -> str:
    """Return a brief outage warning or empty string if all clear."""
    if not outage_result:
        return ""
    status = outage_result.get("status", "UNKNOWN")
    isp    = outage_result.get("isp", "")
    if status in ("OPERATIONAL", "UNKNOWN", "NOREPORTS", None):
        return ""
    label = {
        "MAJOROUTAGE":         "a *major outage*",
        "PARTIALOUTAGE":       "a *partial outage*",
        "DEGRADEDPERFORMANCE": "*degraded performance*",
        "UNDERMAINTENANCE":    "*scheduled maintenance*",
        "POSSIBLEOUTAGE":      "*possible issues reported*",
    }.get(status, "a network issue")
    return (
        f"⚠️ *Heads up: {isp} is currently showing {label} in some areas.*\n"
        "This may be the cause of your problem. Let us check your equipment anyway.\n\n"
    )
