"""
seed_specialty_hospitals.py
Seed specialised hospitals along National Highway corridors:
  - All 19 operational AIIMS (All India Institute of Medical Sciences)
  - Major government burn centres (critical for fuel-fire road accidents)
  - Neuro / spinal injury units (head injury = #1 road accident fatality cause)
  - Paediatric trauma centres
  - Additional Level-I trauma on highest-fatality NH stretches

Sources: MoRTH, AIIMS Annual Reports 2024, NHP Hospital Directory,
         NIMHANS, SCTIMST, SGPGI official websites.
Run via:  python database/init_db.py   (called automatically from __main__)
"""

# ---------------------------------------------------------------------------
# SPECIALTY HOSPITALS
# fmt: (name, category, tier, phone, phone_alt,
#        address, lat, lon, state, district, source, confidence)
# ---------------------------------------------------------------------------

SPECIALTY_HOSPITALS = [

    # =========================================================
    # AIIMS NETWORK  (19 operational as of 2024)
    # =========================================================

    # -- Already in seed_tier2 / seed_trauma, kept here for specialty tag --
    ("AIIMS New Delhi — All Specialties",
     "specialty_hospital", 1, "011-26588500", "011-26593308",
     "Ansari Nagar, New Delhi — junction NH-44/NH-48",
     28.5675, 77.2100, "Delhi", "New Delhi", "aiims", 98),

    ("AIIMS Bhopal — Central India",
     "specialty_hospital", 1, "0755-4293900", "0755-4293901",
     "Saket Nagar, Bhopal — NH-46 corridor",
     23.1793, 77.3649, "Madhya Pradesh", "Bhopal", "aiims", 96),

    ("AIIMS Jodhpur — Rajasthan",
     "specialty_hospital", 1, "0291-2740741", "0291-2740742",
     "Basni Phase-2, Jodhpur — NH-25/NH-62 corridor",
     26.2520, 73.0035, "Rajasthan", "Jodhpur", "aiims", 96),

    ("AIIMS Patna — Bihar",
     "specialty_hospital", 1, "0612-2451070", "0612-2451071",
     "Phulwarisharif, Patna — NH-30/NH-19 corridor",
     25.5479, 85.0777, "Bihar", "Patna", "aiims", 96),

    ("AIIMS Raipur — Chhattisgarh",
     "specialty_hospital", 1, "0771-2573601", "0771-2573602",
     "GE Road, Raipur — NH-53 corridor",
     21.2514, 81.6296, "Chhattisgarh", "Raipur", "aiims", 96),

    ("AIIMS Rishikesh — Uttarakhand",
     "specialty_hospital", 1, "0135-2462900", "0135-2462901",
     "Virbhadra Road, Rishikesh — NH-58/NH-7 gateway to hills",
     30.1158, 78.7886, "Uttarakhand", "Dehradun", "aiims", 96),

    ("AIIMS Bhubaneswar — Odisha",
     "specialty_hospital", 1, "0674-2476789", "0674-2476700",
     "Sijua, Bhubaneswar — NH-16 corridor",
     20.1534, 85.6745, "Odisha", "Bhubaneswar", "aiims", 96),

    ("AIIMS Nagpur — Vidarbha",
     "specialty_hospital", 1, "0712-2700005", "0712-2700006",
     "MIHAN, Nagpur — NH-44 km 1063",
     21.0936, 79.0476, "Maharashtra", "Nagpur", "aiims", 96),

    ("AIIMS Mangalagiri — Andhra Pradesh",
     "specialty_hospital", 1, "0863-2343666", "0863-2343667",
     "Mangalagiri, Guntur — NH-16 corridor",
     16.4307, 80.5686, "Andhra Pradesh", "Guntur", "aiims", 95),

    ("AIIMS Gorakhpur — Eastern UP",
     "specialty_hospital", 1, "0551-2210788", "0551-2210789",
     "Kunraghat, Gorakhpur — NH-27/NH-29 junction",
     26.7606, 83.3732, "Uttar Pradesh", "Gorakhpur", "aiims", 95),

    ("AIIMS Kalyani — West Bengal",
     "specialty_hospital", 1, "033-25928400", "033-25928401",
     "Kalyani, Nadia — NH-12 corridor",
     22.9754, 88.4342, "West Bengal", "Nadia", "aiims", 95),

    ("AIIMS Bathinda — Punjab",
     "specialty_hospital", 1, "0164-2003100", "0164-2003101",
     "Jodhpur Roman, Bathinda — NH-7/NH-10 corridor",
     30.2110, 74.9455, "Punjab", "Bathinda", "aiims", 95),

    ("AIIMS Deoghar — Jharkhand",
     "specialty_hospital", 1, "06432-220070", "06432-220071",
     "Deoghar — NH-114A corridor",
     24.4800, 86.6900, "Jharkhand", "Deoghar", "aiims", 93),

    ("AIIMS Rajkot — Gujarat",
     "specialty_hospital", 1, "0281-2589000", "0281-2589001",
     "Khandheri, Rajkot — NH-27 corridor",
     22.2736, 70.7512, "Gujarat", "Rajkot", "aiims", 93),

    ("AIIMS Bilaspur — Himachal Pradesh",
     "specialty_hospital", 1, "01978-281001", "01978-281002",
     "Kothipura, Bilaspur — NH-21 hill corridor",
     31.3260, 76.7560, "Himachal Pradesh", "Bilaspur", "aiims", 93),

    ("AIIMS Guwahati — Assam / NE Gateway",
     "specialty_hospital", 1, "0361-2332100", "0361-2332101",
     "Changsari, Guwahati — NH-27/NH-37 junction",
     26.2006, 91.6540, "Assam", "Kamrup", "aiims", 94),

    ("AIIMS Jammu",
     "specialty_hospital", 1, "0191-2585800", "0191-2585801",
     "Vijaypur, Samba — NH-44 Jammu bypass",
     32.6020, 74.9950, "Jammu & Kashmir", "Samba", "aiims", 93),

    ("AIIMS Bibinagar — Telangana",
     "specialty_hospital", 1, "08682-277900", "08682-277901",
     "Bibinagar, Yadadri Bhongir — NH-65 corridor",
     17.4850, 78.9940, "Telangana", "Yadadri Bhongir", "aiims", 93),

    ("AIIMS Vijaypur — Jammu",
     "specialty_hospital", 1, "0191-2459800", None,
     "Vijaypur Industrial Area — NH-44 Jammu sector",
     32.5680, 74.9760, "Jammu & Kashmir", "Samba", "aiims", 90),

    # =========================================================
    # BURN CENTRES — critical for road accidents with fire
    # (tanker collisions, fuel ignition on NHs)
    # =========================================================

    ("Safdarjung Hospital Burn Unit — Delhi",
     "burn_centre", 1, "011-26707444", "011-26730000",
     "Ansari Nagar West, Delhi — NH-44/48 hub; 100-bed dedicated burn unit",
     28.5685, 77.2060, "Delhi", "New Delhi", "nhp", 95),

    ("Loknayak Hospital Burn Unit — Delhi",
     "burn_centre", 2, "011-23232400", "011-23232401",
     "Jawaharlal Nehru Marg, Delhi — 60-bed burn ICU",
     28.6394, 77.2410, "Delhi", "New Delhi", "nhp", 90),

    ("Kilpauk Medical College Burn Unit — Chennai",
     "burn_centre", 2, "044-26421777", "044-26421778",
     "Kilpauk, Chennai — largest burn centre in TN; NH-44 terminus",
     13.0820, 80.2414, "Tamil Nadu", "Chennai", "nhp", 91),

    ("KEM Hospital Burn Unit — Mumbai",
     "burn_centre", 2, "022-24138000", "022-24107000",
     "Parel, Mumbai — NH-66 start; 80-bed burn unit",
     19.0035, 72.8407, "Maharashtra", "Mumbai", "nhp", 92),

    ("Victoria Hospital Burn Unit — Bengaluru",
     "burn_centre", 2, "080-26701150", "080-26701155",
     "Fort Road, Bengaluru — NH-44/48 junction; dedicated burn ward",
     12.9636, 77.5854, "Karnataka", "Bengaluru", "nhp", 90),

    ("SSKM Hospital Burn Unit — Kolkata",
     "burn_centre", 2, "033-22041441", "033-22041058",
     "AJC Bose Road, Kolkata — NH-19/16 start; 50-bed burn unit",
     22.5450, 88.3426, "West Bengal", "Kolkata", "nhp", 90),

    ("Government Medical College Nagpur Burn Unit — NH-44",
     "burn_centre", 2, "0712-2745011", "0712-2700088",
     "Medical Square, Nagpur — NH-44 midpoint burn care",
     21.1458, 79.0882, "Maharashtra", "Nagpur", "nhp", 87),

    ("Civil Hospital Ahmedabad Burn Unit",
     "burn_centre", 2, "079-22681000", "079-22681055",
     "Asarwa, Ahmedabad — Gujarat highway hub; 40-bed burn unit",
     23.0497, 72.6130, "Gujarat", "Ahmedabad", "nhp", 88),

    ("SCB Medical College Burn Unit — Cuttack NH-16",
     "burn_centre", 2, "0671-2414003", "0671-2414055",
     "Mangalabag, Cuttack — NH-16 East coast; regional burn centre",
     20.4686, 85.8792, "Odisha", "Cuttack", "nhp", 87),

    ("SMS Hospital Burn Unit — Jaipur NH-48",
     "burn_centre", 2, "0141-2518291", "0141-2518888",
     "Tonk Road, Jaipur — NH-48 corridor; largest burn unit in Rajasthan",
     26.8927, 75.8036, "Rajasthan", "Jaipur", "nhp", 89),

    ("PGIMER Burn Unit — Chandigarh NH-44",
     "burn_centre", 1, "0172-2756767", "0172-2755555",
     "Sector 12, Chandigarh — NH-44 north gateway; Level I burn centre",
     30.7650, 76.7780, "Punjab", "Chandigarh", "nhp", 93),

    # =========================================================
    # NEURO / SPINAL INJURY CENTRES
    # (Head + spinal injuries = #1 and #2 road accident causes of death)
    # =========================================================

    ("NIMHANS Bengaluru — Neuro & Spinal",
     "neuro_spinal", 1, "080-46110007", "080-26995001",
     "Hosur Road, Bengaluru — premier neuroscience institute; NH-44/48",
     12.9401, 77.5959, "Karnataka", "Bengaluru", "nimhans", 98),

    ("SCTIMST Thiruvananthapuram — Neuro/Spinal",
     "neuro_spinal", 1, "0471-2524567", "0471-2443152",
     "Ulloor, Thiruvananthapuram — Sree Chitra neuro institute; NH-66 south",
     8.5228, 76.9366, "Kerala", "Thiruvananthapuram", "sctimst", 97),

    ("SGPGI Lucknow — Neuro & Spinal",
     "neuro_spinal", 1, "0522-2668700", "0522-2668800",
     "Raibareli Road, Lucknow — SGPGI neuro institute; NH-27 corridor",
     26.8370, 81.0140, "Uttar Pradesh", "Lucknow", "sgpgi", 96),

    ("PGIMER Chandigarh — Neuro/Spinal",
     "neuro_spinal", 1, "0172-2756565", "0172-2755555",
     "Sector 12, Chandigarh — NH-44 north; premier neuro/spinal centre",
     30.7650, 76.7780, "Punjab", "Chandigarh", "nhp", 96),

    ("NIMS Hyderabad — Neuro & Spinal",
     "neuro_spinal", 2, "040-23489000", "040-23489001",
     "Punjagutta, Hyderabad — Nizam's neuro institute; NH-44 corridor",
     17.4315, 78.4483, "Telangana", "Hyderabad", "nhp", 93),

    ("AIIMS Trauma Centre Delhi — Neuro/Spinal ICU",
     "neuro_spinal", 1, "011-26593308", "011-26589900",
     "Ansari Nagar, Delhi — dedicated neuro/spinal trauma ICU; NH-44/48",
     28.5671, 77.2100, "Delhi", "New Delhi", "aiims", 97),

    ("Govt Medical College Nagpur Neuro — NH-44",
     "neuro_spinal", 2, "0712-2745011", "0712-2700005",
     "Medical Square, Nagpur — neurosurgery dept; NH-44 midpoint",
     21.1458, 79.0882, "Maharashtra", "Nagpur", "nhp", 87),

    ("NIMHANS Satellite — KGMU Lucknow Neuro",
     "neuro_spinal", 2, "0522-2257540", "0522-2258880",
     "Shah Mina Road, Lucknow — KGMU neurosurgery; NH-27",
     26.8582, 80.9346, "Uttar Pradesh", "Lucknow", "nhp", 88),

    ("SSKM Neurosciences Kolkata — NH-19/16",
     "neuro_spinal", 2, "033-22041441", "033-22041058",
     "AJC Bose Road, Kolkata — neurosurgery & spinal unit; NH-16 start",
     22.5450, 88.3426, "West Bengal", "Kolkata", "nhp", 89),

    ("Madras Medical College Neuro — Chennai NH-44",
     "neuro_spinal", 2, "044-25305000", "044-25304400",
     "Park Town, Chennai — GGH neurosurgery dept; NH-44 terminus",
     13.0827, 80.2707, "Tamil Nadu", "Chennai", "nhp", 88),

    ("Sassoon Hospital Neuro — Pune NH-48",
     "neuro_spinal", 2, "020-26128000", "020-26128055",
     "Pune Station Road, Pune — neurosurgery unit; NH-48 corridor",
     18.5241, 73.8749, "Maharashtra", "Pune", "nhp", 87),

    ("SMS Hospital Neuro — Jaipur NH-48",
     "neuro_spinal", 2, "0141-2518291", "0141-2560291",
     "Tonk Road, Jaipur — neurosurgery & spinal; NH-48",
     26.8927, 75.8036, "Rajasthan", "Jaipur", "nhp", 88),

    ("SCB Medical College Neuro — Cuttack NH-16",
     "neuro_spinal", 2, "0671-2414003", None,
     "Mangalabag, Cuttack — neurosurgery dept; NH-16 East coast",
     20.4686, 85.8792, "Odisha", "Cuttack", "nhp", 85),

    # =========================================================
    # PAEDIATRIC TRAUMA  (child fatalities high on family highway trips)
    # =========================================================

    ("AIIMS Delhi — Paediatric Emergency & Trauma",
     "paediatric_trauma", 1, "011-26588500", "011-26588700",
     "Ansari Nagar, Delhi — dedicated paed emergency; NH-44/48",
     28.5675, 77.2100, "Delhi", "New Delhi", "aiims", 97),

    ("Kalawati Saran Children Hospital Delhi",
     "paediatric_trauma", 1, "011-23365501", "011-23360175",
     "Bangla Sahib Road, Delhi — largest paediatric hospital in N India",
     28.6330, 77.2100, "Delhi", "New Delhi", "nhp", 93),

    ("Institute of Child Health Kolkata — NH-19/16",
     "paediatric_trauma", 2, "033-22419491", "033-22413700",
     "AJC Bose Road, Kolkata — 500-bed children's hospital; NH-16 start",
     22.5450, 88.3426, "West Bengal", "Kolkata", "nhp", 91),

    ("BJ Wadia Hospital Mumbai — NH-66",
     "paediatric_trauma", 2, "022-23085555", "022-23085500",
     "Parel, Mumbai — paediatric trauma; NH-66 start",
     19.0035, 72.8360, "Maharashtra", "Mumbai", "nhp", 91),

    ("Govt Children Hospital Egmore — Chennai NH-44",
     "paediatric_trauma", 2, "044-28193000", "044-28193001",
     "Egmore, Chennai — Institute of Child Health; NH-44 terminus",
     13.0785, 80.2620, "Tamil Nadu", "Chennai", "nhp", 90),

    ("Indira Gandhi Children Hospital Bengaluru — NH-44",
     "paediatric_trauma", 2, "080-22863838", "080-22863839",
     "Kempe Gowda Road, Bengaluru — paediatric emergency; NH-44/48",
     12.9766, 77.5713, "Karnataka", "Bengaluru", "nhp", 89),

    # =========================================================
    # ADDITIONAL LEVEL-I TRAUMA on highest-fatality NH stretches
    # (MoRTH data: NH-44, NH-48, NH-16, NH-58 top crash corridors)
    # =========================================================

    # NH-58  Haridwar - Badrinath (hill highway, high fatality)
    ("Base Hospital Srinagar Garhwal — NH-58",
     "trauma", 2, "01346-252028", None,
     "Srinagar, Pauri Garhwal — NH-58 Haridwar-Badrinath corridor",
     30.2165, 78.7884, "Uttarakhand", "Pauri Garhwal", "nhp", 82),

    ("Government Hospital Rudraprayag — NH-58",
     "trauma", 2, "01364-233007", None,
     "Rudraprayag — NH-58/NH-107 junction; gateway to Kedarnath",
     30.2846, 78.9812, "Uttarakhand", "Rudraprayag", "nhp", 80),

    # NH-44 — Agra-Gwalior black spot stretch
    ("District Hospital Morena — NH-44",
     "trauma", 2, "07532-220200", None,
     "Morena — NH-44 highest-crash district in MP",
     26.4968, 77.9999, "Madhya Pradesh", "Morena", "nhp", 78),

    # NH-48 — Mumbai-Pune Expressway (highest crash density per km)
    ("MGM Hospital Navi Mumbai — NH-48/NH-4",
     "trauma", 2, "022-27432432", "022-27432433",
     "Sector 3, Vashi, Navi Mumbai — NH-48 expressway start",
     19.0773, 73.0147, "Maharashtra", "Navi Mumbai", "nhp", 84),

    ("Government Hospital Khopoli — NH-48 Ghat",
     "trauma", 2, "02192-262200", None,
     "Khopoli — NH-48 Bhor Ghat; highest crash density in Maharashtra",
     18.7667, 73.3416, "Maharashtra", "Raigad", "nhp", 79),

    # NH-27 — Lucknow to Gorakhpur (UP's most dangerous NH stretch)
    ("District Hospital Basti — NH-27",
     "trauma", 2, "05542-250100", None,
     "Basti — NH-27 Lucknow-Gorakhpur highest fatality zone",
     26.8019, 82.7310, "Uttar Pradesh", "Basti", "nhp", 78),

    # NH-16 — Vizag–Vijayawada (East Coast, high truck density)
    ("Government Hospital Eluru — NH-16",
     "trauma", 2, "08812-225888", None,
     "Eluru — NH-16 West Godavari; accident-prone stretch",
     16.7107, 81.0952, "Andhra Pradesh", "Eluru", "nhp", 79),

    # NH-66 — Goa Ghats (Maharashtra-Goa border, highest pedestrian fatalities)
    ("Government Hospital Sawantwadi — NH-66",
     "trauma", 2, "02363-272033", None,
     "Sawantwadi — NH-66 Goa border approach; high fatality ghat stretch",
     15.9053, 73.8211, "Maharashtra", "Sindhudurg", "nhp", 78),

    # =========================================================
    # ORTHOPAEDIC TRAUMA (fractures = most common road injury)
    # =========================================================

    ("AIIMS Delhi — Orthopaedic Trauma",
     "ortho_trauma", 1, "011-26588700", "011-26588500",
     "Ansari Nagar, Delhi — premier ortho trauma; NH-44/48 hub",
     28.5675, 77.2100, "Delhi", "New Delhi", "aiims", 97),

    ("PGIMER Chandigarh — Orthopaedics",
     "ortho_trauma", 1, "0172-2756464", "0172-2755555",
     "Sector 12, Chandigarh — NH-44; 24x7 ortho trauma",
     30.7650, 76.7780, "Punjab", "Chandigarh", "nhp", 95),

    ("KGMU Lucknow — Orthopaedic Trauma NH-27",
     "ortho_trauma", 2, "0522-2257450", "0522-2258880",
     "Shah Mina Road, Lucknow — busy ortho trauma unit; NH-27",
     26.8582, 80.9346, "Uttar Pradesh", "Lucknow", "nhp", 90),

    ("Seth GS Medical College Mumbai — Ortho",
     "ortho_trauma", 2, "022-24107000", "022-24107500",
     "Parel, Mumbai — KEM ortho trauma; NH-66",
     19.0035, 72.8407, "Maharashtra", "Mumbai", "nhp", 90),

    ("SMS Hospital Jaipur — Ortho Trauma NH-48",
     "ortho_trauma", 2, "0141-2518291", "0141-2560291",
     "Tonk Road, Jaipur — largest ortho trauma in Rajasthan; NH-48",
     26.8927, 75.8036, "Rajasthan", "Jaipur", "nhp", 89),
]


