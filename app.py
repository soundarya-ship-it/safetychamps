"""
RoadSoS — Standalone Streamlit App
===================================
Run:  streamlit run app.py
No separate server needed. Everything runs in one process.

Requirements: pip install -r requirements.txt
Free API key: https://console.groq.com (Groq — Llama 3.1, free tier)
"""

import os, sys, sqlite3, math, re, json, urllib.parse
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import requests as http

# ── Language / i18n ───────────────────────────────────────────────────────────
from ui.strings import STRINGS, LANG_OPTIONS, detect_lang_from_script, CRITICAL_KEYWORDS, HIGH_KEYWORDS

if "ui_lang" not in st.session_state:
    st.session_state.ui_lang = "en"

def get_T():
    return STRINGS[st.session_state.get("ui_lang", "en")]

T = get_T()

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="RoadSoS",
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

def _auto_init_db():
    """Auto-initialise DB on first run (needed for Streamlit Cloud)."""
    if not os.path.exists(DB_PATH):
        try:
            init_script = os.path.join(os.path.dirname(__file__), "database", "init_db.py")
            if os.path.exists(init_script):
                exec(open(init_script).read(), {"__file__": init_script})
        except Exception as e:
            pass  # App still works without DB (Tier 1 numbers always shown)

_auto_init_db()

# ══════════════════════════════════════════════════════════════════════════════
# CORE FUNCTIONS (no external deps beyond requests)
# ══════════════════════════════════════════════════════════════════════════════

INDIA_NATIONAL = [
    {"name": "National Emergency (Police + Ambulance + Fire)", "phone": "112",  "tier": 1, "category": "emergency",         "confidence": 100, "highway": True},
    {"name": "Ambulance — NHM (29 states)",                   "phone": "108",  "tier": 1, "category": "ambulance",         "confidence": 100, "highway": True},
    {"name": "NHAI Highway Helpline 24×7",                    "phone": "1033", "tier": 1, "category": "highway_helpline",  "confidence": 100, "highway": True},
    {"name": "MoRTH Road Accident Emergency",                 "phone": "1073", "tier": 1, "category": "emergency",         "confidence": 100, "highway": True},
    {"name": "Police",                                         "phone": "100",  "tier": 1, "category": "police",            "confidence": 100, "highway": True},
    {"name": "Disaster Management Helpline",                  "phone": "1078", "tier": 1, "category": "disaster",          "confidence": 100, "highway": True},
    {"name": "Fire & Rescue",                                  "phone": "101",  "tier": 1, "category": "fire",              "confidence": 100, "highway": False},
    {"name": "Women Helpline",                                 "phone": "1091", "tier": 1, "category": "helpline",          "confidence": 100, "highway": True},
]

