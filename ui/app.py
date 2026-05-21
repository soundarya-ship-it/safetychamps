"""
RoadSoS — Streamlit Demo UI
Run: streamlit run ui/app.py
"""

import streamlit as st
import requests
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

API_BASE = os.environ.get("ROADSOS_API", "http://localhost:8000")

st.set_page_config(
    page_title="RoadSoS — Emergency AI Assistant",
    page_icon="🚨",
    layout="centered",
)

# ── Styling ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.conf-green { color: #1e5a3c; font-weight: 600; }
.conf-amber { color: #b45309; font-weight: 600; }
.conf-red   { color: #b91c1c; font-weight: 600; }
.tier1-badge { background:#1e5a3c; color:white; padding:2px 8px; border-radius:4px; font-size:12px; }
.tier2-badge { background:#1a3f6e; color:white; padding:2px 8px; border-radius:4px; font-size:12px; }
.tier3-badge { background:#888;    color:white; padding:2px 8px; border-radius:4px; font-size:12px; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🚨 RoadSoS")
st.caption("Emergency AI Assistant for Road Accident Victims · Works offline · 240 countries")

st.divider()

# ── Input ─────────────────────────────────────────────────────────────────────
col1, col2 = st.columns([2, 1])
with col1:
    user_msg = st.text_input(
        "Describe the emergency",
        placeholder="e.g. Accident near Hosur on NH-44, person injured",
    )
with col2:
    lang = st.selectbox("Language", ["English", "Tamil", "Hindi"])

col3, col4 = st.columns(2)
with col3:
    lat = st.number_input("Latitude (optional)", value=0.0, format="%.6f")
with col4:
    lon = st.number_input("Longitude (optional)", value=0.0, format="%.6f")

search = st.button("🔍 Find Emergency Contacts", type="primary", use_container_width=True)

# ── Results ───────────────────────────────────────────────────────────────────
if search and user_msg:
    with st.spinner("Finding nearest emergency contacts..."):
        try:
            payload = {
                "message": user_msg,
                "lat": lat if lat != 0.0 else None,
                "lon": lon if lon != 0.0 else None,
            }
            resp = requests.post(f"{API_BASE}/chat", json=payload, timeout=30)
            data = resp.json()
        except Exception as e:
            st.error(f"Could not reach API: {e}")
            st.info("Showing fallback numbers only.")
            data = {
                "national_numbers": [
                    {"name": "National Emergency", "phone": "112", "tier": 1, "confidence": 100},
                    {"name": "Ambulance (NHM)",    "phone": "108", "tier": 1, "confidence": 100},
                    {"name": "NHAI Helpline",       "phone": "1033","tier": 1, "confidence": 100},
                ]
            }

    # Golden Hour Score
    if "golden_hour" in data:
        gh = data["golden_hour"]
        status_map = {"green": "success", "amber": "warning", "red": "error"}
        st.info(f"{gh['icon']} **{gh['message']}**\n\n{gh['advice']}")

    # Triage advice
    if "triage" in data:
        tr = data["triage"]
        st.warning(f"📞 **Call order:** {tr['primary_advice']}")

    st.divider()

    # Tier 1 — Always reliable
    st.subheader("✅ National Numbers — Always Working")
    st.caption("These are government-mandated, 24×7, 100% reliable")

    cols = st.columns(3)
    for i, num in enumerate(data.get("national_numbers", [])[:3]):
        with cols[i % 3]:
            st.metric(label=num["name"], value=num["phone"])

    st.divider()

    # Nearby contacts
    nearby = data.get("nearby_contacts", [])
    if nearby:
        st.subheader(f"📍 Nearest Contacts ({len(nearby)} found)")

        for c in nearby:
            conf  = c.get("confidence", 50)
            cmeta = c.get("confidence_meta", {})
            tier  = c.get("tier", 3)
            tier_label = {1: "🟢 National", 2: "🔵 Verified", 3: "⚪ Local"}.get(tier, "⚪ Local")

            with st.expander(
                f"{cmeta.get('icon','?')} {c['name']} — {c.get('distance_km','?')} km away | {tier_label}",
                expanded=(tier <= 2)
            ):
                col_a, col_b = st.columns(2)
                with col_a:
                    phone = c.get("phone", "No number listed")
                    if phone:
                        st.markdown(f"**📞 {phone}**")
                        if c.get("phone_alt"):
                            st.markdown(f"Alt: {c['phone_alt']}")
                    if c.get("address"):
                        st.caption(c["address"])
                with col_b:
                    st.progress(conf / 100)
                    st.caption(f"Confidence: {conf}% — {cmeta.get('text','')}")

                if c.get("show_fallback_warning"):
                    st.warning("⚠️ Low confidence. Try 112 if this doesn't connect.")

                # Feedback buttons
                fc1, fc2 = st.columns(2)
                with fc1:
                    if st.button("✅ Number worked", key=f"ok_{c.get('id','')}_{c['name']}"):
                        requests.post(f"{API_BASE}/feedback", json={"contact_id": c.get("id", 0), "worked": True})
                        st.success("Thank you! Data updated.")
                with fc2:
                    if st.button("❌ Didn't work", key=f"fail_{c.get('id','')}_{c['name']}"):
                        requests.post(f"{API_BASE}/feedback", json={"contact_id": c.get("id", 0), "worked": False})
                        st.error("Reported. We'll update this number.")
    else:
        st.info("No local contacts found. Use national numbers above — they work everywhere.")

    # WhatsApp share
    st.divider()
    st.subheader("📤 Share with Family")
    if "location" in data:
        loc = data["location"]
        share_text = (
            f"ACCIDENT NEAR {loc.get('display_name','my location')}\n"
            f"Call 112 immediately.\n"
            f"Nearest hospital: {nearby[0]['name'] if nearby else 'see 112'} "
            f"({nearby[0].get('distance_km','?')} km)\n"
            f"Phone: {nearby[0].get('phone','108') if nearby else '108'}"
        )
        wa_url = f"https://wa.me/?text={requests.utils.quote(share_text)}"
        st.markdown(f"[📲 Share on WhatsApp]({wa_url})")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("ℹ️ About RoadSoS")
    st.markdown("""
**Always reliable numbers:**
- 🚨 **112** — All emergencies
- 🚑 **108** — Ambulance
- 🛣️ **1033** — NHAI helpline

**Confidence system:**
- ✅ Green (80-100%) — Verified working
- ⚠️ Amber (50-79%) — Possibly working
- ❌ Red (<50%) — May be outdated

**If a number fails:** Tap "Didn't work" to help improve the data — and always fall back to **112**.

---
Built for IIT Madras Road Safety Hackathon 2026
    """)
    st.caption("Works offline for 66 National Highways + top 50 Indian cities")
