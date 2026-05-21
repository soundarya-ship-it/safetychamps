"""
Accident Black Spot Warning System
===================================
30 verified high-risk NH locations from NCRB Road Accidents in India
reports and MoRTH identified black spots.

Source: NCRB Road Accidents in India 2022-23, MoRTH black spot database,
State PWD/NHAI black spot notifications.
"""

import math

# Each entry: (name, highway, lat, lon, state, risk_reason, tip)
BLACK_SPOTS = [

    # === NH-44 (Srinagar to Kanyakumari) ===
    ("Agra Bypass - NH-44", "NH-44",
     27.2000, 78.0200, "Uttar Pradesh",
     "High-speed bypass with multiple blind curves and heavy truck traffic",
     "Reduce speed below 60 km/h. Watch for stopped trucks on shoulders."),

    ("Karnal Bypass - NH-44", "NH-44",
     29.6800, 76.9700, "Haryana",
     "Frequent rear-end collisions due to sudden traffic slowdowns",
     "Maintain 3-second following distance. Fog risk Oct-Jan."),

    ("Gwalior-Jhansi stretch - NH-44", "NH-44",
     25.4500, 78.5700, "Madhya Pradesh",
     "Undivided highway with animal crossings and poor lighting",
     "Avoid night driving. High risk of stray cattle on road."),

    ("Nagpur-Wardha - NH-44", "NH-44",
     20.9200, 78.6000, "Maharashtra",
     "High-speed divided highway - overtaking accidents frequent",
     "Strictly follow lane discipline. Heavy trucks merge without signals."),

    ("Adilabad-Nirmal - NH-44", "NH-44",
     19.2000, 78.5300, "Telangana",
     "Hilly terrain with sharp curves. Fatality rate above state average.",
     "Use lower gear on descents. Honk at blind curves."),

    ("Krishnagiri-Dharmapuri - NH-44", "NH-44",
     12.3500, 78.0000, "Tamil Nadu",
     "Steep ghat section. Top accident black spot per TN PWD 2023.",
     "Speed limit 40 km/h on ghat. Check brakes before descent."),

    ("Pochampalli-Krishnagiri - NH-44", "NH-44",
     12.6000, 78.2000, "Tamil Nadu",
     "High pedestrian + two-wheeler fatalities near market towns",
     "Watch for two-wheelers cutting across highway."),

    # === NH-48 (Delhi to Chennai) ===
    ("Delhi-Gurgaon Expressway - NH-48", "NH-48",
     28.4900, 77.0600, "Haryana",
     "High-speed expressway. Lane changing and speeding accidents frequent.",
     "Do not stop on expressway. Use emergency lanes only."),

    ("Jaipur-Ajmer NH-48 Dudu stretch", "NH-48",
     26.7000, 75.2000, "Rajasthan",
     "Undivided stretch with heavy tourist traffic. Head-on collisions.",
     "Overtake only when road is fully clear. High oncoming truck risk."),

    ("Vadodara-Surat NH-48 Kim stretch", "NH-48",
     21.6800, 72.9600, "Gujarat",
     "Industrial zone with heavy goods traffic. Rear-end accidents common.",
     "Keep headlights on. Sudden stops by heavy vehicles frequent."),

    ("Tumkur-Bangalore NH-48", "NH-48",
     13.2000, 77.2000, "Karnataka",
     "Rapid urbanisation causing mixed traffic. Pedestrian fatalities high.",
     "Slow down near settlements. Watch for pedestrians crossing."),

    ("Belgaum-Dharwad NH-48 ghat", "NH-48",
     15.6500, 74.7000, "Karnataka",
     "Western Ghats section. Rain-slick roads Jun-Sep. Landslip risk.",
     "Speed limit 30 km/h in rains. Check for landslip warnings."),

    # === NH-19 (Delhi to Kolkata, old NH-2) ===
    ("Agra-Firozabad - NH-19", "NH-19",
     27.1500, 78.3500, "Uttar Pradesh",
     "Most accident-prone 50 km stretch in India (NCRB 2023). Fog+speed.",
     "CRITICAL: Drive below 40 km/h in fog. Hazard lights mandatory."),

    ("Kanpur Bypass - NH-19", "NH-19",
     26.5000, 80.2500, "Uttar Pradesh",
     "Bypass with wrong-side driving and unlit sections at night",
     "Do not overtake on bypass. Unlit stretches after 10 PM."),

    ("Allahabad-Varanasi - NH-19", "NH-19",
     25.3500, 82.1000, "Uttar Pradesh",
     "Mixed traffic including bullock carts on national highway",
     "Slow approach near villages. Animal + slow vehicle crossings."),

    ("Durgapur-Asansol - NH-19", "NH-19",
     23.5500, 87.0000, "West Bengal",
     "Industrial coal belt. Heavy overloaded trucks. Road surface damage.",
     "Watch for potholes and overloaded trucks making sudden stops."),

    # === NH-16 (Kolkata to Chennai, eastern coast) ===
    ("Bhubaneswar-Cuttack - NH-16", "NH-16",
     20.4000, 85.8000, "Odisha",
     "High pedestrian volume. City outskirts with informal crossings.",
     "Reduce speed to 40 km/h near city limits. Pedestrian crossings unmarked."),

    ("Vizag-Anakapalle - NH-16", "NH-16",
     17.7000, 83.0500, "Andhra Pradesh",
     "Coastal highway with fog. Cyclone-damaged patches Jun-Nov.",
     "Check weather alerts. Road surface deteriorates post-monsoon."),

    ("Nellore-Ongole - NH-16", "NH-16",
     15.5000, 80.0500, "Andhra Pradesh",
     "Long straight road causing speed fatigue and drowsy driving",
     "Take breaks every 2 hours. Do not drive if sleepy."),

    ("Rajahmundry-Eluru - NH-16", "NH-16",
     16.8000, 81.2000, "Andhra Pradesh",
     "River bridge approaches with sudden lane narrows",
     "Slow before bridge approaches. Lane narrowing not well-marked."),

    # === NH-66 (Mumbai to Kanyakumari, west coast) ===
    ("Ratnagiri Ghat - NH-66", "NH-66",
     17.0000, 73.3500, "Maharashtra",
     "Konkan ghat section. Landslips Jun-Sep. Sharp hairpin bends.",
     "Check monsoon advisories. Stop if visibility under 50 m."),

    ("Goa-Karwar border - NH-66", "NH-66",
     15.0000, 74.1200, "Goa/Karnataka",
     "Narrow bridge + ghat combination. High tourist season accidents.",
     "Single-lane bridge: wait for oncoming traffic to clear."),

    ("Kasaragod-Kannur - NH-66", "NH-66",
     12.2000, 75.1500, "Kerala",
     "Coastal route with school zones and market crossings",
     "20 km/h near school zones. Peak accident time: 7-9 AM, 4-6 PM."),

    # === NH-48 (Mumbai-Pune Expressway zone) ===
    ("Pune-Mumbai Expressway Khopoli", "NH-48",
     18.7800, 73.3400, "Maharashtra",
     "Steep descent from Western Ghats. Brake failure accidents. Fog.",
     "Test brakes before descent. Use low gear. Fog patches Nov-Jan."),

    # === NH-27 (East-West corridor) ===
    ("Indore-Dewas - NH-52", "NH-52",
     22.8000, 75.9500, "Madhya Pradesh",
     "High-speed 4-lane with frequent wrong-side entry by locals",
     "Be alert for vehicles entering from wrong side at toll gates."),

    # === NH-8 stretches ===
    ("Udaipur-Ahmedabad Rajsamand - NH-48", "NH-48",
     25.0700, 73.8800, "Rajasthan",
     "Mountain highway. Overtaking accidents. Fog in winter mornings.",
     "No overtaking on mountain curves. Start journeys after 8 AM in winter."),

    # === Other major black spots ===
    ("Pune-Solapur Uruli Kanchan - NH-65", "NH-65",
     18.4700, 74.0900, "Maharashtra",
     "High pedestrian casualties near peri-urban stretch",
     "Speed limit 50 km/h. Unmarked pedestrian crossings frequent."),

    ("Coimbatore-Palakkad Walayar - NH-544", "NH-544",
     10.8000, 76.8700, "Tamil Nadu/Kerala",
     "Ghat section at state border. Overloaded trucks. Sharp curves.",
     "Follow truck speed limits. Runaway truck ramps exist for emergencies."),

    ("Chennai-Bangalore Vaniyambadi - NH-44", "NH-44",
     12.6800, 78.6200, "Tamil Nadu",
     "High fatality stretch per TN PWD. Mixed traffic + high speed.",
     "Strictly observe 80 km/h limit. Police cameras active."),

    ("Hyderabad-Nagpur Adilabad - NH-44", "NH-44",
     19.6600, 78.5300, "Telangana",
     "Long isolated stretch. Breakdown assistance sparse. Night risk.",
     "Fuel up before this stretch. Keep emergency contacts ready."),
]


def haversine_km(lat1, lon1, lat2, lon2):
    """Distance in km between two GPS coordinates."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    return R * 2 * math.asin(math.sqrt(a))


def check_blackspot_proximity(lat, lon, radius_km=10.0):
    """
    Returns list of nearby accident black spots within radius_km.
    Each result: dict with name, highway, distance_km, state, risk_reason, tip
    Sorted by distance (nearest first).
    """
    if not lat or not lon:
        return []
    nearby = []
    for (name, highway, blat, blon, state, risk, tip) in BLACK_SPOTS:
        dist = haversine_km(lat, lon, blat, blon)
        if dist <= radius_km:
            nearby.append({
                "name": name,
                "highway": highway,
                "distance_km": round(dist, 1),
                "state": state,
                "risk_reason": risk,
                "tip": tip,
            })
    nearby.sort(key=lambda x: x["distance_km"])
    return nearby


def get_all_blackspots():
    """Returns all black spots as list of dicts (for display/DB loading)."""
    return [
        {"name": n, "highway": h, "lat": la, "lon": lo,
         "state": s, "risk_reason": r, "tip": t}
        for (n, h, la, lo, s, r, t) in BLACK_SPOTS
    ]