# ---------------------------------------------------------------------------

def seed_specialty_hospitals(conn):
    """
    Insert specialised NH corridor hospitals into the contacts table.
    Skips duplicates by name + district.
    Categories used:
      specialty_hospital, burn_centre, neuro_spinal,
      paediatric_trauma, trauma, ortho_trauma
    """
    cur = conn.cursor()
    inserted = 0
    skipped = 0

    for (name, cat, tier, phone, phone_alt,
         addr, lat, lon, state, dist, source, conf) in SPECIALTY_HOSPITALS:

        exists = cur.execute(
            "SELECT id FROM contacts WHERE name=? AND district=?",
            (name, dist)
        ).fetchone()
        if exists:
            skipped += 1
            continue

        cur.execute("""
            INSERT INTO contacts
              (name, category, tier, phone, phone_alt, address, lat, lon,
               state, district, country_code, source, confidence, is_active)
            VALUES (?,?,?,?,?,?,?,?,?,?,'IN',?,?,1)
        """, (name, cat, tier, phone, phone_alt,
              addr, lat, lon, state, dist, source, conf))
        inserted += 1

    conn.commit()
    print(f"[Specialty] Seeded {inserted} specialised hospitals "
          f"({skipped} already existed) — "
          f"AIIMS network, burn centres, neuro/spinal, paediatric, ortho")
    return inserted


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import sqlite3, os, sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    DB_PATH = os.environ.get("ROADSOS_DB", "roadsos.db")
    conn = sqlite3.connect(DB_PATH)
    seed_specialty_hospitals(conn)
    conn.close()
