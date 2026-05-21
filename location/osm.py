"""
OpenStreetMap Overpass API — location data engine.
Fetches hospitals, police stations, ambulances, towing, puncture shops.
Free, global, no API key required.
"""

import requests
import math
from typing import Optional

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Amenity tags to query per service category
CATEGORY_TAGS = {
    "hospital":   [("amenity", "hospital"), ("amenity", "clinic"), ("healthcare", "hospital")],
    "ambulance":  [("emergency", "ambulance_station"), ("amenity", "ambulance_station")],
    "police":     [("amenity", "police")],
    "pharmacy":   [("amenity", "pharmacy")],
    "fire":       [("amenity", "fire_station")],
    "towing":     [("shop", "car_repair"), ("amenity", "car_repair")],
    "puncture":   [("shop", "bicycle"), ("shop", "tyres"), ("shop", "car_repair")],
    "fuel":       [("amenity", "fuel")],
    "trauma":     [("trauma", "yes"), ("emergency", "yes"), ("healthcare:speciality", "trauma_surgery")],
}


def build_overpass_query(lat: float, lon: float, radius_m: int, categories: list[str]) -> str:
    """Builds an Overpass QL query for multiple categories around a point."""
    parts = []
    # For trauma, add an extra name-based search to catch MoRTH trauma centres
    if "trauma" in categories:
        parts.append(f'node["amenity"="hospital"]["name"~"[Tt]rauma",i](around:{radius_m},{lat},{lon});')
        parts.append(f'way["amenity"="hospital"]["name"~"[Tt]rauma",i](around:{radius_m},{lat},{lon});')
        parts.append(f'node["amenity"="hospital"]["emergency"="yes"](around:{radius_m},{lat},{lon});')
        parts.append(f'way["amenity"="hospital"]["emergency"="yes"](around:{radius_m},{lat},{lon});')
    for cat in categories:
        for tag_key, tag_val in CATEGORY_TAGS.get(cat, []):
            parts.append(f'node["{tag_key}"="{tag_val}"](around:{radius_m},{lat},{lon});')
            parts.append(f'way["{tag_key}"="{tag_val}"](around:{radius_m},{lat},{lon});')

    union = "\n".join(parts)
    return f"""
[out:json][timeout:30];
(
{union}
);
out body center;
"""


def fetch_nearby(
    lat: float,
    lon: float,
    radius_m: int = 10000,
    categories: Optional[list[str]] = None,
    timeout: int = 20,
) -> list[dict]:
    """
    Queries Overpass API for emergency contacts near (lat, lon).
    Returns a list of dicts with name, phone, category, distance, coordinates.
    """
    if categories is None:
        categories = ["hospital", "ambulance", "police", "towing", "puncture"]

    query = build_overpass_query(lat, lon, radius_m, categories)

    try:
        resp = requests.post(OVERPASS_URL, data={"data": query}, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"[OSM] Overpass error: {e}")
        return []

    results = []
    for element in data.get("elements", []):
        tags = element.get("tags", {})
        name = tags.get("name") or tags.get("name:en") or tags.get("operator")
        if not name:
            continue

        phone = (
            tags.get("phone")
            or tags.get("contact:phone")
            or tags.get("emergency:phone")
            or tags.get("telephone")
        )

        # Resolve coordinates (ways have 'center', nodes have direct lat/lon)
        el_lat = element.get("lat") or (element.get("center") or {}).get("lat")
        el_lon = element.get("lon") or (element.get("center") or {}).get("lon")

        if not el_lat or not el_lon:
            continue

        dist_m = haversine_m(lat, lon, el_lat, el_lon)
        category = _infer_category(tags)

        results.append({
            "name":         name,
            "phone":        phone,
            "phone_alt":    tags.get("contact:phone:2"),
            "address":      _build_address(tags),
            "lat":          el_lat,
            "lon":          el_lon,
            "distance_m":  round(dist_m),
            "distance_km": round(dist_m / 1000, 1),
            "category":    category,
            "tier":        3,
            "source":      "osm",
            "osm_id":      element.get("id"),
            "tags":         tags,
        })

    # Sort by distance
    results.sort(key=lambda x: x["distance_m"])
    return results


def _infer_category(tags: dict) -> str:
    amenity = tags.get("amenity", "")
    emergency = tags.get("emergency", "")
    shop = tags.get("shop", "")
    healthcare = tags.get("healthcare", "")

    if tags.get("trauma") == "yes": return "trauma"
    if healthcare == "trauma_surgery" or tags.get("healthcare:speciality","") == "trauma_surgery": return "trauma"
    name_lower = tags.get("name","").lower()
    if "trauma" in name_lower: return "trauma"
    if amenity == "hospital" and emergency == "yes": return "trauma"
    if amenity == "hospital" or healthcare == "hospital": return "hospital"
    if amenity == "clinic":  return "hospital"
    if "ambulance" in amenity or "ambulance" in emergency: return "ambulance"
    if amenity == "police":  return "police"
    if amenity == "pharmacy": return "pharmacy"
    if amenity == "fire_station": return "fire"
    if shop in ("tyres", "bicycle"): return "puncture"
    if "car_repair" in amenity or "car_repair" in shop: return "towing"
    if amenity == "fuel":    return "fuel"
    return "other"


def _build_address(tags: dict) -> str:
    parts = []
    for key in ["addr:housenumber", "addr:street", "addr:city", "addr:state", "addr:postcode"]:
        val = tags.get(key)
        if val:
            parts.append(val)
    return ", ".join(parts) if parts else tags.get("addr:full", "")


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in metres between two lat/lon points."""
    R = 6_371_000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi  = math.radians(lat2 - lat1)
    dlam  = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