CATEGORY_ICONS = {
    "hospital": "🏥", "ambulance": "🚑", "police": "🚔",
    "towing": "🚛",   "puncture": "🔧", "pharmacy": "💊",
    "fire": "🚒",     "highway_helpline": "🛣️", "emergency": "🆘",
    "disaster": "⛑️", "helpline": "📞", "other": "📍",
}

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
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
    """Fetch nearby emergency contacts from OpenStreetMap (free, global)."""
    if categories is None:
        categories = ["hospital", "ambulance", "police", "towing", "puncture"]

    tag_map = {
        "hospital":  [('amenity','hospital'), ('amenity','clinic'), ('healthcare','hospital')],
        "ambulance": [('emergency','ambulance_station'), ('amenity','ambulance_station')],
        "police":    [('amenity','police')],
        "pharmacy":  [('amenity','pharmacy')],
        "fire":      [('amenity','fire_station')],
        "towing":    [('shop','car_repair')],
        "puncture":  [('shop','tyres'), ('shop','bicycle')],
    }

    parts = []
    for cat in categories:
        for k, v in tag_map.get(cat, []):
            parts.append(f'node["{k}"="{v}"](around:{radius_m},{lat},{lon});')
            parts.append(f'way["{k}"="{v}"](around:{radius_m},{lat},{lon});')

    query = f'[out:json][timeout:25];\n(\n{"".join(parts)}\n);\nout body center;'

    try:
        resp = http.post(OVERPASS_URL, data={"data": query}, timeout=25)
        elements = resp.json().get("elements", [])
    except Exception as e:
        st.warning(f"OSM query issue (check internet): {e}")
        return []

    results = []
    for el in elements:
        tags = el.get("tags", {})
        name = tags.get("name") or tags.get("name:en") or tags.get("operator")
        if not name:
            continue
        phone = (tags.get("phone") or tags.get("contact:phone")
                 or tags.get("emergency:phone") or tags.get("telephone"))
        el_lat = el.get("lat") or (el.get("center") or {}).get("lat")
        el_lon = el.get("lon") or (el.get("center") or {}).get("lon")
        if not el_lat or not el_lon:
            continue

        amenity = tags.get("amenity",""); shop = tags.get("shop","")
        if amenity=="hospital" or tags.get("healthcare")=="hospital": cat="hospital"
        elif "ambulance" in amenity: cat="ambulance"
        elif amenity=="police":   cat="police"
        elif amenity=="pharmacy": cat="pharmacy"
        elif amenity=="fire_station": cat="fire"
        elif shop=="tyres" or shop=="bicycle": cat="puncture"
        elif "car_repair" in amenity or "car_repair" in shop: cat="towing"
        else: cat="other"

        dist = haversine_km(lat, lon, el_lat, el_lon)
        addr_parts = [tags.get(k) for k in ["addr:housenumber","addr:street","addr:city"] if tags.get(k)]
        results.append({
            "name": name, "phone": phone, "category": cat, "tier": 3,
            "lat": el_lat, "lon": el_lon, "distance_km": dist,
            "address": ", ".join(addr_parts),
            "source": "osm", "confidence": 58 if phone else 35,
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
    if score >= 80: return "🟢", t["verified"],   "#065f46"
    if score >= 50: return "🟡", t["likely_ok"],  "#92400e"
    return "🔴", t["unverified"], "#991b1b"


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
/* ── Base ── */
.block-container{padding-top:0.5rem !important; padding-left:1rem !important; padding-right:1rem !important; max-width:900px}

/* ── Tier 1 emergency numbers ── */
.tier1{background:#064e3b;color:white;border-radius:10px;padding:14px 10px;margin:4px 0;text-align:center;cursor:pointer}
.tier1 .num{font-size:32px;font-weight:800;letter-spacing:3px}
.tier1 .lbl{font-size:11px;opacity:.85;margin-top:4px;line-height:1.3}

/* ── Contact cards ── */
.contact-card{background:#f9fafb;border-left:4px solid #ddd;border-radius:6px;padding:10px 14px;margin:6px 0}
.contact-card.green-border{border-left-color:#059669}
.contact-card.amber-border{border-left-color:#d97706}
.contact-card.red-border{border-left-color:#dc2626}

/* ── Golden hour banners ── */
.gh-green{background:#dcfce7;border:1px solid #86efac;border-radius:10px;padding:14px;color:#14532d;margin:8px 0}
.gh-amber{background:#fef3c7;border:1px solid #fcd34d;border-radius:10px;padding:14px;color:#78350f;margin:8px 0}
.gh-red  {background:#fee2e2;border:1px solid #fca5a5;border-radius:10px;padding:14px;color:#7f1d1d;margin:8px 0}
.gh-green strong,.gh-amber strong,.gh-red strong{font-size:16px}

/* ── Phone number display ── */
.big-phone{font-size:24px;font-weight:800;color:#1e3a5f;margin:4px 0}

/* ── Buttons: bigger touch targets ── */
div.stButton > button {
    min-height: 48px;
    font-size: 16px;
    border-radius: 8px;
}
div.stButton > button[kind="primary"] {
    font-size: 18px;
    min-height: 56px;
    font-weight: 700;
}

/* ── MOBILE RESPONSIVE (screens under 768px) ── */
@media (max-width: 768px) {
    /* Stack all st.columns vertically */
    [data-testid="column"] {
        width: 100% !important;
        flex: 1 1 100% !important;
        min-width: 100% !important;
    }
    /* Tier 1 numbers: 2x2 grid feel via larger padding */
    .tier1 .num { font-size: 36px !important; }
    .tier1 .lbl { font-size: 12px !important; }
    .tier1 { padding: 16px 8px !important; margin: 3px !important; }
    /* Phone number very large on mobile */
    .big-phone { font-size: 30px !important; }
    /* Reduce outer padding */
    .block-container { padding-left: 0.5rem !important; padding-right: 0.5rem !important; }
    /* Bigger buttons on mobile */
    div.stButton > button { min-height: 54px !important; font-size: 17px !important; width: 100% !important; }
    /* Golden hour text bigger */
    .gh-green strong,.gh-amber strong,.gh-red strong { font-size: 17px !important; }
    /* Hide sidebar toggle label on mobile */
    section[data-testid="stSidebar"] { min-width: 280px !important; }
    /* Text inputs larger */
    textarea, input { font-size: 16px !important; }
}

/* ── Urgency banner ── */
[data-testid="stAlert"] { border-radius: 8px; font-size: 15px; }

/* ── Divider spacing ── */
hr { margin: 0.5rem 0 !important; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
col_h1, col_h2 = st.columns([3,1])
with col_h1:
    st.markdown("# 🚨 RoadSoS")
    st.caption(T["tagline"])
with col_h2:
    if not os.path.exists(DB_PATH):
        st.warning("⚠️ DB not initialised\n`python database/init_db.py`")
    else:
        n = sqlite3.connect(DB_PATH).execute("SELECT COUNT(*) FROM contacts WHERE is_active=1").fetchone()[0]
        st.metric(T["metric_label"], n)


# ── Offline / Online mode banner ─────────────────────────────────────────────
def _is_online():
    try:
        http.get("https://1.1.1.1", timeout=2)
        return True
    except Exception:
        return False

_online = _is_online()
if _online:
    st.info("Online mode — AI + live map search active. Works offline too: core features never need internet.")
else:
    st.success("OFFLINE MODE — Running fully offline. GPS + local DB + national numbers all working.")

st.divider()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ " + T["sidebar_settings"])

    # Language selector — manual override
    lang_codes = list(LANG_OPTIONS.keys())
    current_idx = lang_codes.index(st.session_state.get("ui_lang", "en"))
    chosen_lang = st.selectbox(
        T["lang_label"],
        options=lang_codes,
        format_func=lambda x: LANG_OPTIONS[x],
        index=current_idx,
        key="lang_select",
    )
    if chosen_lang != st.session_state.get("ui_lang"):
        st.session_state.ui_lang = chosen_lang
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
    st.caption("Built for IIT Madras Road Safety Hackathon 2026")
    st.caption("Team: Soundarya · Shreya · Ashwin")

# ── Input section ─────────────────────────────────────────────────────────────
st.subheader("📍 " + T["input_header"])

# ── GPS auto-location via browser Geolocation API ────────────────────────────
params = st.query_params
auto_lat = float(params["lat"]) if "lat" in params else 0.0
auto_lon = float(params["lon"]) if "lon" in params else 0.0

st.components.v1.html("""
<style>
#gps-btn {
    background: #1d4ed8; color: white; border: none;
    padding: 14px 20px; border-radius: 10px; font-size: 16px;
    font-weight: 700; width: 100%; cursor: pointer; margin-bottom: 6px;
}
#gps-btn:active { background: #1e40af; }
#gps-status { font-size: 13px; color: #555; text-align: center; min-height: 20px; }
</style>
<button id="gps-btn" onclick="getGPS()">Use My Phone Location (GPS)</button>
<div id="gps-status">Tap above to auto-fill your coordinates</div>
<script>
function getGPS() {
    var btn = document.getElementById('gps-btn');
    var status = document.getElementById('gps-status');
    btn.disabled = true;
    btn.textContent = 'Getting location...';
    status.textContent = 'Requesting GPS — please allow location access';
    if (!navigator.geolocation) {
        status.textContent = 'GPS not available on this device';
        btn.disabled = false; btn.textContent = 'Use My Phone Location (GPS)';
        return;
    }
    navigator.geolocation.getCurrentPosition(
        function(pos) {
            var lat = pos.coords.latitude.toFixed(5);
            var lon = pos.coords.longitude.toFixed(5);
            var acc = Math.round(pos.coords.accuracy);
            status.textContent = 'Location found! Accuracy: ' + acc + ' metres';
            btn.textContent = 'Location found';
            window.parent.location.href =
                window.parent.location.pathname + '?lat=' + lat + '&lon=' + lon;
        },
        function(err) {
            var msgs = {1:'Permission denied', 2:'Position unavailable', 3:'Timeout'};
            status.textContent = 'GPS error: ' + (msgs[err.code] || err.message);
            btn.disabled = false; btn.textContent = 'Use My Phone Location (GPS)';
        },
        {enableHighAccuracy: true, timeout: 12000, maximumAge: 30000}
    );
}
</script>
""", height=90)

if auto_lat != 0.0 and auto_lon != 0.0:
    st.success(f"GPS location captured: {auto_lat:.4f}, {auto_lon:.4f}")

# ── Text input + manual GPS ───────────────────────────────────────────────────
user_msg = st.text_area(
    T["input_label"],
    placeholder=T["input_placeholder"],
    height=80,
)

gps_lat, gps_lon = auto_lat, auto_lon  # default from GPS button
with st.expander("Enter coordinates manually (optional)"):
    col_lat, col_lon = st.columns(2)
    with col_lat:
        gps_lat = st.number_input(T["lat_label"], value=auto_lat, format="%.5f", step=0.001)
    with col_lon:
        gps_lon = st.number_input(T["lon_label"], value=auto_lon, format="%.5f", step=0.001)

go = st.button("Find Emergency Help", type="primary", use_container_width=True)

# ── ALWAYS show Tier 1 numbers ────────────────────────────────────────────────
st.subheader("✅ " + T["tier1_header"])
st.caption(T["tier1_caption"])

t1_cols = st.columns(4)
for i, n in enumerate(INDIA_NATIONAL[:4]):
    with t1_cols[i]:
        icon = CATEGORY_ICONS.get(n["category"], "📞")
        st.markdown(f"""
        <div class="tier1">
          <div class="num">{n['phone']}</div>
          <div class="lbl">{icon} {n['name']}</div>
        </div>""", unsafe_allow_html=True)

st.divider()

# ── Results ───────────────────────────────────────────────────────────────────
if go and (user_msg or (gps_lat != 0.0 and gps_lon != 0.0)):

    # 1. Parse intent
    with st.spinner(T["spinner_intent"]):
        intent = parse_intent_groq(user_msg or "emergency", _get_secret("GROQ_API_KEY"))

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

    # 3. Nearby contacts
    db_contacts, osm_contacts = [], []
    if lat and lon:
        with st.spinner(T["spinner_search"]):
            db_contacts  = fetch_db_contacts(lat, lon, radius_km)
            osm_contacts = fetch_osm_contacts(lat, lon, int(radius_km*1000), intent.get("services"))

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
            st.info(T["no_contacts"])

    # 7. Share
    st.divider()
    st.subheader("Share: " + T["share_header"])
    contacts_for_share = (db_contacts + osm_contacts)[:3]
    nearby_text = ""
    if contacts_for_share:
        c0 = contacts_for_share[0]
        nearby_text = f"\nNearest: {c0['name']} ({c0.get('distance_km','?')} km) - {c0.get('phone') or '108'}"
    share_msg = (
        f"ROAD EMERGENCY at {location_display or 'my location'}\n"
        f"Urgency: {intent['urgency'].upper()}\n"
        f"CALL 112 immediately{nearby_text}\n"
        f"Sent via RoadSoS"
    )
    wa_url  = f"https://wa.me/?text={urllib.parse.quote(share_msg)}"
    sms_url = f"sms:?body={urllib.parse.quote(share_msg)}"
    col_wa, col_sms, _ = st.columns([1,1,2])
    with col_wa:
        st.markdown(f"[WhatsApp]({wa_url})", unsafe_allow_html=True)
    with col_sms:
        st.markdown(f"[SMS]({sms_url})", unsafe_allow_html=True)
    st.caption(T["share_caption"])

elif go:
    st.warning(T["no_input"])

# Footer
st.divider()
col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    st.caption(T["footer1"])
with col_f2:
    st.caption(T["footer2"])
with col_f3:
    st.caption(T["footer3"])
