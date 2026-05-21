"""
RoadSoS — Standalone Streamlit App
===================================
Run:  streamlit run app.py
No separate server needed. Everything runs in one process.

Requirements: pip install -r requirements.txt
Free API key: https://console.groq.com (Groq — Llama 3.1, free tier)
"""

import os, sys, sqlite3, math, re, json, urllib.parse
from datetime import datetime
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import requests as http

# ── Language / i18n ───────────────────────────────────────────────────────────
from ui.strings import STRINGS, LANG_OPTIONS, detect_lang_from_script, CRITICAL_KEYWORDS, HIGH_KEYWORDS
from ui.first_aid import render_first_aid
from location.blackspots import check_blackspot_proximity
try:
    from database.verify_numbers import get_badge_html, verify_number
    VERIFY_AVAILABLE = True
except Exception:
    VERIFY_AVAILABLE = False
    def get_badge_html(phone, country_code="IN"):
        return ""

if "ui_lang" not in st.session_state:
    st.session_state.ui_lang = "en"
# Pre-seed both widget keys so Streamlit never sees index= conflict
if "lang_main" not in st.session_state:
    st.session_state["lang_main"] = st.session_state.ui_lang
if "lang_select" not in st.session_state:
    st.session_state["lang_select"] = st.session_state.ui_lang

def get_T():
    return STRINGS[st.session_state.get("ui_lang", "en")]

T = get_T()

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="RoadSoS Buddy by Safety Champs",
    page_icon="🚨",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Lazy imports (handle missing packages gracefully) ─────────────────────────
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

# ── API keys: check st.secrets (Streamlit Cloud) then os.environ (.env) ──────
def _get_secret(key):
    try:
        return st.secrets[key]
    except Exception:
        return os.environ.get(key, "")

# ── DB path + auto-init ───────────────────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(__file__), "roadsos.db")

@st.cache_resource
def _init_db_once():
    """
    Seed DB only if it is missing or empty.
    If roadsos.db is committed to the repo (preferred), this function returns
    immediately with zero work — no cold-start timeout on Streamlit Cloud.
    """
    try:
        # If DB exists and already has contacts, skip all seeding
        _n = sqlite3.connect(DB_PATH).execute(
            "SELECT COUNT(*) FROM contacts"
        ).fetchone()[0]
        if _n > 0:
            return DB_PATH  # pre-built DB found — nothing to do
    except Exception:
        pass  # Table missing or file missing — fall through to seed

    try:
        from database.init_db import (
            init_db as _init_db,
            seed_national_numbers,
            seed_tier2_contacts,
            seed_roadside_services,
            seed_trauma_centres,
            seed_blood_banks,
        )
        _conn = _init_db()
        seed_national_numbers(_conn)
        seed_tier2_contacts(_conn)
        seed_roadside_services(_conn)
        seed_trauma_centres(_conn)
        seed_blood_banks(_conn)
        _conn.close()
    except Exception:
        pass  # App still works without DB (Tier 1 numbers always shown)
    try:
        from database.verify_numbers import verify_all_contacts
        verify_all_contacts(DB_PATH)
    except Exception:
        pass
    return DB_PATH

_init_db_once()

# ══════════════════════════════════════════════════════════════════════════════
# CORE FUNCTIONS (no external deps beyond requests)
# ══════════════════════════════════════════════════════════════════════════════

INDIA_NATIONAL = [
    {"name": "Emergency", "short": "Police·Ambulance·Fire", "phone": "112",  "tier": 1, "category": "emergency",         "confidence": 100, "highway": True},
    {"name": "Ambulance", "short": "NHM · 29 states",      "phone": "108",  "tier": 1, "category": "ambulance",         "confidence": 100, "highway": True},
    {"name": "Highway",   "short": "NHAI 24×7",             "phone": "1033", "tier": 1, "category": "highway_helpline",  "confidence": 100, "highway": True},
    {"name": "Road Acc.", "short": "MoRTH",                 "phone": "1073", "tier": 1, "category": "emergency",         "confidence": 100, "highway": True},
    {"name": "Police",    "short": "",                       "phone": "100",  "tier": 1, "category": "police",            "confidence": 100, "highway": True},
    {"name": "Disaster",  "short": "Helpline",               "phone": "1078", "tier": 1, "category": "disaster",          "confidence": 100, "highway": True},
    {"name": "Fire",      "short": "& Rescue",               "phone": "101",  "tier": 1, "category": "fire",              "confidence": 100, "highway": False},
    {"name": "Women",     "short": "Helpline",               "phone": "1091", "tier": 1, "category": "helpline",          "confidence": 100, "highway": True},
]


def _flag(cc):
    """Convert ISO alpha-2 country code to flag emoji."""
    try:
        return chr(0x1F1E6 + ord(cc[0]) - 65) + chr(0x1F1E6 + ord(cc[1]) - 65)
    except Exception:
        return ""


@st.cache_data(ttl=3600)
def load_country_numbers():
    """Load all national_numbers rows from DB. Falls back to hardcoded list if DB missing."""
    try:
        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute(
            "SELECT country_code, country_name, police, ambulance, fire, emergency, notes "
            "FROM national_numbers ORDER BY country_name"
        ).fetchall()
        conn.close()
        if rows:
            return [
                {"cc": r[0], "name": r[1], "police": r[2], "ambulance": r[3],
                 "fire": r[4], "emergency": r[5], "notes": r[6]}
                for r in rows
            ]
    except Exception:
        pass
    # Hardcoded fallback (key countries) in case DB not ready
    return [
        {"cc":"IN","name":"India",        "police":"100","ambulance":"108","fire":"101","emergency":"112","notes":"108=NHM ambulance; 1033=NHAI"},
        {"cc":"US","name":"USA",          "police":"911","ambulance":"911","fire":"911","emergency":"911","notes":None},
        {"cc":"GB","name":"UK",           "police":"999","ambulance":"999","fire":"999","emergency":"999","notes":None},
        {"cc":"AU","name":"Australia",    "police":"000","ambulance":"000","fire":"000","emergency":"000","notes":None},
        {"cc":"AE","name":"UAE",          "police":"999","ambulance":"998","fire":"997","emergency":"999","notes":None},
        {"cc":"SG","name":"Singapore",    "police":"999","ambulance":"995","fire":"995","emergency":"999","notes":None},
        {"cc":"DE","name":"Germany",      "police":"110","ambulance":"112","fire":"112","emergency":"112","notes":None},
        {"cc":"FR","name":"France",       "police":"17", "ambulance":"15", "fire":"18", "emergency":"112","notes":None},
        {"cc":"JP","name":"Japan",        "police":"110","ambulance":"119","fire":"119","emergency":"110","notes":None},
        {"cc":"CN","name":"China",        "police":"110","ambulance":"120","fire":"119","emergency":"110","notes":None},
    ]


CATEGORY_ICONS = {
    "hospital": "🏥", "ambulance": "🚑", "police": "🚔",
    "towing": "🚛",   "puncture": "🔧", "pharmacy": "💊",
    "fire": "🚒",     "highway_helpline": "🛣️", "emergency": "🆘",
    "disaster": "⛑️", "helpline": "📞", "other": "📍",
    "trauma": "🏨",   "fuel": "⛽",   "blood_bank": "🩸",
}

OVERPASS_MIRRORS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
]
OVERPASS_URL = OVERPASS_MIRRORS[0]   # kept for backward compat
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"


def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return round(R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a)), 1)


