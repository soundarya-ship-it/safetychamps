"""
Number verification for RoadSoS contacts.
Uses Google's phonenumbers (libphonenumber) library -- offline, free, never breaks.

Validates:
  - Indian emergency short codes (112, 108, 1033, etc.) -> "Gov. Emergency Service"
  - Toll-free numbers (1800...) -> "Toll-Free Verified"
  - 10-digit mobile/landline numbers -> carrier + region info
  - International numbers -> format check

Run standalone:  python database/verify_numbers.py
Or called from init_db.py automatically after seeding.
"""

import sqlite3
import os
from datetime import date

try:
    import phonenumbers
    from phonenumbers import carrier, geocoder, PhoneNumberType, NumberParseException
    PHONENUMBERS_AVAILABLE = True
except ImportError:
    PHONENUMBERS_AVAILABLE = False

# ── Indian government short codes (cannot be looked up via phonenumbers) ──────
INDIAN_SHORT_CODES = {
    "112":       ("All Emergency",          "National Emergency - MHA"),
    "100":       ("Police",                 "National Emergency"),
    "101":       ("Fire Service",           "National Emergency"),
    "102":       ("Ambulance",              "State Government"),
    "108":       ("Emergency Ambulance",    "NHM / GVK EMRI"),
    "109":       ("Missing Persons",        "State Government"),
    "1033":      ("NHAI Highway Helpline",  "NHAI"),
    "1073":      ("Road Accident Relief",   "MoRTH"),
    "104":       ("Medical Advice Helpline","NHM"),
    "1800116117":("Ambulance Toll-Free",    "NHM"),
    "181":       ("Women Helpline",         "State Government"),
    "1091":      ("Women Helpline",         "National Commission for Women"),
    "1098":      ("Child Helpline",         "CHILDLINE India"),
    "14567":     ("Senior Citizen Helpline","Government of India"),
    "1800111363":("NHAI Toll-Free",         "NHAI"),
}


def verify_number(phone, country_code="IN"):
    """
    Validate a single phone number.

    Returns a dict:
      valid          : True / False / None (unknown)
      type           : short_code | toll_free | mobile | landline | invalid | unknown
      type_label     : human-readable type string
      carrier_name   : telecom carrier (empty string if unknown)
      region         : geographic region from phonenumbers
      confidence_boost: integer to add to base tier confidence (-20 to +40)
      badge          : "emergency" | "verified" | "toll_free" | "invalid" | "unverified"
      badge_label    : short string shown in UI
    """
    if not PHONENUMBERS_AVAILABLE:
        return {
            "valid": None, "type": "unknown", "type_label": "Unverified",
            "carrier_name": "", "region": "",
            "confidence_boost": 0,
            "badge": "unverified", "badge_label": "Unverified"
        }

    # Normalise: strip spaces, dashes, parentheses
    clean = phone.strip()
    for ch in (" ", "-", "(", ")", "."):
        clean = clean.replace(ch, "")

    # ── 1. Indian short codes ─────────────────────────────────────────────────
    if clean in INDIAN_SHORT_CODES:
        service_name, authority = INDIAN_SHORT_CODES[clean]
        return {
            "valid": True,
            "type": "short_code",
            "type_label": "Emergency Short Code",
            "carrier_name": authority,
            "region": "India (National)",
            "confidence_boost": 40,
            "badge": "emergency",
            "badge_label": "Gov. Emergency Service"
        }

    # ── 2. Toll-free pattern (starts with 1800, length 10-12) ────────────────
    if clean.startswith("1800") and 10 <= len(clean) <= 12:
        return {
            "valid": True,
            "type": "toll_free",
            "type_label": "Toll-Free",
            "carrier_name": "Toll-Free (India)",
            "region": "India",
            "confidence_boost": 20,
            "badge": "toll_free",
            "badge_label": "Toll-Free Verified"
        }

    # ── 3. Full number via phonenumbers ───────────────────────────────────────
    try:
        if clean.startswith("+"):
            parsed = phonenumbers.parse(clean, None)
        elif country_code == "IN" and len(clean) == 10:
            parsed = phonenumbers.parse("+91" + clean, None)
        elif country_code == "IN" and clean.startswith("0") and len(clean) <= 12:
            # STD code + number (e.g. 044-12345678)
            parsed = phonenumbers.parse("+91" + clean.lstrip("0"), None)
        else:
            parsed = phonenumbers.parse(clean, country_code)

        if not phonenumbers.is_valid_number(parsed):
            return {
                "valid": False, "type": "invalid", "type_label": "Invalid Number",
                "carrier_name": "", "region": "",
                "confidence_boost": -20,
                "badge": "invalid", "badge_label": "Invalid Format"
            }

        num_type = phonenumbers.number_type(parsed)
        type_map = {
            PhoneNumberType.MOBILE:               ("mobile",           "Mobile",         15),
            PhoneNumberType.FIXED_LINE:            ("landline",         "Landline",       20),
            PhoneNumberType.FIXED_LINE_OR_MOBILE:  ("landline_mobile",  "Landline/Mobile",15),
            PhoneNumberType.TOLL_FREE:             ("toll_free",        "Toll-Free",      25),
            PhoneNumberType.PREMIUM_RATE:          ("premium",          "Premium Rate",    0),
            PhoneNumberType.SHARED_COST:           ("shared",           "Shared Cost",    10),
            PhoneNumberType.VOIP:                  ("voip",             "VoIP",            5),
            PhoneNumberType.UAN:                   ("uan",              "UAN",            15),
            PhoneNumberType.UNKNOWN:               ("unknown",          "Unknown",         0),
        }
        type_key, type_label, conf_boost = type_map.get(num_type, ("unknown", "Unknown", 0))

        try:
            carrier_name = carrier.name_for_number(parsed, "en") or ""
        except Exception:
            carrier_name = ""

        try:
            region = geocoder.description_for_number(parsed, "en") or ""
        except Exception:
            region = ""

        return {
            "valid": True,
            "type": type_key,
            "type_label": type_label,
            "carrier_name": carrier_name,
            "region": region,
            "confidence_boost": conf_boost,
            "badge": "verified",
            "badge_label": f"{type_label} ✓ Verified"
        }

    except NumberParseException:
        return {
            "valid": False, "type": "invalid", "type_label": "Cannot Parse",
            "carrier_name": "", "region": "",
            "confidence_boost": -10,
            "badge": "invalid", "badge_label": "Cannot Parse"
        }


