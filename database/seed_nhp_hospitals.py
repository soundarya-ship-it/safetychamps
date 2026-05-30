"""
seed_nhp_hospitals.py
─────────────────────
Seed the contacts table from data/nhp_hospitals.csv
(the official India National Hospital Directory pulled from data.gov.in).

For rows where the API has no GPS coordinates, falls back to a pincode
centroid from data/pincode_coords.json (built by
scripts/geocode_pincodes.py via Nominatim).

Categorisation:
    Tier 2, source = 'nhp_data_gov'
    Confidence 80 if 24×7 emergency flag is set, else 72.

Dedup: skip rows where a contact already exists with the same
(name, district) — same pattern as seed_districts.py.
"""

import os
import re
import csv
import json

CSV_PATH   = os.path.join(os.path.dirname(__file__), "..", "data", "nhp_hospitals.csv")
CACHE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "pincode_coords.json")

COORD_RE = re.compile(r"(-?\d+\.?\d*)\s*[, ]+\s*(-?\d+\.?\d*)")


def _real(v):
    """NHP uses '0', 'NA', 'NULL', empty string as missing-data placeholders."""
    s = (v or "").strip()
    return s if s and s.upper() not in ("0", "NULL", "NA", "N/A", "NONE") else ""


def _parse_coords(raw):
    s = _real(raw)
    if not s:
        return None, None
    m = COORD_RE.search(s)
    if not m:
        return None, None
    try:
        lat, lon = float(m.group(1)), float(m.group(2))
    except ValueError:
        return None, None
    if not (6 <= lat <= 38 and 68 <= lon <= 98):    # outside India bbox
        return None, None
    return lat, lon


def _split_numbers(raw):
    """
    Split a NHP phone field into individual numbers.
    NHP often packs 2-4 numbers into one field separated by commas, e.g.
    '03192 233665, 03192 246058, 03192 233455'. Tap-to-call and the
    phonenumbers verifier both choke on comma-lists, so we explode them here.
    """
    if not raw:
        return []
    return [p.strip() for p in str(raw).split(",") if p.strip()]


def _collect_numbers(row):
    """Return an ordered, deduped list of all real phone numbers in this row,
    preferring emergency lines first, then landline, then mobile."""
    seen, out = set(), []
    for key in ("emergency_num", "telephone", "mobile_number",
                "_ambulance_phone_no"):
        for num in _split_numbers(_real(row.get(key))):
            if num not in seen:
                seen.add(num)
                out.append(num)
    return out


def _load_pincode_cache():
    if not os.path.exists(CACHE_PATH):
        return {}
    with open(CACHE_PATH, encoding="utf-8") as f:
        return json.load(f)


def seed_nhp_hospitals(conn, csv_path=CSV_PATH):
    if not os.path.exists(csv_path):
        print(f"[NHP] {csv_path} not found — run scripts/fetch_nhp.py first")
        return 0

    pincode_cache = _load_pincode_cache()
    cur = conn.cursor()

    inserted = skipped_dup = skipped_no_phone = skipped_no_loc = 0
    used_direct = used_pincode = 0

    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            name    = _real(row.get("hospital_name"))
            numbers = _collect_numbers(row)
            if not (name and numbers):
                skipped_no_phone += 1
                continue
            phone     = numbers[0]
            phone_alt = numbers[1] if len(numbers) > 1 else None

            # Try direct coords, then pincode fallback
            lat, lon = _parse_coords(row.get("_location_coordinates"))
            if lat and lon:
                used_direct += 1
            else:
                pin = _real(row.get("_pincode"))
                cached = pincode_cache.get(pin) if pin else None
                if cached:
                    lat, lon = cached["lat"], cached["lon"]
                    used_pincode += 1
                else:
                    skipped_no_loc += 1
                    continue

            district = _real(row.get("district")) or ""
            state    = _real(row.get("state")) or ""

            # Dedup — skip if a contact with the same name in this district exists
            exists = cur.execute(
                "SELECT id FROM contacts WHERE name=? AND district=?",
                (name, district),
            ).fetchone()
            if exists:
                skipped_dup += 1
                continue

            has_24x7   = bool(_real(row.get("_emergency_services")))
            confidence = 80 if has_24x7 else 72
            address    = _real(row.get("_address_original_first_line"))

            cur.execute("""
                INSERT INTO contacts
                  (name, category, tier, phone, phone_alt, address,
                   lat, lon, state, district, country_code,
                   source, confidence, is_active)
                VALUES (?,'hospital',2,?,?,?,?,?,?,?, 'IN',
                        'nhp_data_gov', ?, 1)
            """, (name, phone, phone_alt, address,
                  lat, lon, state, district, confidence))
            inserted += 1

    conn.commit()
    print(f"[NHP] Seeded {inserted} hospitals from data.gov.in")
    print(f"       direct GPS coords      : {used_direct}")
    print(f"       pincode-backfilled     : {used_pincode}")
    print(f"       skipped (no phone)     : {skipped_no_phone}")
    print(f"       skipped (no location)  : {skipped_no_loc}")
    print(f"       skipped (duplicate)    : {skipped_dup}")
    return inserted


if __name__ == "__main__":
    import sys, sqlite3
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    DB_PATH = os.environ.get("ROADSOS_DB", "roadsos.db")
    conn = sqlite3.connect(DB_PATH)
    seed_nhp_hospitals(conn)
    conn.close()
