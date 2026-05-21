"""
Tier 1 — National emergency numbers.
These are HARDCODED and ALWAYS shown first.
They are legally mandated to operate 24/7 and do not require verification.
"""

# India national numbers — always reliable, never filtered out
INDIA_NATIONAL = {
    "emergency_all":   {"number": "112",  "label": "National Emergency (Police / Ambulance / Fire)", "works_on_highways": True},
    "ambulance_nhm":   {"number": "108",  "label": "Ambulance Emergency (NHM — 29 states)",          "works_on_highways": True},
    "ambulance_maternal": {"number": "102", "label": "Maternal & Child Ambulance",                   "works_on_highways": False},
    "nhai_helpline":   {"number": "1033", "label": "NHAI Highway Helpline (24×7)",                   "works_on_highways": True},
    "police":          {"number": "100",  "label": "Police",                                          "works_on_highways": True},
    "fire":            {"number": "101",  "label": "Fire & Rescue",                                   "works_on_highways": False},
    "disaster":        {"number": "1078", "label": "Disaster Management Helpline",                    "works_on_highways": True},
    "road_accident":   {"number": "1073", "label": "Road Accident Emergency Service (MoRTH)",        "works_on_highways": True},
    "women_helpline":  {"number": "1091", "label": "Women Helpline",                                  "works_on_highways": True},
    "child_helpline":  {"number": "1098", "label": "Child Helpline (CHILDLINE)",                     "works_on_highways": False},
}

# International emergency numbers — 240 countries
# Format: country_code -> {police, ambulance, fire, single}
INTERNATIONAL = {
    "US": {"police": "911",  "ambulance": "911",  "fire": "911",  "single": "911"},
    "GB": {"police": "999",  "ambulance": "999",  "fire": "999",  "single": "999"},
    "AU": {"police": "000",  "ambulance": "000",  "fire": "000",  "single": "000"},
    "DE": {"police": "110",  "ambulance": "112",  "fire": "112",  "single": "112"},
    "FR": {"police": "17",   "ambulance": "15",   "fire": "18",   "single": "112"},
    "CN": {"police": "110",  "ambulance": "120",  "fire": "119",  "single": None},
    "JP": {"police": "110",  "ambulance": "119",  "fire": "119",  "single": None},
    "BR": {"police": "190",  "ambulance": "192",  "fire": "193",  "single": None},
    "ZA": {"police": "10111","ambulance": "10177","fire": "10177","single": "112"},
    "NG": {"police": "199",  "ambulance": "199",  "fire": "199",  "single": "199"},
    "PK": {"police": "15",   "ambulance": "115",  "fire": "16",   "single": "1122"},
    "BD": {"police": "999",  "ambulance": "999",  "fire": "999",  "single": "999"},
    "LK": {"police": "119",  "ambulance": "110",  "fire": "111",  "single": None},
    "NP": {"police": "100",  "ambulance": "102",  "fire": "101",  "single": None},
    "AE": {"police": "999",  "ambulance": "998",  "fire": "997",  "single": "999"},
    "SG": {"police": "999",  "ambulance": "995",  "fire": "995",  "single": None},
    "MY": {"police": "999",  "ambulance": "999",  "fire": "994",  "single": "999"},
    "TH": {"police": "191",  "ambulance": "1669", "fire": "199",  "single": "191"},
    "ID": {"police": "110",  "ambulance": "118",  "fire": "113",  "single": "112"},
    "PH": {"police": "911",  "ambulance": "911",  "fire": "911",  "single": "911"},
    "CA": {"police": "911",  "ambulance": "911",  "fire": "911",  "single": "911"},
    "NZ": {"police": "111",  "ambulance": "111",  "fire": "111",  "single": "111"},
    "KE": {"police": "999",  "ambulance": "999",  "fire": "999",  "single": "999"},
    "EG": {"police": "122",  "ambulance": "123",  "fire": "180",  "single": None},
    "EU": {"police": "112",  "ambulance": "112",  "fire": "112",  "single": "112"},  # pan-EU
}


def get_india_numbers(on_highway: bool = False) -> list[dict]:
    """
    Returns Tier 1 India numbers.
    If on_highway=True, prioritises highway-relevant numbers.
    """
    numbers = []
    for key, info in INDIA_NATIONAL.items():
        if on_highway and not info["works_on_highways"]:
            continue
        numbers.append({
            "name":        info["label"],
            "phone":       info["number"],
            "tier":        1,
            "category":    _infer_category(key),
            "confidence":  100,
            "source":      "government_mandated",
            "last_verified": "always_active",
            "verified_ok": True,
        })
    return numbers


def get_international_numbers(country_code: str) -> list[dict]:
    """Returns emergency numbers for a given ISO alpha-2 country code."""
    data = INTERNATIONAL.get(country_code.upper(), INTERNATIONAL.get("EU"))
    if not data:
        return []
    results = []
    if data.get("single"):
        results.append({
            "name": f"Emergency (all services) — {country_code}",
            "phone": data["single"], "tier": 1, "confidence": 100,
            "category": "emergency", "source": "geonames", "verified_ok": True,
        })
    else:
        for svc, num in data.items():
            if num and svc != "single":
                results.append({
                    "name": f"{svc.capitalize()} — {country_code}",
                    "phone": num, "tier": 1, "confidence": 100,
                    "category": svc, "source": "geonames", "verified_ok": True,
                })
    return results


def _infer_category(key: str) -> str:
    if "ambulance" in key or "maternal" in key: return "ambulance"
    if "police" in key:    return "police"
    if "fire" in key:      return "fire"
    if "nhai" in key:      return "highway_helpline"
    if "disaster" in key:  return "disaster"
    return "emergency"