def geocode_text(text):
    """Convert location text to lat/lon using Nominatim (free)."""
    try:
        clean = re.sub(
            r'\b(accident|crash|breakdown|near|on|the|a|an|help|sos|emergency|i am|there is)\b',
            ' ', text, flags=re.IGNORECASE
        )
        clean = re.sub(r'\s+', ' ', clean).strip() + " India"
        resp = http.get(NOMINATIM_URL, params={
            "q": clean, "format": "json", "limit": 1,
            "countrycodes": "in", "addressdetails": 1,
        }, headers={"User-Agent": "RoadSoS/1.0"}, timeout=8)
        results = resp.json()
        if results:
            r = results[0]
            addr = r.get("address", {})
            return {
                "lat": float(r["lat"]), "lon": float(r["lon"]),
                "display": r.get("display_name", ""),
                "city": addr.get("city") or addr.get("town") or addr.get("village", ""),
                "state": addr.get("state", ""),
            }
    except Exception as e:
        st.warning(f"Geocoding issue: {e}")
    return None


def fetch_osm_contacts(lat, lon, radius_m=15000, categories=None):
    """
    Fetch nearby emergency contacts from OpenStreetMap via Overpass API.
    Uses a compact nwr+regex query (3 lines instead of 18+) to avoid rate-limits.
    Falls back through 3 Overpass mirrors automatically.
    """
    # Compact Overpass query — nwr = node+way+relation in one shot
    # Much lighter than the old approach of separate node/way per tag
    r_small = min(radius_m, 10000)   # towing/puncture: smaller radius
    query = f"""[out:json][timeout:8];
(
  nwr["amenity"~"^(hospital|clinic|police|fire_station|ambulance_station|pharmacy)$"](around:{radius_m},{lat},{lon});
  nwr["healthcare"~"^(hospital|clinic|doctor)$"](around:{radius_m},{lat},{lon});
  nwr["emergency"~"^(ambulance_station|yes)$"](around:{radius_m},{lat},{lon});
  nwr["shop"~"^(tyres|car_repair)$"](around:{r_small},{lat},{lon});
);
out center 40;"""

    elements = []
    last_err = None
    for mirror in OVERPASS_MIRRORS:
        try:
            resp = http.post(mirror, data={"data": query}, timeout=12)
            if resp.status_code == 200:
                data = resp.json()
                elements = data.get("elements", [])
                break   # success — stop trying mirrors
        except Exception as e:
            last_err = e
            continue   # try next mirror

    if not elements and last_err:
        # Silent — caller shows fallback numbers; don't spam a warning
        return []

    results = []
    for el in elements:
        tags = el.get("tags", {})
        name = (tags.get("name") or tags.get("name:en")
                or tags.get("name:ta") or tags.get("operator"))
        if not name:
            continue
        phone = (tags.get("phone") or tags.get("contact:phone")
                 or tags.get("emergency:phone") or tags.get("telephone"))
        el_lat = el.get("lat") or (el.get("center") or {}).get("lat")
        el_lon = el.get("lon") or (el.get("center") or {}).get("lon")
        if not el_lat or not el_lon:
            continue

        amenity = tags.get("amenity", "")
        shop    = tags.get("shop", "")
        healthcare = tags.get("healthcare", "")
        if amenity in ("hospital", "clinic") or healthcare in ("hospital", "clinic"):
            cat = "hospital"
        elif "ambulance" in amenity or tags.get("emergency") == "ambulance_station":
            cat = "ambulance"
        elif amenity == "police":
            cat = "police"
        elif amenity == "pharmacy":
            cat = "pharmacy"
        elif amenity == "fire_station":
            cat = "fire"
        elif shop in ("tyres", "bicycle"):
            cat = "puncture"
        elif shop == "car_repair" or "car_repair" in amenity:
            cat = "towing"
        else:
            cat = "other"

        dist = haversine_km(lat, lon, el_lat, el_lon)
        addr_parts = [tags.get(k) for k in
                      ["addr:housenumber", "addr:street", "addr:city"] if tags.get(k)]
        results.append({
            "name": name, "phone": phone, "category": cat, "tier": 3,
            "lat": el_lat, "lon": el_lon, "distance_km": dist,
            "address": ", ".join(addr_parts),
            "source": "osm", "confidence": 60 if phone else 38,
        })

    results.sort(key=lambda x: x["distance_km"])
    return results


def fetch_db_contacts(lat, lon, radius_km=15):
    """Fetch pre-verified contacts from local SQLite DB."""
    if not os.path.exists(DB_PATH):
        return []
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    delta = radius_km / 111.0
    rows = conn.execute("""
        SELECT * FROM contacts
        WHERE is_active=1 AND lat IS NOT NULL
          AND lat BETWEEN ? AND ? AND lon BETWEEN ? AND ?
        ORDER BY confidence DESC LIMIT 50
    """, (lat-delta, lat+delta, lon-delta, lon+delta)).fetchall()
    conn.close()

    results = []
    for r in rows:
        c = dict(r)
        if c["lat"] and c["lon"]:
            dist = haversine_km(lat, lon, c["lat"], c["lon"])
            if dist <= radius_km:
                c["distance_km"] = dist
                results.append(c)
    return sorted(results, key=lambda x: x["distance_km"])


def merge_contacts(db, osm):
    """Merge DB + OSM, deduplicate by proximity (100m), rank by tier + confidence."""
    seen = []
    merged = []
    for c in db + osm:
        if not c.get("lat") or not c.get("lon"):
            merged.append(c); continue
        dup = any(haversine_km(c["lat"],c["lon"],s["lat"],s["lon"]) < 0.1 for s in seen)
        if not dup:
            seen.append({"lat": c["lat"], "lon": c["lon"]})
            merged.append(c)
    merged.sort(key=lambda x: (x.get("tier",3), -x.get("confidence",50), x.get("distance_km",999)))
    return merged


def golden_hour(nearest_km, on_highway=False, rural=False):
    t = get_T()
    speed = 80 if on_highway else (50 if rural else 30)
    eta = round((nearest_km / speed) * 60)
    if eta <= 15:
        return {"status":"green","icon":"🟢","eta":eta,
                "msg":   t["gh_green_msg"].format(eta=eta),
                "advice":t["gh_green_advice"]}
    elif eta <= 30:
        return {"status":"amber","icon":"🟡","eta":eta,
                "msg":   t["gh_amber_msg"].format(eta=eta),
                "advice":t["gh_amber_advice"]}
    else:
        return {"status":"red","icon":"🔴","eta":eta,
                "msg":   t["gh_red_msg"].format(eta=eta),
                "advice":t["gh_red_advice"]}


def parse_intent_groq(message, api_key):
    """Use Groq Llama to parse intent. Falls back to rules if unavailable."""
    if not GROQ_AVAILABLE or not api_key:
        return _rule_parse(message)
    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role":"system","content":(
                    'Extract from the user message and return ONLY JSON: '
                    '{"location":"<place or highway>","urgency":"critical|high|medium|low",'
                    '"services":["hospital","ambulance","police","towing","puncture"],'
                    '"on_highway":true/false,"highway":"<NH-44 etc or null>"}'
                )},
                {"role":"user","content":message}
            ],
            temperature=0.1, max_tokens=200,
        )
        raw = resp.choices[0].message.content.strip()
        raw = re.sub(r"```[a-z]*","",raw).strip().strip("```")
        return {**_rule_parse(message), **json.loads(raw)}
    except Exception:
        return _rule_parse(message)


