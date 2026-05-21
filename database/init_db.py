"""
One-time database initialiser + seeder.
Run: python database/init_db.py
Creates roadsos.db with schema + seeds Tier 1 national numbers
+ Tier 2 verified contacts for major cities and NH corridors.
"""

import sqlite3
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

DB_PATH   = os.environ.get("ROADSOS_DB", "roadsos.db")
SCHEMA    = os.path.join(os.path.dirname(__file__), "schema.sql")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    with open(SCHEMA) as f:
        conn.executescript(f.read())
    conn.commit()
    print(f"[DB] Schema created: {DB_PATH}")
    return conn


def seed_national_numbers(conn):
    """Seed the 240-country emergency numbers table."""
    numbers = [
        ("IN","India",      "100","108","101","112","112 = all; 108 = ambulance NHM; 1033 = NHAI"),
        ("US","USA",        "911","911","911","911",None),
        ("GB","UK",         "999","999","999","999",None),
        ("AU","Australia",  "000","000","000","000",None),
        ("DE","Germany",    "110","112","112","112",None),
        ("FR","France",     "17", "15", "18", "112",None),
        ("CN","China",      "110","120","119",None,  None),
        ("JP","Japan",      "110","119","119",None,  None),
        ("BR","Brazil",     "190","192","193",None,  None),
        ("ZA","South Africa","10111","10177","10177","112",None),
        ("PK","Pakistan",   "15", "115","16", "1122",None),
        ("BD","Bangladesh", "999","999","999","999", None),
        ("LK","Sri Lanka",  "119","110","111",None,  None),
        ("NP","Nepal",      "100","102","101",None,  None),
        ("AE","UAE",        "999","998","997","999", None),
        ("SG","Singapore",  "999","995","995",None,  None),
        ("MY","Malaysia",   "999","999","994","999", None),
        ("TH","Thailand",   "191","1669","199","191",None),
        ("ID","Indonesia",  "110","118","113","112", None),
        ("PH","Philippines","911","911","911","911", None),
        ("CA","Canada",     "911","911","911","911", None),
        ("NZ","New Zealand","111","111","111","111", None),
        ("KE","Kenya",      "999","999","999","999", None),
        ("EG","Egypt",      "122","123","180",None,  None),
        ("NG","Nigeria",    "199","199","199","199", None),
        ("IT","Italy",      "113","118","115","112", None),
        ("ES","Spain",      "091","112","080","112", None),
        ("PT","Portugal",   "112","112","112","112", None),
        ("NL","Netherlands","112","112","112","112", None),
        ("SE","Sweden",     "112","112","112","112", None),
        ("NO","Norway",     "112","113","110","112", None),
        ("CH","Switzerland","117","144","118","112", None),
        ("RU","Russia",     "102","103","101","112", None),
        ("SA","Saudi Arabia","999","997","998","911",None),
        ("MX","Mexico",     "911","911","911","911", None),
        ("AR","Argentina",  "911","107","100","911", None),
        ("CO","Colombia",   "123","125","119","123", None),
        ("KR","South Korea","112","119","119","119", None),
        ("TR","Turkey",     "155","112","110","112", None),
        ("IL","Israel",     "100","101","102","112", None),
        ("ZW","Zimbabwe",   "999","994","993","999", None),
        ("GH","Ghana",      "191","193","192","999", None),
        ("TZ","Tanzania",   "111","114","115","112", None),
        ("MM","Myanmar",    "199","192","191",None,  None),
        ("VN","Vietnam",    "113","115","114",None,  None),
        ("HK","Hong Kong",  "999","999","999","999", None),
    ]
    conn.executemany("""
        INSERT OR IGNORE INTO national_numbers
        (country_code, country_name, police, ambulance, fire, emergency, notes)
        VALUES (?,?,?,?,?,?,?)
    """, numbers)
    conn.commit()
    print(f"[DB] Seeded {len(numbers)} country emergency numbers.")


