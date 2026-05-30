"""
Geocode every distinct pincode found in data/nhp_hospitals.csv that
has a phone but no valid GPS. Writes a pincode -> (lat, lon) cache to
data/pincode_coords.json.

Uses curl via subprocess (Python requests is flaky against some hosts
on this machine — same issue we hit with data.gov.in).

Nominatim policy:
  * Max 1 request per second
  * User-Agent must identify the app
  https://operations.osmfoundation.org/policies/nominatim/

Re-running this script is safe — existing cache entries are skipped.

Usage:  python scripts/geocode_pincodes.py
"""
import os, csv, re, json, time, subprocess, sys

CSV_PATH   = "data/nhp_hospitals.csv"
CACHE_PATH = "data/pincode_coords.json"
USER_AGENT = "RoadSoS/1.0 (https://safetychamps.streamlit.app)"
SLEEP_SEC  = 1.1

COORD_RE = re.compile(r"(-?\d+\.?\d*)\s*[, ]+\s*(-?\d+\.?\d*)")


def real(v):
    s = (v or "").strip()
    return s if s and s.upper() not in ("0", "NULL", "NA", "N/A", "NONE") else ""


def has_valid_coords(row):
    raw = real(row.get("_location_coordinates"))
    if not raw:
        return False
    m = COORD_RE.search(raw)
    if not m:
        return False
    try:
        lat, lon = float(m.group(1)), float(m.group(2))
        return 6 <= lat <= 38 and 68 <= lon <= 98
    except ValueError:
        return False


def has_phone(row):
    return any(real(row.get(k)) for k in
               ("telephone", "mobile_number", "emergency_num"))


def collect_target_pincodes():
    """Pincodes from rows that have phone + pincode but no valid GPS."""
    with open(CSV_PATH, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    targets = set()
    for r in rows:
        if has_phone(r) and not has_valid_coords(r):
            pc = real(r.get("_pincode"))
            if pc and pc.isdigit() and len(pc) == 6:
                targets.add(pc)
    return sorted(targets)


def load_cache():
    if not os.path.exists(CACHE_PATH):
        return {}
    with open(CACHE_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_cache(cache):
    """Atomic write so a Ctrl-C doesn't corrupt the cache."""
    tmp = CACHE_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, sort_keys=True)
    os.replace(tmp, CACHE_PATH)


def geocode_pincode(pincode):
    """Return {'lat': float, 'lon': float} or None."""
    url = ("https://nominatim.openstreetmap.org/search"
           f"?q={pincode}%2C+India&format=json&countrycodes=in&limit=1")
    try:
        proc = subprocess.run(
            ["curl", "-s", "--max-time", "30",
             "-H", f"User-Agent: {USER_AGENT}", url],
            capture_output=True, text=True, check=True,
        )
        data = json.loads(proc.stdout)
        if not data:
            return None
        r = data[0]
        return {"lat": float(r["lat"]), "lon": float(r["lon"])}
    except (subprocess.CalledProcessError, json.JSONDecodeError,
            KeyError, ValueError):
        return None


def main():
    targets = collect_target_pincodes()
    cache = load_cache()
    todo = [p for p in targets if p not in cache]

    print(f"Target pincodes total : {len(targets):,}")
    print(f"Already cached        : {len(targets) - len(todo):,}")
    print(f"To geocode now        : {len(todo):,}")
    print(f"Estimated time        : ~{len(todo) * SLEEP_SEC / 60:.1f} minutes\n")

    if not todo:
        print("Nothing to do — cache is complete.")
        return

    hit = miss = 0
    for i, pincode in enumerate(todo, 1):
        result = geocode_pincode(pincode)
        if result:
            cache[pincode] = result
            hit += 1
            tag = f"OK  {result['lat']:.4f}, {result['lon']:.4f}"
        else:
            cache[pincode] = None      # remember the miss so we don't retry
            miss += 1
            tag = "MISS"

        print(f"  [{i:>4}/{len(todo)}] {pincode}  {tag}")

        # Save every 25 lookups so a crash loses at most ~30s of progress
        if i % 25 == 0:
            save_cache(cache)

        time.sleep(SLEEP_SEC)

    save_cache(cache)
    print(f"\nDone. Hits: {hit}  Misses: {miss}  Cache: {CACHE_PATH}")


if __name__ == "__main__":
    main()