def _rule_parse(message):
    msg = message.lower()
    # English keywords
    en_critical = ["blood","unconscious","not breathing","fire","critical","dying","severe"]
    en_high     = ["injured","hurt","accident","crash","hit","collision"]
    # Multilingual keywords (from ui/strings.py)
    all_critical = en_critical + [w for lang_words in CRITICAL_KEYWORDS.values() for w in lang_words]
    all_high     = en_high     + [w for lang_words in HIGH_KEYWORDS.values()     for w in lang_words]

    if any(w in msg for w in all_critical) or any(w in message for w in all_critical):
        urgency, services = "critical", ["hospital","ambulance","police"]
    elif any(w in msg for w in all_high) or any(w in message for w in all_high):
        urgency, services = "high", ["hospital","ambulance","police"]
    elif any(w in msg for w in ["puncture","flat tyre","flat tire"]):
        urgency, services = "medium", ["puncture"]
    elif any(w in msg for w in ["breakdown","tow","stranded","car won't start"]):
        urgency, services = "medium", ["towing"]
    else:
        urgency, services = "high", ["hospital","ambulance","police"]
    nh = re.search(r'(NH[-\s]?\d+|SH[-\s]?\d+)', message, re.IGNORECASE)
    # Detect language from script
    detected_lang = detect_lang_from_script(message)
    return {
        "location": message, "urgency": urgency, "services": services,
        "on_highway": bool(nh), "highway": nh.group(0) if nh else None,
        "language": detected_lang,
    }


def confidence_badge(score):
    t = get_T()
    if score >= 80: return "🟢", t["verified"],   "#166534"
    if score >= 50: return "🟡", t["likely_ok"],  "#92400E"
    return "🔴", t["unverified"], "#991B1B"


def record_feedback(contact_id, worked):
    if not os.path.exists(DB_PATH): return
    conn = sqlite3.connect(DB_PATH)
    if worked:
        conn.execute("UPDATE contacts SET user_confirms=user_confirms+1, confidence=MIN(confidence+5,100) WHERE id=?", (contact_id,))
    else:
        conn.execute("UPDATE contacts SET user_fails=user_fails+1, confidence=MAX(confidence-20,0) WHERE id=?", (contact_id,))
        conn.execute("SELECT user_fails, confidence FROM contacts WHERE id=?", (contact_id,))
        row = conn.execute("SELECT user_fails, confidence FROM contacts WHERE id=?", (contact_id,)).fetchone()
        if row and row[0] >= 3 and row[1] < 30:
            conn.execute("UPDATE contacts SET is_active=0 WHERE id=?", (contact_id,))
    conn.execute("INSERT INTO user_feedback(contact_id,worked,comment) VALUES(?,?,'via_app')", (contact_id, int(worked)))
    conn.commit(); conn.close()


# ══════════════════════════════════════════════════════════════════════════════
# STREAMLIT UI
# ══════════════════════════════════════════════════════════════════════════════

# ── CSS (mobile-first) ────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ═══════════════════════════════════════════════════════════════
   RoadSoS Design System
   ─────────────────────────────────────────────────────────────
   COLOR TOKENS  (semantic, single source of truth)
   RED   = emergency action — call now, critical, SOS
   GREEN = safe / confirmed / ambulance
   BLUE  = information, GPS, navigation
   AMBER = caution, medium urgency, warning
   ═══════════════════════════════════════════════════════════════ */
:root {
  /* Red — emergency */
  --c-red:        #DC2626;
  --c-red-dark:   #991B1B;
  --c-red-deep:   #7F1D1D;
  --c-red-bg:     #FEF2F2;
  --c-red-border: #FECACA;

  /* Green — safe / ambulance */
  --c-green:        #16A34A;
  --c-green-dark:   #166534;
  --c-green-deep:   #064E3B;  /* authority tiles */
  --c-green-bg:     #F0FDF4;
  --c-green-border: #BBF7D0;

  /* Blue — info / GPS */
  --c-blue:        #1D4ED8;
  --c-blue-dark:   #1E3A5F;
  --c-blue-bg:     #EFF6FF;
  --c-blue-border: #BFDBFE;

  /* Amber — warning */
  --c-amber:        #D97706;
  --c-amber-dark:   #92400E;
  --c-amber-bg:     #FFFBEB;
  --c-amber-border: #FDE68A;

  /* Neutral */
  --c-text:    #111827;
  --c-text-2:  #4B5563;
  --c-text-3:  #9CA3AF;
  --c-surface: #F8FAFC;
  --c-border:  #E2E8F0;
  --c-white:   #FFFFFF;

  /* ── TYPE SCALE (emergency-first: larger than typical apps) ──
     Minimum 13px — a panicking person with cracked screen must read this
  */
  --fs-xs:    11px;   /* badges, tiny chips — use sparingly */
  --fs-sm:    13px;   /* captions, secondary info */
  --fs-base:  15px;   /* body text */
  --fs-ui:    16px;   /* labels, secondary buttons */
  --fs-cta:   18px;   /* primary buttons, action text */
  --fs-num-s: 22px;   /* distances, secondary numbers */
  --fs-num-m: 26px;   /* contact phone numbers */
  --fs-num-l: 36px;   /* tier-1 emergency numbers */

  /* ── WEIGHTS ── */
  --fw-normal:  400;
  --fw-medium:  600;
  --fw-bold:    800;
}

/* ── Hide Streamlit chrome (toolbar, footer, deploy button) ── */
[data-testid="stHeader"]        { display: none !important; }
[data-testid="stToolbar"]       { display: none !important; }
[data-testid="stDeployButton"]  { display: none !important; }
[data-testid="stDecoration"]    { display: none !important; }
footer                          { display: none !important; }
#MainMenu                       { display: none !important; }

/* ── Layout ── */
.block-container {
  padding-top: 0.75rem !important;
  padding-left: 1rem !important;
  padding-right: 1rem !important;
  max-width: 900px;
  font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
  color: var(--c-text);
}

/* ── Tighten vertical rhythm — no surprise gaps ── */
.stMarkdown p { margin-bottom: 0.2rem !important; }
div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] {
  padding-top: 0 !important;
  padding-bottom: 0 !important;
}
/* Remove bottom margin on section headers */
h3 { margin-top: 0.6rem !important; margin-bottom: 0.3rem !important; }

/* ── Tier 1 emergency numbers ── */
.tier1 {
  background: var(--c-green-deep);
  color: var(--c-white);
  border-radius: 10px;
  padding: 14px 8px;
  margin: 4px 0;
  text-align: center;
  cursor: pointer;
}
.tier1 .num {
  font-size: var(--fs-num-l);
  font-weight: var(--fw-bold);
  letter-spacing: 2px;
  line-height: 1.1;
}
.tier1 .lbl {
  font-size: var(--fs-sm);
  font-weight: var(--fw-medium);
  opacity: 0.95;
  margin-top: 6px;
  line-height: 1.3;
}
.tier1 .sub {
  font-size: var(--fs-xs);
  opacity: 0.7;
  margin-top: 3px;
  line-height: 1.3;
}

/* ── Contact cards ── */
.contact-card {
  background: var(--c-surface);
  border-left: 4px solid var(--c-border);
  border-radius: 6px;
  padding: 10px 14px;
  margin: 6px 0;
}
.contact-card.green-border { border-left-color: var(--c-green); }
.contact-card.amber-border { border-left-color: var(--c-amber); }
.contact-card.red-border   { border-left-color: var(--c-red); }

