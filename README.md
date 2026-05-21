# RoadSoS — Emergency AI Assistant

**National Road Safety Hackathon 2026 | IIT Madras CoERS**
**Team: Soundarya Lakshmi Narayanan · Shreya · Ashwin**

---

## What It Does

RoadSoS is an AI-powered emergency assistant for road accident victims in India.
When someone is in distress, they type (or speak) what happened — and the app instantly:

1. **Parses the emergency** using AI (Groq/Llama 3.1) or smart rule-based fallback
2. **Finds nearest verified contacts** — hospitals, ambulances, police — with confidence scores
3. **Calculates a Golden Hour Score** — how long until help arrives vs. the 60-minute survival window
4. **Recommends who to call first** with exact numbers (always shows 112/108 at the top)
5. **Works offline** — Tier 1 national numbers (112, 108, 1033) are hardcoded and never need internet

---

## Quick Start (Windows)

**Double-click `start.bat`** — it handles everything automatically.

Or run manually:

```
pip install -r requirements.txt
copy .env.example .env
REM Edit .env to add your GROQ_API_KEY (free — see below)
python database/init_db.py
streamlit run app.py
```

Open: **http://localhost:8501**

---

## Getting a Free Groq API Key (30 seconds)

1. Go to https://console.groq.com
2. Sign up (free, no credit card)
3. Click "Create API Key"
4. Copy it into `.env` as `GROQ_API_KEY=gsk_your_key_here`

Without a key, the app still works using smart rule-based parsing.

---

## Project Structure

```
roadsos/
├── app.py                   <- MAIN ENTRY POINT (streamlit run app.py)
├── start.bat                <- Windows one-click launcher
├── requirements.txt
├── .env.example             <- Copy to .env and add your keys
├── database/
│   ├── schema.sql           <- SQLite schema (contacts, national_numbers, feedback)
│   └── init_db.py           <- Seeds 32 verified contacts + 46 country numbers
├── chatbot/
│   ├── nlu.py               <- AI message parser (Groq) + rule-based fallback
│   └── triage.py            <- Golden Hour Score + call order triage
├── contacts/
│   ├── national.py          <- Tier 1: hardcoded numbers (112, 108, 1033, 100...)
│   └── confidence.py        <- 0-100 confidence scoring engine
├── location/
│   ├── osm.py               <- OpenStreetMap Overpass API (free, no key needed)
│   └── geocoder.py          <- Nominatim geocoding (free, no key needed)
└── verification/
    └── verifier.py          <- Automated verification + user feedback loop
```

---

## The Core Innovation: Verified Contact Numbers

Emergency numbers in India are **unreliable**. Local hospital lines go dead.
RoadSoS solves this with a three-tier confidence system:

| Tier | Source | Confidence | How Verified |
|------|--------|-----------|--------------|
| 1 | Govt mandated (112, 108, 1033) | 100 — always shown | Government mandated. Hardcoded. Never filtered. |
| 2 | State hospitals, NHP verified | 80-95 | Cross-checked NHP + state police websites |
| 3 | Local OSM / Google Maps | 35-75 | Automated weekly ping + user feedback |

**Confidence score (0–100):**
- Base score from source reliability
- +8 if verified in the last 30 days
- +10 if confirmed by multiple sources
- -25 per automated verification failure
- -20 per user "Didn't work" report
- Auto-deactivated after 3 user failures + score below 30

**User feedback loop (real-world signal):**
- Every contact card has "Worked" and "Didn't work" buttons
- Feedback updates confidence immediately
- 3 "didn't work" reports + confidence < 30 → number deactivated automatically

---

## Golden Hour Score

Road accident survival drops sharply after 60 minutes. RoadSoS shows:

- **Green (<=15 min):** Help can arrive in time. Stay calm, wait for ambulance.
- **Amber (16–30 min):** Act quickly. Start first aid if trained.
- **Red (>30 min):** Critical. Call 112 NOW. Begin transport toward nearest hospital.

ETA is calculated from the nearest hospital's distance using road-speed assumptions
(80 km/h highway, 50 km/h rural, 30 km/h city).

---

## Supported Languages

The AI parser detects: English, Tamil, Hindi, Telugu, Kannada, Malayalam, Bengali.
Rule-based fallback works for any language using keyword detection.

---

## Technology Stack

| Component | Technology | Cost |
|-----------|-----------|------|
| UI | Streamlit | Free |
| AI / NLU | Groq + Llama 3.1-8B | Free (14,400 req/day) |
| Geocoding | Nominatim (OSM) | Free, no key |
| Nearby contacts | OpenStreetMap Overpass API | Free, no key |
| Database | SQLite (offline-capable) | Free |
| Verification | NHP API + user feedback | Free |

**Zero cost to run. Works offline for critical features.**

---

## Team

- **Soundarya Lakshmi Narayanan** — Backend architecture, NLU, confidence scoring
- **Shreya** — UI/UX, Streamlit frontend, demo flow
- **Ashwin** — Data engineering, highway corridor data, verification pipeline