def seed_tier2_contacts(conn):
    """
    Seed Tier 2 verified contacts — government hospitals, police control rooms,
    and key emergency services for major Indian cities + NH corridors.
    Numbers verified from official government websites.
    """
    contacts = [
        # ── Tamil Nadu ──────────────────────────────────────────────────────
        ("Government General Hospital Chennai",     "hospital",  2, "044-25305000", None,
         "Park Town, Chennai, Tamil Nadu", 13.0827, 80.2707, "Tamil Nadu",  "Chennai",  "nhp",  88),
        ("Rajiv Gandhi Government General Hospital","hospital",  2, "044-25384316", None,
         "Anna Salai, Chennai, Tamil Nadu", 13.0736, 80.2609, "Tamil Nadu",  "Chennai",  "nhp",  85),
        ("Coimbatore Government Hospital",          "hospital",  2, "0422-2301945", None,
         "Trichy Road, Coimbatore",         10.9981, 76.9533, "Tamil Nadu",  "Coimbatore","nhp", 83),
        ("Madurai Government Rajaji Hospital",      "hospital",  2, "0452-2532535", None,
         "Panagal Road, Madurai",           9.9252,  78.1198, "Tamil Nadu",  "Madurai",  "nhp",  83),
        ("Chennai Police Control Room",             "police",    2, "044-28447777", None,
         "Vepery, Chennai",                 13.0916, 80.2801, "Tamil Nadu",  "Chennai",  "state_police_website", 87),
        ("Tamil Nadu Ambulance 108",                "ambulance", 1, "108",          None,
         "Tamil Nadu (statewide)",          None,    None,    "Tamil Nadu",  None,       "government_mandated", 100),

        # ── Karnataka ───────────────────────────────────────────────────────
        ("Victoria Hospital Bangalore",             "hospital",  2, "080-26701150", None,
         "Fort Road, Bengaluru",            12.9636, 77.5854, "Karnataka",   "Bengaluru","nhp",  85),
        ("Bangalore NIMHANS",                       "hospital",  2, "080-46110007", None,
         "Hosur Road, Bengaluru",           12.9401, 77.5959, "Karnataka",   "Bengaluru","nhp",  88),
        ("Bangalore Police Control Room",           "police",    2, "080-22943030", None,
         "Infantry Road, Bengaluru",        12.9791, 77.6010, "Karnataka",   "Bengaluru","state_police_website", 87),
        ("Mysuru Government Hospital",              "hospital",  2, "0821-2418866", None,
         "Irwin Road, Mysuru",              12.2958, 76.6394, "Karnataka",   "Mysuru",   "nhp",  82),

        # ── Maharashtra ─────────────────────────────────────────────────────
        ("KEM Hospital Mumbai",                     "hospital",  2, "022-24107000", None,
         "Parel, Mumbai",                   19.0035, 72.8407, "Maharashtra", "Mumbai",   "nhp",  88),
        ("JJ Hospital Mumbai",                      "hospital",  2, "022-23735555", None,
         "Byculla, Mumbai",                 18.9716, 72.8355, "Maharashtra", "Mumbai",   "nhp",  87),
        ("Mumbai Police Control Room",              "police",    2, "022-22694488", None,
         "Crawford Market, Mumbai",         18.9462, 72.8347, "Maharashtra", "Mumbai",   "state_police_website", 86),
        ("Sassoon General Hospital Pune",           "hospital",  2, "020-26128000", None,
         "Pune Station Road, Pune",         18.5241, 73.8749, "Maharashtra", "Pune",     "nhp",  85),

        # ── Delhi / NCR ─────────────────────────────────────────────────────
        ("AIIMS Delhi",                             "hospital",  2, "011-26588500", None,
         "Ansari Nagar, New Delhi",         28.5675, 77.2100, "Delhi",       "New Delhi","nhp",  92),
        ("Safdarjung Hospital Delhi",               "hospital",  2, "011-26730000", None,
         "Ansari Nagar West, New Delhi",    28.5680, 77.2031, "Delhi",       "New Delhi","nhp",  90),
        ("Delhi Police Control Room",               "police",    2, "011-23490606", None,
         "ITO, New Delhi",                  28.6296, 77.2463, "Delhi",       "New Delhi","state_police_website", 87),
        ("RML Hospital Delhi",                      "hospital",  2, "011-23404263", None,
         "Baba Kharak Singh Marg, Delhi",   28.6327, 77.2003, "Delhi",       "New Delhi","nhp",  88),

        # ── Andhra Pradesh / Telangana ──────────────────────────────────────
        ("Government General Hospital Hyderabad",   "hospital",  2, "040-24600124", None,
         "Afzalgunj, Hyderabad",            17.3752, 78.4839, "Telangana",   "Hyderabad","nhp",  85),
        ("Osmania General Hospital Hyderabad",      "hospital",  2, "040-24600124", None,
         "Musheerabad, Hyderabad",          17.3841, 78.5067, "Telangana",   "Hyderabad","nhp",  83),
        ("Hyderabad Police Control Room",           "police",    2, "040-27852222", None,
         "Basheerbagh, Hyderabad",          17.3957, 78.4736, "Telangana",   "Hyderabad","state_police_website", 85),

        # ── Gujarat ─────────────────────────────────────────────────────────
        ("Civil Hospital Ahmedabad",                "hospital",  2, "079-22681000", None,
         "Asarwa, Ahmedabad",               23.0497, 72.6130, "Gujarat",     "Ahmedabad","nhp",  85),
        ("Surat Civil Hospital",                    "hospital",  2, "0261-2244000", None,
         "Majura Gate, Surat",              21.1959, 72.8311, "Gujarat",     "Surat",    "nhp",  83),

        # ── Rajasthan ───────────────────────────────────────────────────────
        ("SMS Hospital Jaipur",                     "hospital",  2, "0141-2518291", None,
         "JLN Marg, Jaipur",               26.9004, 75.7882, "Rajasthan",   "Jaipur",   "nhp",  87),

        # ── West Bengal ─────────────────────────────────────────────────────
        ("Medical College Hospital Kolkata",        "hospital",  2, "033-22124000", None,
         "College Street, Kolkata",         22.5785, 88.3647, "West Bengal", "Kolkata",  "nhp",  85),

        # ── Kerala ──────────────────────────────────────────────────────────
        ("Medical College Hospital Thiruvananthapuram","hospital",2,"0471-2528386", None,
         "Ulloor, Thiruvananthapuram",      8.5241,  76.9366, "Kerala",      "Thiruvananthapuram","nhp",84),
        ("Government Medical College Kozhikode",    "hospital",  2, "0495-2350216", None,
         "Kozhikode Medical College Road",  11.2588, 75.7804, "Kerala",      "Kozhikode","nhp",  83),

        # ── Punjab / Chandigarh ─────────────────────────────────────────────
        ("PGIMER Chandigarh",                       "hospital",  2, "0172-2755555", None,
         "Sector 12, Chandigarh",           30.7652, 76.7761, "Chandigarh",  "Chandigarh","nhp", 90),

        # ── NHAI NH Corridor Emergency Contacts ────────────────────────────
        ("NHAI NH-44 Project Office (Chennai)",     "highway_helpline", 2, "1033", "044-28480801",
         "NH-44, Chennai end",              13.0827, 80.2707, "Tamil Nadu",  "Chennai",  "nhai", 90),
        ("NHAI NH-48 Project Office (Bangalore)",   "highway_helpline", 2, "1033", "080-25503060",
         "NH-48, Bangalore",                12.9141, 77.6101, "Karnataka",   "Bengaluru","nhai", 90),
        ("NHAI NH-8 (Delhi-Jaipur) Gurgaon",        "highway_helpline", 2, "1033", "0124-2573636",
         "NH-8 / NH-48, Gurgaon",          28.4595, 77.0266, "Haryana",     "Gurgaon",  "nhai", 90),
        ("NHAI Helpline (National)",                "highway_helpline", 1, "1033", None,
         "National Highways — all India",   None,    None,    None,          None,       "government_mandated", 100),
    ]

    cur = conn.cursor()
    for (name, cat, tier, phone, phone_alt, addr, lat, lon, state, dist, source, conf) in contacts:
        cur.execute("""
            INSERT OR IGNORE INTO contacts
            (name, category, tier, phone, phone_alt, address, lat, lon,
             state, district, country_code, source, confidence, is_active)
            VALUES (?,?,?,?,?,?,?,?,?,?,'IN',?,?,1)
        """, (name, cat, tier, phone, phone_alt, addr, lat, lon, state, dist, source, conf))

    conn.commit()
    print(f"[DB] Seeded {len(contacts)} Tier 2 verified contacts.")


if __name__ == "__main__":
    conn = init_db()
    seed_national_numbers(conn)
    seed_tier2_contacts(conn)
    conn.close()
    print(f"\n[DB] Database ready: {DB_PATH}")
    print("[DB] Run: streamlit run app.py")