/* ── Golden hour banners ── */
.gh-green {
  background: var(--c-green-bg);
  border: 1px solid var(--c-green-border);
  border-radius: 10px;
  padding: 14px;
  color: var(--c-green-dark);
  margin: 8px 0;
}
.gh-amber {
  background: var(--c-amber-bg);
  border: 1px solid var(--c-amber-border);
  border-radius: 10px;
  padding: 14px;
  color: var(--c-amber-dark);
  margin: 8px 0;
}
.gh-red {
  background: var(--c-red-bg);
  border: 1px solid var(--c-red-border);
  border-radius: 10px;
  padding: 14px;
  color: var(--c-red-dark);
  margin: 8px 0;
}
.gh-green strong, .gh-amber strong, .gh-red strong {
  font-size: var(--fs-ui);
  font-weight: var(--fw-bold);
}

/* ── Phone number display in contact cards ── */
.big-phone {
  font-size: var(--fs-num-m);
  font-weight: var(--fw-bold);
  color: var(--c-blue-dark);
  margin: 4px 0;
  letter-spacing: 1px;
}

/* ── Streamlit button overrides ── */
div.stButton > button {
  min-height: 48px;
  font-size: var(--fs-ui);
  font-weight: var(--fw-medium);
  border-radius: 8px;
  letter-spacing: 0.2px;
}
div.stButton > button[kind="primary"] {
  font-size: var(--fs-cta);
  min-height: 56px;
  font-weight: var(--fw-bold);
  letter-spacing: 0.3px;
}

/* ── Alert / info banners ── */
[data-testid="stAlert"] {
  border-radius: 8px;
  font-size: var(--fs-base);
}

/* ── Language selectbox — compact pill style ── */
div[data-testid="stSelectbox"] > div > div {
  border-radius: 20px !important;
  border-color: var(--c-border) !important;
  font-size: 13px !important;
  min-height: 34px !important;
  padding: 2px 10px !important;
  background: var(--c-surface) !important;
}
div[data-testid="stSelectbox"] > div > div:focus-within {
  border-color: var(--c-blue) !important;
  box-shadow: 0 0 0 2px rgba(29,78,216,0.15) !important;
}
/* Remove extra space that Streamlit adds around the selectbox */
div[data-testid="stSelectbox"] { margin-bottom: 0 !important; }

/* ── MOBILE (under 600px) ── */
@media (max-width: 600px) {
  /* Only stack columns that aren't the main header pair */
  .tier1 { padding: 16px 8px !important; margin: 3px !important; }
  .tier1 .num { font-size: 38px !important; }
  .tier1 .lbl { font-size: 13px !important; }
  .big-phone  { font-size: 30px !important; }
  .block-container {
    padding-top: 0.5rem !important;
    padding-left: 0.5rem !important;
    padding-right: 0.5rem !important;
  }
  div.stButton > button { min-height: 54px !important; font-size: 17px !important; width: 100% !important; }
  .gh-green strong, .gh-amber strong, .gh-red strong { font-size: 17px !important; }
  section[data-testid="stSidebar"] { min-width: 280px !important; }
  textarea, input { font-size: 16px !important; }
  /* Emergency subheader slightly smaller on mobile */
  h3 { font-size: 18px !important; }
}
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
def _is_online():
    try:
        http.get("https://1.1.1.1", timeout=2)
        return True
    except Exception:
        return False

_online = _is_online()
_online_dot = "🟢" if _online else "🔴"
_online_txt = "Online" if _online else "Offline"

try:
    _n_contacts = sqlite3.connect(DB_PATH).execute(
        "SELECT COUNT(*) FROM contacts WHERE is_active=1"
    ).fetchone()[0]
except Exception:
    _n_contacts = 0

_hcol1, _hcol2 = st.columns([5, 3])
with _hcol1:
    st.markdown("## 🚨 RoadSoS Buddy")
    st.caption("by Safety Champs · India emergency assistant")
with _hcol2:
    # ── Language selector — session state drives value, no index= needed ──
    _lang_codes = list(LANG_OPTIONS.keys())
    _chosen = st.selectbox(
        "🌐",
        options=_lang_codes,
        format_func=lambda x: LANG_OPTIONS[x],
        key="lang_main",
        label_visibility="collapsed",
        help="Change language / भाषा बदलें / மொழி மாற்று",
    )
    if _chosen != st.session_state.get("ui_lang"):
        st.session_state.ui_lang = _chosen
        st.session_state["lang_select"] = _chosen   # keep sidebar in sync
        T = get_T()
        st.rerun()
    # ── Compact status row ──
    st.markdown(
        f'<div style="text-align:right;font-family:system-ui,sans-serif;margin-top:0px">'
        f'<span style="font-size:19px;font-weight:800;color:#064E3B">'
        f'{_n_contacts if _n_contacts else "–"}</span>'
        f'<span style="font-size:10px;color:#9CA3AF;margin-left:3px">contacts</span>'
        f'&nbsp;&nbsp;{_online_dot}'
        f'</div>',
        unsafe_allow_html=True
    )

# ── SOS BUTTON ───────────────────────────────────────────────────────────────
st.html("""
<div style="display:flex;gap:10px;margin:6px 0 2px 0;font-family:system-ui,sans-serif">
  <a href="tel:112" style="flex:2;background:#DC2626;color:#FFFFFF;border-radius:12px;
     font-size:24px;font-weight:800;padding:16px 10px;letter-spacing:2px;
     text-decoration:none;display:block;text-align:center">SOS 112</a>
  <a href="tel:108" style="flex:1;background:#16A34A;color:#FFFFFF;border-radius:12px;
     font-size:17px;font-weight:800;padding:16px 6px;line-height:1.3;
     text-decoration:none;display:block;text-align:center">108<br>Ambulance</a>
</div>
<div style="font-size:13px;color:#9CA3AF;text-align:center;margin-top:6px;font-family:system-ui,sans-serif">
  Tap to call immediately &bull; Works offline &bull; 24×7 anywhere in India
</div>
""")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ " + T["sidebar_settings"])

    # Language selector — session state drives value, no index= needed
    lang_codes = list(LANG_OPTIONS.keys())
    chosen_lang = st.selectbox(
        T["lang_label"],
        options=lang_codes,
        format_func=lambda x: LANG_OPTIONS[x],
        key="lang_select",
    )
    if chosen_lang != st.session_state.get("ui_lang"):
        st.session_state.ui_lang = chosen_lang
        st.session_state["lang_main"] = chosen_lang   # keep header in sync
        T = get_T()
        st.rerun()

    st.divider()
    groq_key = st.text_input(T["groq_key_label"], type="password", help=T["groq_key_help"])
    if groq_key:
        os.environ["GROQ_API_KEY"] = groq_key
        st.success("✅ " + T["ai_active"])
    else:
        st.info("💡 " + T["no_api_info"])

    st.divider()
    radius_km = st.slider(T["radius_label"], 5, 50, 15)

    st.divider()
    st.markdown(f"**{T['always_reliable']}**")
    for n in INDIA_NATIONAL[:4]:
        st.markdown(f"`{n['phone']}` — {n['name']}")

    st.divider()
    st.caption("RoadSoS Buddy by Safety Champs")
    st.caption("IIT Madras Road Safety Hackathon 2026")
    st.caption("Soundarya · Shreya · Ashwin")

# ── Input section ─────────────────────────────────────────────────────────────
st.subheader("🆘 " + T["input_header"])

# ── GPS auto-location ─────────────────────────────────────────────────────────
# Uses streamlit-js-eval which runs JS in the main page (not a sandboxed iframe),
# so mobile browsers (Chrome Android, Samsung Internet, Safari iOS) grant permission.

if "gps_lat" not in st.session_state:
    st.session_state.gps_lat = 0.0
