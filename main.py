"""
RoadSoS — FastAPI Backend
Entry point for the emergency contact API.

Run: uvicorn main:app --reload
Docs: http://localhost:8000/docs
"""

import sqlite3
import os
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from location.geocoder import geocode, reverse_geocode, extract_location_from_text
from location.osm import fetch_nearby, haversine_m
from contacts.national import get_india_numbers, get_international_numbers
from contacts.confidence import confidence_label, should_show_fallback_warning
from chatbot.nlu import parse_user_message, build_response_message
from chatbot.triage import compute_golden_hour_score, triage_severity
from verification.verifier import handle_user_feedback

DB_PATH = os.environ.get("ROADSOS_DB", "roadsos.db")

app = FastAPI(
    title="RoadSoS API",
    description="Emergency contact finder for road accident victims. AI-powered, offline-capable.",
    version="1.0.0",
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


# ── Models ────────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    lat:     Optional[float] = None
    lon:     Optional[float] = None
    session_id: Optional[str] = None

class FeedbackRequest(BaseModel):
    contact_id: int
    worked:     bool
    session_id: Optional[str] = None


# ── Core endpoint: the main chat interface ────────────────────────────────────

@app.post("/chat")
def chat(req: ChatRequest):
    """
    Main endpoint. Accepts a natural language message + optional coords.
    Returns: triage advice, national numbers, nearby contacts with confidence scores.
    """
    # Step 1: Parse intent
    intent = parse_user_message(req.message)

    # Step 2: Resolve location
    lat, lon = req.lat, req.lon
    if not lat or not lon:
        if intent.get("lat") and intent.get("lon"):
            lat, lon = intent["lat"], intent["lon"]
        else:
            loc_text = extract_location_from_text(intent.get("location_text") or req.message)
            geo = geocode(loc_text)
            if geo:
                lat, lon = geo["lat"], geo["lon"]

    if not lat or not lon:
        return {
            "error": "Could not determine location. Please share your GPS coordinates or type a landmark.",
            "fallback": {
                "message": "Without location, always call: 112 (National Emergency) or 108 (Ambulance)",
                "numbers": get_india_numbers(on_highway=False),
            }
        }

    # Step 3: Determine country
    country_info = reverse_geocode(lat, lon) or {}
    country_code = country_info.get("country_code", "IN")
    on_highway   = intent.get("on_highway", False)

    # Step 4: Tier 1 — always show national numbers first
    if country_code == "IN":
        national = get_india_numbers(on_highway=on_highway)
    else:
        national = get_international_numbers(country_code)

    # Step 5: Tier 2+3 — nearby contacts from OSM + DB
    categories = intent.get("services_needed") or ["hospital", "ambulance", "police"]
    radius_m   = 20000 if on_highway else 10000
    osm_results = fetch_nearby(lat, lon, radius_m=radius_m, categories=categories)

    # Step 6: Merge DB contacts (Tier 2) with OSM (Tier 3)
    db_contacts = _query_db_contacts(lat, lon, radius_m, categories)
    all_local   = _merge_and_rank(db_contacts, osm_results)

    # Step 7: Golden Hour Score
    nearest_hospital_km = next(
        (c["distance_km"] for c in all_local if c["category"] == "hospital"), 15.0
    )
    golden_hour = compute_golden_hour_score(
        nearest_hospital_km, on_highway=on_highway,
        is_rural=(country_info.get("city") is None)
    )

    # Step 8: Triage
    triage = triage_severity(
        req.message, intent.get("urgency", "medium"), categories
    )

    # Step 9: Attach confidence labels to local contacts
    for c in all_local:
        c["confidence_meta"] = confidence_label(c.get("confidence", 50))
        c["show_fallback_warning"] = should_show_fallback_warning(c.get("confidence", 50))

    return {
        "intent":            intent,
        "location":          {"lat": lat, "lon": lon, **country_info},
        "golden_hour":       golden_hour,
        "triage":            triage,
        "national_numbers":  national,
        "nearby_contacts":   all_local[:10],
        "total_found":       len(all_local),
        "text_summary":      build_response_message(
                                 national[:3] + all_local[:3], intent, golden_hour
                             ),
    }


# ── Simple search without chat ─────────────────────────────────────────────────

@app.get("/nearby")
def nearby(
    lat:        float = Query(...),
    lon:        float = Query(...),
    radius_km:  float = Query(10),
    categories: str   = Query("hospital,ambulance,police"),
):
    """Direct location-based search. No NLU processing."""
    cats = [c.strip() for c in categories.split(",")]
    results = fetch_nearby(lat, lon, radius_m=int(radius_km * 1000), categories=cats)
    db_res  = _query_db_contacts(lat, lon, int(radius_km * 1000), cats)
    merged  = _merge_and_rank(db_res, results)
    for c in merged:
        c["confidence_meta"] = confidence_label(c.get("confidence", 50))
    return {"contacts": merged, "total": len(merged)}


# ── Feedback endpoint ──────────────────────────────────────────────────────────

@app.post("/feedback")
def feedback(req: FeedbackRequest):
    """User reports whether a number worked or not."""
    handle_user_feedback(req.contact_id, req.worked, DB_PATH)
    return {"status": "ok", "message": "Thank you for improving RoadSoS data!"}


# ── Health check ───────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0.0", "offline_ready": os.path.exists(DB_PATH)}


# ── Helpers ────────────────────────────────────────────────────────────────────

def _query_db_contacts(lat: float, lon: float, radius_m: int, categories: list) -> list:
    """Queries the local SQLite DB for cached/verified contacts."""
    if not os.path.exists(DB_PATH):
        return []
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # Bounding box approximation for fast pre-filter (1 deg lat ≈ 111 km)
    delta = radius_m / 111_000
    placeholders = ",".join("?" * len(categories))
    rows = conn.execute(f"""
        SELECT * FROM contacts
        WHERE is_active = 1
          AND lat BETWEEN ? AND ?
          AND lon BETWEEN ? AND ?
          AND category IN ({placeholders})
        ORDER BY confidence DESC
        LIMIT 50
    """, (lat-delta, lat+delta, lon-delta, lon+delta, *categories)).fetchall()
    conn.close()

    results = []
    for row in rows:
        c = dict(row)
        dist = haversine_m(lat, lon, c["lat"], c["lon"])
        if dist <= radius_m:
            c["distance_m"]  = round(dist)
            c["distance_km"] = round(dist / 1000, 1)
            results.append(c)
    return results


def _merge_and_rank(db_contacts: list, osm_contacts: list) -> list:
    """
    Merges DB (Tier 2) and OSM (Tier 3) contacts.
    Deduplicates by proximity (same place within 100m = same contact).
    Ranks by: tier ASC, confidence DESC, distance ASC.
    """
    seen_positions = []
    merged = []

    for c in db_contacts + osm_contacts:
        clat, clon = c.get("lat"), c.get("lon")
        if not clat or not clon:
            merged.append(c)
            continue
        # Deduplicate: skip if another contact is within 100m
        is_dup = any(
            haversine_m(clat, clon, s["lat"], s["lon"]) < 100
            for s in seen_positions
        )
        if not is_dup:
            seen_positions.append({"lat": clat, "lon": clon})
            merged.append(c)

    merged.sort(key=lambda x: (
        x.get("tier", 3),
        -x.get("confidence", 50),
        x.get("distance_m", 999999),
    ))
    return merged
