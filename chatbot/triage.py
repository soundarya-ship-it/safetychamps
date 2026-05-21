"""
Golden Hour Score + Severity Triage.
These are the two innovation features that make RoadSoS stand out.
"""

import math


# Road speed assumptions for ETA calculation (km/h)
SPEED_HIGHWAY = 80
SPEED_CITY    = 30
SPEED_RURAL   = 50

# Golden hour thresholds (minutes)
GREEN_MAX  = 15
AMBER_MAX  = 30
RED_CUTOFF = 30  # >30 min = critical risk


def compute_golden_hour_score(
    nearest_hospital_km: float,
    on_highway: bool = False,
    is_rural: bool = False,
) -> dict:
    """
    Computes estimated arrival time for the nearest hospital
    and rates the golden hour situation.
    """
    speed = SPEED_HIGHWAY if on_highway else (SPEED_RURAL if is_rural else SPEED_CITY)
    eta_min = round((nearest_hospital_km / speed) * 60)

    if eta_min <= GREEN_MAX:
        status = "green"
        icon   = "🟢"
        msg    = f"Help can arrive in ~{eta_min} min. Golden hour is safe."
        advice = "Stay calm. Call 108/112 and wait for ambulance."
    elif eta_min <= AMBER_MAX:
        status = "amber"
        icon   = "🟡"
        msg    = f"Estimated arrival: ~{eta_min} min. Act quickly."
        advice = "Call 108 immediately. Start first aid if trained. Don't move spinal injuries."
    else:
        status = "red"
        icon   = "🔴"
        msg    = f"⚠️ {eta_min} min to nearest hospital — outside golden hour window."
        advice = "CALL 112 NOW. If safe, begin transport towards nearest hospital. Every minute counts."

    return {
        "eta_min":            eta_min,
        "status":             status,
        "icon":               icon,
        "msg":                msg,
        "advice":             advice,
        "nearest_km":         nearest_hospital_km,
        "speed_assumption":   speed,
    }


def triage_severity(description: str, urgency: str, services_needed: list) -> dict:
    """
    Given the NLU output, determines which emergency to call FIRST.
    Returns an ordered call list with reasoning.
    """
    call_order = []

    # Life-threatening: ambulance first, always
    if urgency == "critical":
        call_order = [
            {"service": "112",  "label": "National Emergency",   "reason": "Single call gets police + ambulance + fire", "priority": 1},
            {"service": "108",  "label": "Ambulance (NHM)",      "reason": "Dedicated ambulance dispatch",               "priority": 2},
            {"service": "100",  "label": "Police",               "reason": "For traffic management and FIR",             "priority": 3},
        ]
        advice = "Call 112 FIRST — one call dispatches everything."

    elif urgency == "high" and "ambulance" in services_needed:
        call_order = [
            {"service": "108",  "label": "Ambulance (108)",      "reason": "Fastest medical response",     "priority": 1},
            {"service": "112",  "label": "National Emergency",   "reason": "If 108 is busy or not available", "priority": 2},
            {"service": "100",  "label": "Police",               "reason": "File accident report",         "priority": 3},
        ]
        advice = "Call 108 for the ambulance first — medical help is the priority."

    elif "towing" in services_needed or "puncture" in services_needed:
        call_order = [
            {"service": "1033", "label": "NHAI Helpline",        "reason": "For breakdown on National Highway",    "priority": 1},
            {"service": "local_towing", "label": "Nearest towing service", "reason": "Private tow truck",         "priority": 2},
        ]
        advice = "Call 1033 (NHAI) if on a National Highway — they dispatch roadside assistance."

    else:
        call_order = [
            {"service": "112",  "label": "National Emergency",   "reason": "When in doubt, 112 handles everything", "priority": 1},
        ]
        advice = "When unsure, always call 112 first."

    # Check if on highway — add NHAI
    desc_lower = description.lower() if description else ""
    if any(w in desc_lower for w in ["highway", "nh", "national highway", "expressway"]):
        call_order.insert(1, {
            "service": "1033", "label": "NHAI Highway Helpline",
            "reason": "Fastest response on National Highways", "priority": 1.5
        })

    return {
        "call_order": call_order,
        "primary_advice": advice,
        "urgency": urgency,
    }