if "gps_lon" not in st.session_state:
    st.session_state.gps_lon = 0.0
if "_gps_pending" not in st.session_state:
    st.session_state["_gps_pending"] = False

# Accept coordinates passed via URL query params (backwards compat / desktop)
_params = st.query_params
if "lat" in _params and "lon" in _params and not st.session_state.gps_lat:
    try:
        st.session_state.gps_lat = float(_params["lat"])
        st.session_state.gps_lon = float(_params["lon"])
    except Exception:
        pass

try:
    from streamlit_js_eval import get_geolocation as _get_geolocation
    _GPS_COMPONENT = True
except ImportError:
    _GPS_COMPONENT = False

if _GPS_COMPONENT:
    _gcol1, _gcol2 = st.columns([5, 1])
    with _gcol1:
        _gps_already = bool(st.session_state.gps_lat)
        _btn_label = "✅ Location Detected — tap to re-detect" if _gps_already else "📍 Auto-detect My Location"
        if st.button(_btn_label, use_container_width=True):
            st.session_state["_gps_pending"] = True
            st.session_state.gps_lat = 0.0
            st.session_state.gps_lon = 0.0
    with _gcol2:
        if st.session_state.gps_lat:
            if st.button("🗑️", help="Clear GPS", use_container_width=True):
                st.session_state.gps_lat = 0.0
                st.session_state.gps_lon = 0.0
                st.session_state["_gps_pending"] = False
                st.session_state["_manual_lat"] = 0.0
                st.session_state["_manual_lon"] = 0.0
                st.rerun()

    if st.session_state.get("_gps_pending"):
        st.caption("⏳ Requesting your location — please **Allow** when your browser prompts…")
        _loc = _get_geolocation()
        if _loc and isinstance(_loc, dict) and _loc.get("coords"):
            st.session_state.gps_lat = float(_loc["coords"]["latitude"])
            st.session_state.gps_lon = float(_loc["coords"]["longitude"])
            # Pre-seed the manual number inputs so they show the GPS coords
            st.session_state["_manual_lat"] = st.session_state.gps_lat
            st.session_state["_manual_lon"] = st.session_state.gps_lon
            st.session_state["_gps_pending"] = False
            st.rerun()
else:
    # Fallback for local dev without streamlit-js-eval installed
    st.info("Install `streamlit-js-eval` for one-tap GPS detection on mobile.")

auto_lat = st.session_state.gps_lat
auto_lon = st.session_state.gps_lon

if auto_lat != 0.0 and auto_lon != 0.0:
    st.success(f"📍 GPS location: {auto_lat:.4f}, {auto_lon:.4f}")
    # Proactive black spot check on GPS capture
    _gps_spots = check_blackspot_proximity(auto_lat, auto_lon, radius_km=10)
    if _gps_spots:
        s = _gps_spots[0]
        st.warning(
            f"**Accident Black Spot Nearby ({s['distance_km']} km):** {s['name']}\n\n"
            f"**Risk:** {s['risk_reason']}\n\n"
            f"**Safety tip:** {s['tip']}"
        )

# ── WhatsApp Emergency Card — always visible ──────────────────────────────────
def _build_wa_url(lat=0.0, lon=0.0, situation="", urgency="", nearest_name="", nearest_phone=""):
    """Build a WhatsApp share URL with a rich pre-filled emergency card."""
    now = datetime.now()
    time_str = now.strftime("%d %b %Y, %I:%M %p")

    if lat and lon and lat != 0.0 and lon != 0.0:
        loc_line   = f"📍 GPS: {lat:.5f}, {lon:.5f}"
        maps_line  = f"🗺️ https://maps.google.com/?q={lat},{lon}"
    else:
        loc_line   = "📍 Location: (GPS not yet detected — tap GPS button)"
        maps_line  = ""

    situation_line = f"🚗 Situation: {situation}\n" if situation else ""
    urgency_line   = f"⚠️ Urgency: {urgency.upper()}\n" if urgency else ""
    nearest_line   = (f"🏥 Nearest help: {nearest_name} — {nearest_phone}\n"
                      if nearest_name and nearest_phone else "")

    msg = (
        f"🚨 ROAD ACCIDENT — URGENT HELP NEEDED 🚨\n\n"
        f"{loc_line}\n"
        f"{maps_line}\n\n"
        f"⏰ Time: {time_str}\n\n"
        f"{situation_line}"
        f"{urgency_line}"
        f"{nearest_line}\n"
        f"📞 Call 112 — Emergency (Police · Ambulance · Fire)\n"
        f"📞 Call 108 — Ambulance (NHM, 29 states)\n"
        f"📞 Call 1033 — NHAI Highway Helpline\n\n"
        f"🩺 DO NOT move injured — wait for ambulance\n"
        f"❤️ Sent via RoadSoS Buddy | safetychamps.streamlit.app"
    )
    return f"https://wa.me/?text={urllib.parse.quote(msg.strip())}"


# Build URL using whatever we know right now (GPS + any prior search)
_prior_intent  = st.session_state.get("last_intent", {}) or {}
_wa_url_now = _build_wa_url(
    lat          = auto_lat,
    lon          = auto_lon,
    situation    = "",          # no search yet at this point
    urgency      = "",
    nearest_name = "",
    nearest_phone= "",
)

st.html(f"""
<div style="margin:10px 0 6px 0;font-family:system-ui,sans-serif">

  <!-- Card container -->
  <div style="background:linear-gradient(135deg,#16A34A 0%,#15803D 100%);
              border-radius:14px;padding:14px 16px;position:relative;overflow:hidden">

    <!-- Decorative circles -->
    <div style="position:absolute;right:-20px;top:-20px;width:80px;height:80px;
                background:rgba(255,255,255,0.08);border-radius:50%"></div>
    <div style="position:absolute;right:20px;bottom:-25px;width:60px;height:60px;
                background:rgba(255,255,255,0.06);border-radius:50%"></div>

    <!-- Header row -->
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px">
      <span style="font-size:22px">📲</span>
      <div>
        <div style="font-size:16px;font-weight:800;color:#FFFFFF;line-height:1.1">
          Share Emergency on WhatsApp
        </div>
        <div style="font-size:11px;color:rgba(255,255,255,0.8);margin-top:1px">
          {"📍 GPS ready · " if auto_lat else ""}Pre-fills location · numbers · time
        </div>
      </div>
    </div>

    <!-- Preview card -->
    <div style="background:rgba(255,255,255,0.12);border-radius:10px;
                padding:10px 12px;margin-bottom:10px;font-size:12px;
                color:rgba(255,255,255,0.95);line-height:1.7;font-family:monospace">
      🚨 ROAD ACCIDENT — URGENT HELP<br>
      {"📍 GPS: " + str(round(auto_lat,4)) + ", " + str(round(auto_lon,4)) if auto_lat else "📍 Location: [tap GPS to add]"}<br>
      {"🗺️ maps.google.com/?q=" + str(auto_lat) + "," + str(auto_lon) + "<br>" if auto_lat else ""}
      📞 112 · 108 · 1033<br>
      ⏰ {datetime.now().strftime("%d %b %Y, %I:%M %p")}
    </div>

    <!-- Big WhatsApp button -->
    <a href="{_wa_url_now}"
       target="_blank"
       style="display:block;background:#FFFFFF;color:#16A34A;border-radius:10px;
              font-size:17px;font-weight:800;padding:13px;text-align:center;
              text-decoration:none;letter-spacing:0.3px">
      📤 Send on WhatsApp
    </a>

    <div style="font-size:11px;color:rgba(255,255,255,0.7);text-align:center;margin-top:8px">
      You choose who to send to · Works on mobile & desktop
    </div>
  </div>

</div>
""")

