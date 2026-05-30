"""
Dumps the contacts table of roadsos.db to two places:

  1. static/contacts.json    — compact JSON dump (for any external use)
  2. static/emergency.html   — INLINE inside a <script> block as
                                window.__CONTACTS_DATA__, so the offline
                                page works without fetching from
                                /app/static/contacts.json (which is not
                                reliably served on Streamlit Cloud).

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
import re

DB_PATH  = os.environ.get("ROADSOS_DB", "roadsos.db")
OUT_PATH = "static/contacts.json"
HTML_PATH = "static/emergency.html"

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

    payload = {
        "generated_from": DB_PATH,
        "contact_count":  len(contacts),
        "schema":         FIELDS,
        "contacts":       contacts,
    }

    os.makedirs("static", exist_ok=True)

    # 1. Write the plain JSON file
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        # No indent — saves ~300 KB; not human-edited
        json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
    size_kb = os.path.getsize(OUT_PATH) / 1024
    print(f"[export] wrote {len(contacts):,} contacts -> {OUT_PATH} "
          f"({size_kb:.0f} KB)")

    # 2. Inject the same payload into emergency.html so the page works
    #    without fetching contacts.json (Streamlit Cloud doesn't reliably
    #    serve files from static/, so external fetches return the React
    #    shell instead of the JSON).
    if os.path.exists(HTML_PATH):
        with open(HTML_PATH, "r", encoding="utf-8") as f:
            html = f.read()

        # Use a stable script tag we can find on subsequent runs
        marker = "<!-- __ROADSOS_CONTACTS_INLINE__ -->"
        block = (
            marker + "\n"
            "<script>window.__CONTACTS_DATA__ = "
            + json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
            + ";</script>"
        )

        if marker in html:
            # Replace existing block (everything from marker to end of <script>)
            html = re.sub(
                r"<!-- __ROADSOS_CONTACTS_INLINE__ -->\n?<script>.*?</script>",
                block,
                html,
                count=1,
                flags=re.DOTALL,
            )
            print(f"[export] replaced inline data block in {HTML_PATH}")
        else:
            # First run — insert before the main <script> at the bottom
            html = html.replace(
                "<script>\n// ════════════════════════════════════════════════════════════════════════════\n// State",
                block + "\n<script>\n// ════════════════════════════════════════════════════════════════════════════\n// State",
                1,
            )
            print(f"[export] inserted inline data block in {HTML_PATH}")

        with open(HTML_PATH, "w", encoding="utf-8") as f:
            f.write(html)
        size_kb = os.path.getsize(HTML_PATH) / 1024
        print(f"[export] {HTML_PATH} is now {size_kb:.0f} KB "
              f"(includes embedded contacts data)")
    else:
        print(f"[export] {HTML_PATH} not found — skipping inline injection")


if __name__ == "__main__":
    main()
