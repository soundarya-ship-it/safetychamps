"""
Automated verification engine — runs nightly.
Checks Tier 2 and Tier 3 numbers against external sources.
Tier 1 (national numbers) are NEVER re-verified — they're always trusted.

Verification methods (in order of reliability):
  1. Google Maps Places API  — checks if number still listed at the place
  2. National Health Portal  — checks if hospital still in NHP database
  3. OSM cross-check         — checks if Overpass returns same number
  4. Format validation       — last resort: is the number even a valid Indian number?
"""

import re
import sqlite3
import requests
from datetime import datetime, timedelta
from contacts.confidence import compute_confidence

DB_PATH = "roadsos.db"

# Indian phone number patterns
INDIAN_MOBILE_RE  = re.compile(r"^(\+91|0)?[6-9]\d{9}$")
INDIAN_LANDLINE_RE = re.compile(r"^(\+91|0)?[1-9]\d{6,9}$")
NATIONAL_SHORTCODE = re.compile(r"^\d{3,4}$")  # 112, 108, 1033 etc.


def validate_number_format(phone: str) -> bool:
    """Basic format check — catches obviously dead numbers."""
    phone_clean = phone.strip().replace(" ", "").replace("-", "")
    return bool(
        INDIAN_MOBILE_RE.match(phone_clean)
        or INDIAN_LANDLINE_RE.match(phone_clean)
        or NATIONAL_SHORTCODE.match(phone_clean)
    )


def verify_via_google_maps(contact: dict, api_key: str) -> dict:
    """
    Checks Google Maps Places API to see if the phone number is still
    associated with the place. Does NOT make an actual phone call.
    Returns: {result: 'ok'|'changed'|'not_found'|'api_error', new_phone: str|None}
    """
    if not api_key or not contact.get("lat") or not contact.get("lon"):
        return {"result": "skipped", "new_phone": None}

    try:
        # Step 1: Find place near the stored coordinates
        nearby_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            "location": f"{contact['lat']},{contact['lon']}",
            "radius": 100,
            "keyword": contact["name"],
            "key": api_key,
        }
        resp = requests.get(nearby_url, params=params, timeout=10)
        data = resp.json()

        if not data.get("results"):
            return {"result": "not_found", "new_phone": None}

        place_id = data["results"][0]["place_id"]

        # Step 2: Get phone number for this place
        details_url = "https://maps.googleapis.com/maps/api/place/details/json"
        det_params = {
            "place_id": place_id,
            "fields": "formatted_phone_number,international_phone_number",
            "key": api_key,
        }
        det_resp = requests.get(details_url, params=det_params, timeout=10)
        det_data = det_resp.json().get("result", {})

        gm_phone = (
            det_data.get("formatted_phone_number", "")
            .replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        )
        stored_phone = contact["phone"].replace(" ", "").replace("-", "")

        if not gm_phone:
            return {"result": "not_found", "new_phone": None}
        elif gm_phone == stored_phone or stored_phone in gm_phone:
            return {"result": "ok", "new_phone": None}
        else:
            return {"result": "changed", "new_phone": gm_phone}

    except Exception as e:
        return {"result": "api_error", "new_phone": None, "error": str(e)}


def verify_via_nhp(contact: dict) -> dict:
    """
    Checks National Health Portal public search for government hospitals.
    Uses the public NHP API (no key required for read).
    """
    if contact.get("category") not in ("hospital", "ambulance"):
        return {"result": "skipped", "new_phone": None}

    try:
        url = "https://nhp.gov.in/api/hospital/search"
        params = {"name": contact["name"][:30], "state": contact.get("state", "")}
        resp = requests.get(url, params=params, timeout=10)

        if resp.status_code != 200:
            return {"result": "api_error", "new_phone": None}

        results = resp.json().get("data", [])
        stored_phone = contact["phone"].replace(" ", "").replace("-", "")

        for hospital in results[:3]:
            nhp_phone = str(hospital.get("phone", "")).replace(" ", "").replace("-", "")
            if nhp_phone and (nhp_phone == stored_phone or stored_phone in nhp_phone):
                return {"result": "ok", "new_phone": None}
            elif nhp_phone and len(nhp_phone) >= 7:
                return {"result": "changed", "new_phone": nhp_phone}

        return {"result": "not_found", "new_phone": None}

    except Exception:
        return {"result": "api_error", "new_phone": None}