# ── Text input + manual GPS ───────────────────────────────────────────────────
user_msg = st.text_area(
    T["input_label"],
    placeholder=T["input_placeholder"],
    height=80,
)

# Pre-seed session state keys so number_input reads from them (avoids
# the "value= conflicts with session state" warning in Streamlit >=1.35)
if "_manual_lat" not in st.session_state:
    st.session_state["_manual_lat"] = auto_lat
if "_manual_lon" not in st.session_state:
    st.session_state["_manual_lon"] = auto_lon
# If GPS just fired, push the new coords into the widget keys
if auto_lat != 0.0 and st.session_state["_manual_lat"] == 0.0:
    st.session_state["_manual_lat"] = auto_lat
if auto_lon != 0.0 and st.session_state["_manual_lon"] == 0.0:
    st.session_state["_manual_lon"] = auto_lon

with st.expander("Enter coordinates manually (optional)"):
    col_lat, col_lon = st.columns(2)
    with col_lat:
        gps_lat = st.number_input(T["lat_label"], format="%.5f", step=0.001, key="_manual_lat")
    with col_lon:
        gps_lon = st.number_input(T["lon_label"], format="%.5f", step=0.001, key="_manual_lon")

gps_lat = gps_lat or auto_lat
gps_lon = gps_lon or auto_lon