def verify_all_contacts(db_path):
    """
    Run phonenumbers verification on every active contact in the DB.
    Updates: confidence, verified_ok, last_verified.
    Returns count of contacts updated.
    """
    if not PHONENUMBERS_AVAILABLE:
        print("[verify] phonenumbers not installed -- skipping number verification")
        print("[verify] Run:  pip install phonenumbers")
        return 0

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT id, phone, country_code, tier, confidence FROM contacts WHERE is_active=1"
    ).fetchall()

    today = date.today().isoformat()
    updated = 0

    for row in rows:
        result = verify_number(row["phone"], row["country_code"] or "IN")
        base = {1: 95, 2: 78, 3: 50}.get(int(row["tier"]), 50)
        new_conf = min(100, max(5, base + result["confidence_boost"]))
        verified_ok = 1 if result.get("valid") else 0

        conn.execute("""
            UPDATE contacts
            SET confidence = ?, verified_ok = ?, last_verified = ?, updated_at = datetime('now')
            WHERE id = ?
        """, (new_conf, verified_ok, today, row["id"]))
        updated += 1

    conn.commit()
    conn.close()
    print(f"[verify] {updated} contacts verified via phonenumbers ({today})")
    return updated


def get_badge_html(phone, country_code="IN"):
    """Return a small HTML badge string for inline display in Streamlit."""
    r = verify_number(phone, country_code)
    badge = r["badge"]
    label = r["badge_label"]
    styles = {
        "emergency": "background:#dc2626;color:#fff;padding:1px 7px;border-radius:9px;font-size:11px;font-weight:700",
        "verified":  "background:#16a34a;color:#fff;padding:1px 7px;border-radius:9px;font-size:11px",
        "toll_free": "background:#2563eb;color:#fff;padding:1px 7px;border-radius:9px;font-size:11px",
        "invalid":   "background:#dc2626;color:#fff;padding:1px 7px;border-radius:9px;font-size:11px",
        "unverified":"background:#6b7280;color:#fff;padding:1px 7px;border-radius:9px;font-size:11px",
    }
    style = styles.get(badge, styles["unverified"])
    return f'<span style="{style}">{label}</span>'


# ── Standalone run ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    db = os.path.join(os.path.dirname(__file__), "..", "roadsos.db")
    if not os.path.exists(db):
        print(f"[verify] DB not found at {db} -- run init_db.py first")
    else:
        n = verify_all_contacts(db)
        print(f"[verify] Done. {n} contacts updated.")
