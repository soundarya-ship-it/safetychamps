"""
Pulls the entire NHP National Hospital Directory from data.gov.in
into data/nhp_hospitals.csv.

Uses curl via subprocess — Python `requests` against this endpoint is
flaky (SSL/timeout quirks on data.gov.in); curl is reliable.

Usage:  DATA_GOV_KEY=xxx python scripts/fetch_nhp.py
"""
import os, csv, sys, time, json, subprocess

API   = "https://api.data.gov.in/resource/98fa254e-c5f8-4910-a19b-4828939b477d"
KEY   = os.environ.get("DATA_GOV_KEY") or sys.exit("Set DATA_GOV_KEY env var")
PAGE  = 300
OUT   = "data/nhp_hospitals.csv"
MAX_RETRIES = 5

FIELDS = [
    "_sr_no", "hospital_name", "_hospital_care_type",
    "_discipline_systems_of_medicine", "_address_original_first_line",
    "state", "district", "_subdistrict", "_pincode",
    "telephone", "mobile_number", "emergency_num",
    "_ambulance_phone_no", "_bloodbank_phone_no",
    "_location_coordinates", "_emergency_services",
    "_total_num_beds", "specialties", "facilities",
]


def fetch_page(offset, page_size):
    url = (f"{API}?api-key={KEY}&format=json"
           f"&offset={offset}&limit={page_size}")
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            proc = subprocess.run(
                ["curl", "-s", "--max-time", "60", url],
                capture_output=True, text=True, check=True,
            )
            return json.loads(proc.stdout)
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            wait = 2 ** attempt
            print(f"  ! attempt {attempt}/{MAX_RETRIES} failed "
                  f"({type(e).__name__}); retry in {wait}s")
            time.sleep(wait)
    raise RuntimeError(f"Gave up on offset={offset} after {MAX_RETRIES} retries")


def main():
    os.makedirs("data", exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()

        offset, total_written = 0, 0
        while True:
            data = fetch_page(offset, PAGE)
            batch = data.get("records", [])
            if not batch:
                break
            for row in batch:
                w.writerow(row)
            f.flush()
            total_written += len(batch)
            total = data.get("total", "?")
            print(f"  fetched {total_written:>6} / {total}")
            if len(batch) < PAGE:
                break
            offset += PAGE
            time.sleep(0.3)

    print(f"\nSaved {total_written} hospitals -> {OUT}")


if __name__ == "__main__":
    main()