go = st.button("🔍 Find Emergency Help Near Me", type="primary", use_container_width=True)

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ── Results ───────────────────────────────────────────────────────────────────
if go and (user_msg or (gps_lat != 0.0 and gps_lon != 0.0)):

    # 1. Parse intent
    with st.spinner(T["spinner_intent"]):
        intent = parse_intent_groq(user_msg or "emergency", _get_secret("GROQ_API_KEY"))
    st.session_state.last_intent = intent

    # Auto-detect language from script and switch UI if needed
    if user_msg:
        detected = detect_lang_from_script(user_msg)
        if detected != "en" and detected != st.session_state.get("ui_lang", "en"):
            st.session_state.ui_lang = detected
            T = get_T()
            st.toast(f"Language detected: {LANG_OPTIONS[detected]}", icon="🌐")
        elif intent.get("language") in STRINGS and intent["language"] != st.session_state.get("ui_lang","en") and st.session_state.get("ui_lang","en") == "en":
            st.session_state.ui_lang = intent["language"]
            T = get_T()

    urgency_colors = {"critical":"🔴","high":"🟠","medium":"🟡","low":"🟢"}
    st.info(f"{urgency_colors.get(intent['urgency'],'🟠')} **{T['urgency_label']}: {intent['urgency'].upper()}** — "
            f"{T['calling_label']}: {', '.join(intent.get('services',['ambulance']))} "
            + (f"| {intent['highway']}" if intent.get('highway') else ""))

    # 2. Geocode — GPS first, then offline lookup, then Nominatim (online)
    from location.offline_geo import lookup_offline
    lat, lon, location_display = None, None, ""
    geo_source = ""

    if gps_lat != 0.0 and gps_lon != 0.0:
        # Phone GPS — best accuracy, fully offline
        lat, lon = gps_lat, gps_lon
        location_display = f"{lat:.4f}, {lon:.4f}"
        geo_source = "GPS"
        st.success(f"GPS location: **{lat:.4f}, {lon:.4f}**")
    elif user_msg:
        # Try offline lookup first (no internet needed)
        geo = lookup_offline(intent.get("location") or user_msg)
        if geo:
            lat, lon = geo["lat"], geo["lon"]
            location_display = geo.get("display", "")
            geo_source = "offline"
            st.success(f"Location (offline): **{geo.get('city','')}**")
        else:
            # Fall back to Nominatim if online
            with st.spinner(T["spinner_locate"]):
                geo = geocode_text(intent.get("location") or user_msg)
            if geo:
                lat, lon = geo["lat"], geo["lon"]
                location_display = geo.get("display", "")
                geo_source = "online"
                st.success(f"{T['located_msg']}: **{geo.get('city','')}, {geo.get('state','')}**")
            else:
                st.warning(f"{T['no_location']}")

    # 2b. Black Spot Warning — check after geocoding (for typed locations)
    if lat and lon and geo_source != "GPS":  # GPS already checked above
        _spots = check_blackspot_proximity(lat, lon, radius_km=10)
        if _spots:
            s = _spots[0]
            st.warning(
                f"**Accident Black Spot Nearby ({s['distance_km']} km):** {s['name']}\n\n"
                f"**Risk:** {s['risk_reason']}\n\n"
                f"**Safety tip:** {s['tip']}"
            )

    # 3. Nearby contacts — include blood_bank + trauma for critical injuries
    db_contacts, osm_contacts = [], []
    _is_critical = intent.get("urgency") in ("critical", "high")
    _osm_cats = list(intent.get("services", []))
    if _is_critical and "trauma" not in _osm_cats:
        _osm_cats.append("trauma")
    if _is_critical and "blood_bank" not in _osm_cats:
        _osm_cats.append("blood_bank")

    if not lat or not lon:
        # Location could not be resolved — still show actionable numbers
        st.markdown("""
<div style="background:#FFFBEB;border:2px solid #D97706;border-radius:14px;
            padding:16px 18px;margin:10px 0;font-family:system-ui,sans-serif">
  <div style="font-size:15px;font-weight:700;color:#92400E;margin-bottom:4px">
    📍 Location not resolved — tap GPS button above or type a city name
  </div>
  <div style="font-size:13px;color:#4B5563;margin-bottom:14px">
    While you do that, these numbers work <strong>anywhere in India right now:</strong>
  </div>
  <div style="display:flex;gap:8px">
    <a href="tel:112" style="flex:1;background:#DC2626;color:#FFFFFF;border-radius:10px;
       padding:16px 4px;text-align:center;text-decoration:none;font-size:28px;
       font-weight:800;letter-spacing:1px;display:block">112</a>
    <a href="tel:108" style="flex:1;background:#16A34A;color:#FFFFFF;border-radius:10px;
       padding:16px 4px;text-align:center;text-decoration:none;font-size:28px;
       font-weight:800;letter-spacing:1px;display:block">108</a>
    <a href="tel:1033" style="flex:1;background:#1D4ED8;color:#FFFFFF;border-radius:10px;
       padding:16px 4px;text-align:center;text-decoration:none;font-size:22px;
       font-weight:800;letter-spacing:1px;display:block;line-height:1.4">1033</a>
  </div>
</div>
""", unsafe_allow_html=True)

    if lat and lon:
        with st.spinner(T["spinner_search"]):
            db_contacts  = fetch_db_contacts(lat, lon, radius_km)
            osm_contacts = fetch_osm_contacts(lat, lon, int(radius_km*1000), _osm_cats or intent.get("services"))

        all_contacts = merge_contacts(db_contacts, osm_contacts)

        # 4. Golden Hour Score
        hospitals = [c for c in all_contacts if c.get("category")=="hospital"]
        if hospitals:
            gh = golden_hour(hospitals[0]["distance_km"], intent.get("on_highway",False))
            gh_class = {"green":"gh-green","amber":"gh-amber","red":"gh-red"}[gh["status"]]
            st.markdown(f"""
            <div class="{gh_class}">
              <strong>{gh['icon']} Golden Hour Score: {gh['msg']}</strong><br>
              <span style="font-size:13px">{gh['advice']}</span>
            </div>""", unsafe_allow_html=True)
            st.markdown("")

        # 4b. Blood bank alert — shown prominently for critical cases
        if _is_critical:
            blood_banks_found = [c for c in all_contacts if c.get("category") == "blood_bank"]
            if blood_banks_found:
                bb = blood_banks_found[0]
                st.markdown(
                    f'<div style="background:#FEF2F2;border:2px solid #DC2626;border-radius:10px;'
                    f'padding:12px 16px;margin:8px 0;font-family:system-ui,sans-serif">'
                    f'<div style="font-size:15px;font-weight:600;color:#991B1B">'
                    f'🩸 Nearest Blood Bank: {bb["name"]}</div>'
                    f'<div style="font-size:26px;font-weight:800;color:#DC2626;margin:6px 0;letter-spacing:1px">'
                    f'{bb.get("phone","Call 112")}</div>'
                    f'<div style="font-size:13px;color:#4B5563">'
                    f'{bb.get("distance_km","?")} km away &nbsp;·&nbsp; '
                    f'{bb.get("address","")}</div>'
                    f'<div style="font-size:13px;color:#991B1B;margin-top:6px">'
                    f'Call ahead to pre-order blood — tell them accident type and likely blood volume needed</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    '<div style="background:#FEF2F2;border:1px solid #FECACA;border-radius:8px;'
                    'padding:10px 14px;margin:8px 0;font-size:13px;color:#991B1B;'
                    'font-family:system-ui,sans-serif">'
                    '🩸 <b>Blood bank needed:</b> Call the nearest trauma centre directly '
                    '— all listed trauma centres have 24×7 blood banks on-site.</div>',
                    unsafe_allow_html=True
                )

        # 5. Triage call order
        if intent["urgency"] in ("critical","high"):
            if intent.get("on_highway"):
                st.error(f"🚨 **{T['callorder_critical_hw']}**")
            else:
                st.error(f"🚨 **{T['callorder_critical']}**")
        elif intent["urgency"] == "medium":
            if "puncture" in intent.get("services",[]):
                st.warning(f"**{T['callorder_puncture']}**")
            else:
                st.warning(f"**{T['callorder_medium']}**")

        # 6. Show nearby contacts
        if all_contacts:
            st.subheader(f"{len(all_contacts)} " + T["contacts_found"].format(r=radius_km))
            for c in all_contacts[:12]:
                icon  = CATEGORY_ICONS.get(c.get("category","other"), "[!]")
                conf  = c.get("confidence", 50)
                badge_icon, badge_text, badge_color = confidence_badge(conf)
                phone = c.get("phone") or "--"
                dist  = c.get("distance_km","?")
                tier_label = {1:"National",2:"Verified",3:"Local"}.get(c.get("tier",3),"Local")
                with st.expander(
                    f"{icon} **{c['name']}** - {dist} km | {badge_icon} {badge_text} | {tier_label}",
                    expanded=(conf >= 80 or c.get("tier",3) <= 2)
                ):
                    col_a, col_b, col_c = st.columns([2,2,1])
                    with col_a:
                        if phone and phone != "--":
                            st.markdown(f'<p class="big-phone">{phone}</p>', unsafe_allow_html=True)
                            badge_html = get_badge_html(phone, c.get("country_code", "IN"))
                            if badge_html:
                                st.markdown(badge_html, unsafe_allow_html=True)
                            if c.get("phone_alt"):
                                st.markdown(f"Alt: **{c['phone_alt']}**")
                        else:
                            st.warning(T["no_phone"])
                        if c.get("address"):
                            st.caption(f"Addr: {c['address']}")
                    with col_b:
                        st.progress(conf/100, text=f"{T['confidence_label']}: {conf}%")
                        st.caption(f"{T['source_label']}: {c.get('source','unknown')} | Tier {c.get('tier',3)}")
                        if conf < 50:
                            st.warning(T["low_conf_warning"])
                    with col_c:
                        cid = c.get("id", 0)
                        if cid and st.button("OK " + T["btn_worked"], key=f"ok_{cid}_{c['name'][:8]}"):
                            record_feedback(cid, True)
                            st.success(T["feedback_ok"])
                        if cid and st.button("X " + T["btn_failed"], key=f"no_{cid}_{c['name'][:8]}"):
                            record_feedback(cid, False)
                            st.error(T["feedback_fail"])
        else:
            # No local contacts from DB or OSM — show national numbers prominently
            st.markdown("""
<div style="background:#FEF2F2;border:2px solid #DC2626;border-radius:14px;
            padding:16px 18px;margin:10px 0;font-family:system-ui,sans-serif">
  <div style="font-size:15px;font-weight:700;color:#991B1B;margin-bottom:4px">
    ⚠️ No nearby contacts found in database for this area
  </div>
  <div style="font-size:13px;color:#4B5563;margin-bottom:14px">
    OSM/DB may not have this location yet — but these national numbers work <strong>anywhere in India, 24×7:</strong>
  </div>
  <div style="display:flex;gap:8px">
    <a href="tel:112" style="flex:1;background:#DC2626;color:#FFFFFF;border-radius:10px;
       padding:16px 4px;text-align:center;text-decoration:none;font-size:28px;
       font-weight:800;letter-spacing:1px;display:block">112</a>
    <a href="tel:108" style="flex:1;background:#16A34A;color:#FFFFFF;border-radius:10px;
       padding:16px 4px;text-align:center;text-decoration:none;font-size:28px;
       font-weight:800;letter-spacing:1px;display:block">108</a>
    <a href="tel:1033" style="flex:1;background:#1D4ED8;color:#FFFFFF;border-radius:10px;
       padding:16px 4px;text-align:center;text-decoration:none;font-size:22px;
       font-weight:800;letter-spacing:1px;display:block;line-height:1.4">1033</a>
  </div>
  <div style="font-size:11px;color:#6B7280;margin-top:10px;line-height:1.7">
    📞 112 — Emergency (Police · Ambulance · Fire) &nbsp;|&nbsp;
    📞 108 — NHM Ambulance (29 states) &nbsp;|&nbsp;
    📞 1033 — NHAI Highway Helpline
  </div>
</div>
""", unsafe_allow_html=True)

    # 7. Share — rich card with full situation context
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.subheader("📤 " + T["share_header"])

    contacts_for_share = (db_contacts + osm_contacts)[:1]
    _near_name  = contacts_for_share[0]["name"]  if contacts_for_share else ""
    _near_phone = contacts_for_share[0].get("phone","108") if contacts_for_share else ""

    _wa_url_rich = _build_wa_url(
        lat           = gps_lat,
        lon           = gps_lon,
        situation     = user_msg[:120] if user_msg else "",
        urgency       = intent.get("urgency",""),
        nearest_name  = _near_name,
        nearest_phone = _near_phone,
    )

    # SMS fallback (shorter message)
    _sms_body = (
        f"ROAD ACCIDENT {location_display or ''}\n"
        f"Urgency: {intent.get('urgency','?').upper()}\n"
        f"{('GPS: https://maps.google.com/?q=' + str(gps_lat) + ',' + str(gps_lon)) if gps_lat else ''}\n"
        f"CALL 112 | 108\n"
        f"Sent via RoadSoS"
    )
    sms_url = f"sms:?body={urllib.parse.quote(_sms_body.strip())}"

    # Urgency colour
    _urg = intent.get("urgency","medium")
    _urg_colour = {"critical":"#DC2626","high":"#EA580C","medium":"#D97706","low":"#16A34A"}.get(_urg,"#D97706")

    st.html(f"""
<div style="font-family:system-ui,sans-serif;margin:4px 0 10px 0">

  <!-- Rich WhatsApp card -->
  <div style="background:linear-gradient(135deg,#16A34A 0%,#15803D 100%);
              border-radius:14px;padding:14px 16px;margin-bottom:10px;position:relative;overflow:hidden">
    <div style="position:absolute;right:-15px;top:-15px;width:70px;height:70px;
                background:rgba(255,255,255,0.08);border-radius:50%"></div>

    <div style="font-size:13px;font-weight:700;color:rgba(255,255,255,0.85);
                margin-bottom:8px;text-transform:uppercase;letter-spacing:0.5px">
      📲 Full Emergency Card — WhatsApp
    </div>

    <!-- Message preview -->
    <div style="background:rgba(255,255,255,0.12);border-radius:10px;
                padding:10px 12px;margin-bottom:10px;font-size:11.5px;
                color:rgba(255,255,255,0.95);line-height:1.75;font-family:monospace">
      🚨 ROAD ACCIDENT — URGENT HELP<br>
      {("📍 " + str(round(gps_lat,4)) + ", " + str(round(gps_lon,4))) if gps_lat else "📍 Location text shared"}<br>
      {("🗺️ maps.google.com/?q=" + str(gps_lat) + "," + str(gps_lon) + "<br>") if gps_lat else ""}
      {("🚗 " + user_msg[:80] + ("…" if len(user_msg) > 80 else "") + "<br>") if user_msg else ""}
      <span style="color:#FDE68A;font-weight:700">⚠️ Urgency: {_urg.upper()}</span><br>
      {("🏥 " + _near_name + " — " + _near_phone + "<br>") if _near_name else ""}
      📞 112 · 108 · 1033 &nbsp;⏰ {datetime.now().strftime("%I:%M %p")}
    </div>

    <a href="{_wa_url_rich}" target="_blank"
       style="display:block;background:#FFFFFF;color:#16A34A;border-radius:10px;
              font-size:17px;font-weight:800;padding:13px;text-align:center;
              text-decoration:none;letter-spacing:0.3px">
      📤 Send on WhatsApp
    </a>
    <div style="font-size:11px;color:rgba(255,255,255,0.7);text-align:center;margin-top:7px">
      You choose who to send to · Location · situation · nearest hospital included
    </div>
  </div>

  <!-- SMS fallback -->
  <a href="{sms_url}"
     style="display:block;background:#1D4ED8;color:#FFFFFF;border-radius:10px;
            font-size:15px;font-weight:700;padding:12px;text-align:center;
            text-decoration:none">
    💬 Send as SMS (no internet needed)
  </a>
  <div style="font-size:11px;color:#9CA3AF;text-align:center;margin-top:5px">
    {T["share_caption"]}
  </div>

</div>
""")

