"""
Geocoding — converts text location to lat/lon.
Uses Nominatim (OSM geocoder) — free, no API key.
Falls back to user-provided coordinates if text geocoding fails.
"""

import requests
from functools import lru_cache

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
REVERSE_URL   = "https://nominatim.openstreetmap.org/reverse"
HEADERS = {"User-Agent": "RoadSoS-Emergency-App/1.0 (roadsos@team.in)"}


@lru_cache(maxsize=512)
def geocode(location_text: str, country_bias: str = "IN") -> dict | None:
    """
    Converts a location string like 'near Hosur on NH-44' to lat/lon.
    Returns dict with lat, lon, display_name, country_code or None.
    """
    params = {
        "q":              location_text,
        "format":         "json",
        "limit":          1,
        "countrycodes":   country_bias.lower(),
        "addressdetails": 1,
    }
    try:
        resp = requests.get(NOMINATIM_URL, params=params, headers=HEADERS, timeout=10)
        results = resp.json()
        if not results:
            # Retry without country bias
            params.pop("countrycodes")
            resp = requests.get(NOMINATIM_URL, params=params, headers=HEADERS, timeout=10)
            results = resp.json()

        if results:
            r = results[0]
            addr = r.get("address", {})
            return {
                "lat":          float(r["lat"]),
                "lon":          float(r["lon"]),
                "display_name": r.get("display_name", ""),
                "city":         addr.get("city") or addr.get("town") or addr.get("village"),
                "state":        addr.get("state"),
                "country_code": addr.get("country_code", "").upper(),
                "postcode":     addr.get("postcode"),
            }
    except Exception as e:
        print(f"[Geocoder] Error: {e}")
    return None


def reverse_geocode(lat: float, lon: float) -> dict | None:
    """Converts lat/lon to human-readable location info."""
    params = {"lat": lat, "lon": lon, "format": "json", "addressdetails": 1}
    try:
        resp = requests.get(REVERSE_URL, params=params, headers=HEADERS, timeout=10)
        data = resp.json()
        addr = data.get("address", {})
        return {
            "display_name": data.get("display_name", ""),
            "city":         addr.get("city") or addr.get("town") or addr.get("village"),
            "state":        addr.get("state"),
            "country_code": addr.get("country_code", "").upper(),
            "road":         addr.get("road"),
            "postcode":     addr.get("postcode"),
        }
    except Exception as e:
        print(f"[Geocoder] Reverse error: {e}")
    return None


def extract_location_from_text(text: str) -> str:
    """
    Simple heuristic to extract a location from free text.
    e.g. 'accident near Hosur on NH-44' -> 'Hosur NH-44 India'
    The NLU module (chatbot/nlu.py) handles this better with LLM.
    """
    # Common Indian highway patterns
    import re
    nh_match = re.search(r'(NH[-\s]?\d+|SH[-\s]?\d+)', text, re.IGNORECASE)
    nh = nh_match.group(0) if nh_match else ""

    # Strip common accident phrases
    clean = re.sub(
        r'\b(accident|crash|breakdown|near|on|the|a|an|i am|i\'m|there is|help|sos|emergency)\b',
        ' ', text, flags=re.IGNORECASE
    ).strip()
    clean = re.sub(r'\s+', ' ', clean)

    return f"{clean} {nh} India".strip()