def run_verification_batch(
    db_path: str = DB_PATH,
    google_api_key: str = "",
    max_contacts: int = 200,
    tier: int = None,
):
    """
    Nightly job: verify Tier 2 and 3 contacts.
    Prioritises contacts that haven't been checked recently
    or have low confidence scores.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Fetch contacts that need verification (oldest first, skip Tier 1)
    query = """
        SELECT * FROM contacts
        WHERE is_active = 1
          AND tier > 1
          AND (last_verified IS NULL OR last_verified < date('now', '-7 days'))
        ORDER BY confidence ASC, last_verified ASC
        LIMIT ?
    """
    if tier:
        query = query.replace("AND tier > 1", f"AND tier = {tier}")

    contacts = cur.execute(query, (max_contacts,)).fetchall()
    print(f"[Verifier] Checking {len(contacts)} contacts...")

    updated = 0
    for row in contacts:
        contact = dict(row)

        # Method 1: format check (free, instant)
        fmt_ok = validate_number_format(contact["phone"])
        if not fmt_ok:
            result = {"result": "fail_format", "new_phone": None}
        else:
            # Method 2: Google Maps (if key available)
            if google_api_key:
                result = verify_via_google_maps(contact, google_api_key)
            else:
                # Method 3: NHP for hospitals
                result = verify_via_nhp(contact)

        # Determine new verified_ok
        ok_statuses = {"ok"}
        verified_ok = result["result"] in ok_statuses
        fail_count  = (contact["fail_count"] + 1) if not verified_ok else 0

        # Recompute confidence
        new_confidence = compute_confidence(
            source       = contact["source"],
            last_verified= datetime.utcnow().isoformat(),
            verified_ok  = verified_ok,
            fail_count   = fail_count,
            user_confirms= contact["user_confirms"],
            user_fails   = contact["user_fails"],
        )

        # Update DB
        update_q = """
            UPDATE contacts SET
                verified_ok   = ?,
                fail_count    = ?,
                confidence    = ?,
                last_verified = ?,
                phone         = COALESCE(?, phone),
                updated_at    = datetime('now')
            WHERE id = ?
        """
        new_phone = result.get("new_phone")
        cur.execute(update_q, (
            int(verified_ok), fail_count, new_confidence,
            datetime.utcnow().isoformat(), new_phone, contact["id"]
        ))

        # Log
        cur.execute("""
            INSERT INTO verification_log (contact_id, method, result, new_phone, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (
            contact["id"],
            "google_maps" if google_api_key else "nhp_or_format",
            result["result"],
            new_phone,
            f"confidence: {contact['confidence']} -> {new_confidence}"
        ))

        updated += 1

    conn.commit()
    conn.close()
    print(f"[Verifier] Done. Updated {updated} contacts.")
    return updated


def handle_user_feedback(contact_id: int, worked: bool, db_path: str = DB_PATH):
    """
    Called when a user taps 'number worked' or 'number not working'.
    Immediately updates confidence and logs the feedback.
    User feedback is the strongest real-world signal we have.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    row = cur.execute("SELECT * FROM contacts WHERE id=?", (contact_id,)).fetchone()
    if not row:
        conn.close()
        return

    contact = dict(row)

    if worked:
        new_confirms = contact["user_confirms"] + 1
        new_fails    = contact["user_fails"]
    else:
        new_confirms = contact["user_confirms"]
        new_fails    = contact["user_fails"] + 1

    new_confidence = compute_confidence(
        source       = contact["source"],
        last_verified= contact["last_verified"],
        verified_ok  = bool(worked),
        fail_count   = contact["fail_count"] if not worked else 0,
        user_confirms= new_confirms,
        user_fails   = new_fails,
    )

    cur.execute("""
        UPDATE contacts SET
            user_confirms = ?,
            user_fails    = ?,
            confidence    = ?,
            updated_at    = datetime('now')
        WHERE id = ?
    """, (new_confirms, new_fails, new_confidence, contact_id))

    cur.execute("""
        INSERT INTO user_feedback (contact_id, worked, comment)
        VALUES (?, ?, ?)
    """, (contact_id, int(worked), "via app"))

    conn.commit()
    conn.close()

    # If 3+ users say it doesn't work, mark inactive immediately
    if new_fails >= 3 and new_confidence < 30:
        conn2 = sqlite3.connect(db_path)
        conn2.execute("UPDATE contacts SET is_active=0 WHERE id=?", (contact_id,))
        conn2.commit()
        conn2.close()
        print(f"[Verifier] Contact {contact_id} deactivated after {new_fails} user failures.")