elif go:
    st.warning(T["no_input"])

# ── ALWAYS show Tier 1 numbers ────────────────────────────────────────────────
st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
st.subheader("✅ " + T["tier1_header"])
st.caption(T["tier1_caption"])

t1_cols = st.columns(4)
for i, n in enumerate(INDIA_NATIONAL[:4]):
    with t1_cols[i]:
        icon = CATEGORY_ICONS.get(n["category"], "📞")
        short = n.get("short", "")
        st.markdown(f"""
        <div class="tier1">
          <div class="num">{n['phone']}</div>
          <div class="lbl">{icon} {n['name']}</div>
          {f'<div class="sub">{short}</div>' if short else ''}
        </div>""", unsafe_allow_html=True)

# ── International Emergency Numbers ──────────────────────────────────────────
st.subheader("🌍 International Emergency Numbers")
_all_countries = load_country_numbers()
st.caption(f"Instant reference for {len(_all_countries)} countries — works fully offline")

_search_col, _info_col = st.columns([3, 1])
with _search_col:
    _country_search = st.text_input(
        "Search country", placeholder="e.g. Germany, Japan, UAE...",
        label_visibility="collapsed", key="country_search"
    )
with _info_col:
    st.markdown(
        f'<div style="background:#1D4ED8;color:#FFFFFF;border-radius:8px;'
        f'padding:6px 12px;text-align:center;font-weight:600;font-size:14px;'
        f'font-family:system-ui,sans-serif">'
        f'{len(_all_countries)} Countries</div>',
        unsafe_allow_html=True
    )

_filtered = [
    c for c in _all_countries
    if not _country_search or _country_search.lower() in c["name"].lower()
       or _country_search.upper() in c["cc"]
]

if _filtered:
    def _country_card_html(c):
        emerg  = c.get("emergency") or c.get("ambulance") or "—"
        police = c.get("police") or "—"
        amb    = c.get("ambulance") or "—"
        fire   = c.get("fire") or "—"
        cc     = c["cc"].upper()
        name   = c["name"]
        return (
            f'<div style="border:1px solid #E2E8F0;border-radius:10px;'
            f'padding:10px 12px;margin:3px 0;background:#F8FAFC;min-height:90px;'
            f'font-family:system-ui,sans-serif">'
            f'<div style="display:flex;align-items:center;gap:6px;margin-bottom:4px">'
            f'<span style="background:#1E3A5F;color:#FFFFFF;font-size:10px;font-weight:600;'
            f'padding:2px 6px;border-radius:4px;letter-spacing:0.8px">{cc}</span>'
            f'<span style="font-size:14px;font-weight:600;color:#111827">{name}</span>'
            f'</div>'
            f'<div style="font-size:26px;font-weight:800;color:#DC2626;'
            f'letter-spacing:1px;margin:4px 0;line-height:1.1">{emerg}</div>'
            f'<div style="font-size:12px;color:#4B5563;line-height:1.8">'
            f'🚔&nbsp;{police}&nbsp;&nbsp;🚑&nbsp;{amb}&nbsp;&nbsp;🚒&nbsp;{fire}</div>'
            f'</div>'
        )

    _show_limit = 12 if not _country_search else len(_filtered)
    _display = _filtered[:_show_limit]
    _cols_per_row = 3
    for _row_start in range(0, len(_display), _cols_per_row):
        _row = _display[_row_start:_row_start + _cols_per_row]
        _rcols = st.columns(_cols_per_row)
        for _ci, _c in enumerate(_row):
            with _rcols[_ci]:
                st.markdown(_country_card_html(_c), unsafe_allow_html=True)

    if not _country_search and len(_filtered) > _show_limit:
        with st.expander(f"Show all {len(_filtered)} countries"):
            _rest = _filtered[_show_limit:]
            for _row_start in range(0, len(_rest), _cols_per_row):
                _row = _rest[_row_start:_row_start + _cols_per_row]
                _rcols = st.columns(_cols_per_row)
                for _ci, _c in enumerate(_row):
                    with _rcols[_ci]:
                        st.markdown(_country_card_html(_c), unsafe_allow_html=True)
else:
    st.info(f"No country found matching '{_country_search}'")

# ── First Aid — ALWAYS VISIBLE (works offline, no search needed) ─────────────
st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
st.subheader("🩺 First Aid & Golden Hour Guide")
st.caption("Works fully offline · WHO · Indian Red Cross · MoRTH guidelines")
_intent_for_aid = st.session_state.get("last_intent", None)
render_first_aid(user_msg=user_msg, intent=_intent_for_aid,
                 lang=st.session_state.get("ui_lang", "en"))

# Footer
st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    st.caption(T["footer1"])
with col_f2:
    st.caption(T["footer2"])
with col_f3:
    st.caption(T["footer3"])
