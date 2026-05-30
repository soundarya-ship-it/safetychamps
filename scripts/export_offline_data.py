"""
Dumps the contacts table of roadsos.db to a compact JSON file at
static/contacts.json — embedded into emergency.html at load time so the
offline page can find nearby hospitals without any server round-trip.

Trims each row to only the fields the offline page needs (name, phone,
phone_alt, lat, lon, category, tier, confidence, state, district). Drops
inactive rows. Sorts by tier then confidence so the highest-quality
contacts are scanned first.

Usage:  python scripts/export_offline_data.py
"""
import os
import sys
import json
import sqlite3

DB_PATH  = os.environ.get("ROADSOS_DB", "roadsos.db")
OUT_PATH = "static/contacts.json"

# Fields the offline emergency page actually uses
FIELDS = [
    "id", "name", "phone", "phone_alt", "category",
    "tier", "confidence", "lat", "lon", "state", "district",
]


def main():
    if not os.path.exists(DB_PATH):
        sys.exit(f"[export] DB not found at {DB_PATH} — run init_db first")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(f"""
        SELECT {', '.join(FIELDS)}
          FROM contacts
         WHERE is_active = 1
           AND phone IS NOT NULL
           AND lat IS NOT NULL
           AND lon IS NOT NULL
         ORDER BY tier ASC, confidence DESC
    """).fetchall()

    # Tier 1 numbers without coords (national shortcodes) also belong in the
    # offline page so they always render at the top.
    tier1_no_coord = conn.execute(f"""
        SELECT {', '.join(FIELDS)}
          FROM contacts
         WHERE is_active = 1
           AND tier = 1
           AND (lat IS NULL OR lon IS NULL)
    """).fetchall()

    conn.close()

    contacts = [dict(r) for r in tier1_no_coord] + [dict(r) for r in rows]

    os.makedirs("static", exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        # No indent — saves ~300 KB; the file isn't meant to be human-edited
        json.dump({
            "generated_from": DB_PATH,
            "contact_count":  len(contacts),
            "schema":         FIELDS,
            "contacts":       contacts,
        }, f, ensure_ascii=False, separators=(",", ":"))

    size_kb = os.path.getsize(OUT_PATH) / 1024
    print(f"[export] wrote {len(contacts):,} contacts -> {OUT_PATH} "
          f"({size_kb:.0f} KB)")


if __name__ == "__main__":
    main()
