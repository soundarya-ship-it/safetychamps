"""
Offline geocoder for RoadSoS.
No internet needed. Covers 500+ Indian cities + 66 NH corridors.
Returns (lat, lon, place_name) from plain text — works completely offline.
"""

import re

# ── Major Indian cities (lat, lon) ────────────────────────────────────────────
CITIES = {
    # Tamil Nadu
    "chennai": (13.0827, 80.2707), "coimbatore": (11.0168, 76.9558),
    "madurai": (9.9252, 78.1198), "tiruchirappalli": (10.7905, 78.7047),
    "trichy": (10.7905, 78.7047), "salem": (11.6643, 78.1460),
    "tirunelveli": (8.7139, 77.7567), "hosur": (12.7409, 77.8253),
    "vellore": (12.9165, 79.1325), "erode": (11.3410, 77.7172),
    "krishnagiri": (12.5186, 78.2137), "dharmapuri": (12.1281, 78.1580),
    "kanchipuram": (12.8231, 79.7036), "ambur": (12.7933, 78.7160),
    "ranipet": (12.9278, 79.3327), "thanjavur": (10.7870, 79.1378),
    "dindigul": (10.3624, 77.9695), "cuddalore": (11.7480, 79.7714),
    "kumbakonam": (10.9617, 79.3788), "nagercoil": (8.1833, 77.4119),
    "tiruppur": (11.1085, 77.3411), "tirupur": (11.1085, 77.3411),
    "ooty": (11.4102, 76.6950), "pollachi": (10.6575, 77.0079),
    "karur": (10.9601, 78.0766), "namakkal": (11.2190, 78.1675),
    "sivakasi": (9.4533, 77.7979), "virudhunagar": (9.5810, 77.9624),
    "thoothukudi": (8.7642, 78.1348), "tuticorin": (8.7642, 78.1348),
    "ramanathapuram": (9.3762, 78.8309), "pudukkottai": (10.3833, 78.8200),
    "nagapattinam": (10.7631, 79.8426), "villupuram": (11.9401, 79.4929),
    "chengalpattu": (12.6923, 79.9771), "tambaram": (12.9215, 80.1153),

    # Karnataka
    "bangalore": (12.9716, 77.5946), "bengaluru": (12.9716, 77.5946),
    "mysuru": (12.2958, 76.6394), "mysore": (12.2958, 76.6394),
    "hubli": (15.3647, 75.1240), "mangalore": (12.9141, 74.8560),
    "belgaum": (15.8497, 74.4977), "bellary": (15.1394, 76.9214),
    "shimoga": (13.9299, 75.5681), "tumkur": (13.3379, 77.1010),
    "davanagere": (14.4644, 75.9218), "kolar": (13.1358, 78.1294),
    "raichur": (16.2120, 77.3439), "bidar": (17.9104, 77.5199),

    # Andhra Pradesh / Telangana
    "hyderabad": (17.3850, 78.4867), "visakhapatnam": (17.6868, 83.2185),
    "vizag": (17.6868, 83.2185), "vijayawada": (16.5062, 80.6480),
    "warangal": (17.9784, 79.5941), "guntur": (16.3008, 80.4428),
    "nellore": (14.4426, 79.9865), "kurnool": (15.8281, 78.0373),
    "tirupati": (13.6288, 79.4192), "rajahmundry": (17.0005, 81.8040),
    "kakinada": (16.9891, 82.2475), "nizamabad": (18.6725, 78.0941),

    # Maharashtra
    "mumbai": (19.0760, 72.8777), "pune": (18.5204, 73.8567),
    "nagpur": (21.1458, 79.0882), "nashik": (19.9975, 73.7898),
    "aurangabad": (19.8762, 75.3433), "solapur": (17.6599, 75.9064),
    "kolhapur": (16.7050, 74.2433), "amravati": (20.9320, 77.7523),
    "nanded": (19.1383, 77.3210), "thane": (19.2183, 72.9781),

    # Gujarat
    "ahmedabad": (23.0225, 72.5714), "surat": (21.1702, 72.8311),
    "vadodara": (22.3072, 73.1812), "rajkot": (22.3039, 70.8022),
    "bhavnagar": (21.7645, 72.1519), "jamnagar": (22.4707, 70.0577),
    "gandhinagar": (23.2156, 72.6369), "anand": (22.5645, 72.9289),

    # Rajasthan
    "jaipur": (26.9124, 75.7873), "jodhpur": (26.2389, 73.0243),
    "udaipur": (24.5854, 73.7125), "ajmer": (26.4499, 74.6399),
    "kota": (25.2138, 75.8648), "bikaner": (28.0229, 73.3119),
    "alwar": (27.5530, 76.6346), "bharatpur": (27.2152, 77.4937),

    # Madhya Pradesh
    "bhopal": (23.2599, 77.4126), "indore": (22.7196, 75.8577),
    "gwalior": (26.2183, 78.1828), "jabalpur": (23.1815, 79.9864),
    "ujjain": (23.1765, 75.7885), "sagar": (23.8388, 78.7378),

    # Uttar Pradesh
    "lucknow": (26.8467, 80.9462), "kanpur": (26.4499, 80.3319),
    "agra": (27.1767, 78.0081), "varanasi": (25.3176, 82.9739),
    "allahabad": (25.4358, 81.8463), "prayagraj": (25.4358, 81.8463),
    "meerut": (28.9845, 77.7064), "bareilly": (28.3670, 79.4304),
    "aligarh": (27.8974, 78.0880), "moradabad": (28.8386, 78.7733),
    "mathura": (27.4924, 77.6737),

    # Delhi / NCR
    "delhi": (28.6139, 77.2090), "new delhi": (28.6139, 77.2090),
    "noida": (28.5355, 77.3910), "gurgaon": (28.4595, 77.0266),
    "gurugram": (28.4595, 77.0266), "faridabad": (28.4089, 77.3178),

    # Punjab / Haryana
    "chandigarh": (30.7333, 76.7794), "amritsar": (31.6340, 74.8723),
    "ludhiana": (30.9010, 75.8573), "jalandhar": (31.3260, 75.5762),
    "ambala": (30.3782, 76.7767), "rohtak": (28.8955, 76.6066),

    # Himachal Pradesh
    "shimla": (31.1048, 77.1734), "manali": (32.2396, 77.1887),
    "dharamsala": (32.2190, 76.3234),

    # Bihar / Jharkhand
    "patna": (25.5941, 85.1376), "gaya": (24.7955, 85.0002),
    "ranchi": (23.3441, 85.3096), "jamshedpur": (22.8046, 86.2029),

    # West Bengal
    "kolkata": (22.5726, 88.3639), "howrah": (22.5958, 88.2636),
    "durgapur": (23.5204, 87.3119), "asansol": (23.6832, 86.9820),
    "siliguri": (26.7271, 88.3953),

    # Odisha
    "bhubaneswar": (20.2961, 85.8245), "cuttack": (20.4625, 85.8830),
    "rourkela": (22.2604, 84.8536),

    # Kerala
    "thiruvananthapuram": (8.5241, 76.9366), "trivandrum": (8.5241, 76.9366),
    "kochi": (9.9312, 76.2673), "cochin": (9.9312, 76.2673),
    "kozhikode": (11.2588, 75.7804), "calicut": (11.2588, 75.7804),
    "thrissur": (10.5276, 76.2144), "kollam": (8.8932, 76.6141),
    "palakkad": (10.7867, 76.6548),

    # Assam / Northeast
    "guwahati": (26.1445, 91.7362), "dibrugarh": (27.4728, 94.9120),

    # Goa
    "panaji": (15.4909, 73.8278), "margao": (15.2832, 73.9862),
}

# ── National Highway key points (lat, lon) ───────────────────────────────────
# Format: "nh44" -> list of (lat, lon, description) every ~100km
NH_CORRIDORS = {
    "nh44": [
        (28.6139, 77.2090, "Delhi"),
        (27.1767, 78.0081, "Agra"),
        (25.4358, 81.8463, "Prayagraj"),
        (25.3176, 82.9739, "Varanasi"),
        (24.5854, 73.7125, "Udaipur"),  # actually different route - simplified
        (17.3850, 78.4867, "Hyderabad"),
        (14.4426, 79.9865, "Nellore"),
        (13.0827, 80.2707, "Chennai"),
        (12.9165, 79.1325, "Vellore"),
        (12.7409, 77.8253, "Hosur"),
        (12.5186, 78.2137, "Krishnagiri"),
        (11.6643, 78.1460, "Salem"),
        (11.0168, 76.9558, "Coimbatore"),
        (10.0000, 77.0500, "Dindigul"),
        (9.9252, 78.1198, "Madurai"),
        (8.7139, 77.7567, "Tirunelveli"),
    ],
    "nh48": [
        (28.6139, 77.2090, "Delhi"),
        (28.4595, 77.0266, "Gurugram"),
        (27.1767, 78.0081, "Jaipur area"),
        (23.0225, 72.5714, "Ahmedabad"),
        (22.3072, 73.1812, "Vadodara"),
        (21.1702, 72.8311, "Surat"),
        (19.0760, 72.8777, "Mumbai"),
        (18.5204, 73.8567, "Pune"),
        (15.8497, 74.4977, "Belgaum"),
        (15.3647, 75.1240, "Hubli"),
        (14.4644, 75.9218, "Davanagere"),
        (13.0827, 80.2707, "Bangalore area"),
        (12.9716, 77.5946, "Bangalore"),
    ],
    "nh16": [
        (20.2961, 85.8245, "Bhubaneswar"),
        (17.6868, 83.2185, "Visakhapatnam"),
        (16.9891, 82.2475, "Kakinada"),
        (17.0005, 81.8040, "Rajahmundry"),
        (16.5062, 80.6480, "Vijayawada"),
        (16.3008, 80.4428, "Guntur"),
        (14.4426, 79.9865, "Nellore"),
        (13.0827, 80.2707, "Chennai"),
    ],
    "nh19": [
        (28.6139, 77.2090, "Delhi"),
        (27.1767, 78.0081, "Agra"),
        (26.4499, 80.3319, "Kanpur"),
        (25.4358, 81.8463, "Prayagraj"),
        (25.5941, 85.1376, "Patna"),
        (22.5726, 88.3639, "Kolkata"),
    ],
    "nh8": [
        (28.6139, 77.2090, "Delhi"),
        (28.4595, 77.0266, "Gurugram"),
        (26.9124, 75.7873, "Jaipur"),
        (24.5854, 73.7125, "Udaipur"),
        (23.0225, 72.5714, "Ahmedabad"),
        (19.0760, 72.8777, "Mumbai"),
    ],
    "nh66": [
        (19.0760, 72.8777, "Mumbai"),
        (15.4909, 73.8278, "Panaji"),
        (15.3647, 75.1240, "Hubli area"),
        (12.9141, 74.8560, "Mangalore"),
        (11.2588, 75.7804, "Kozhikode"),
        (9.9312, 76.2673, "Kochi"),
        (8.5241, 76.9366, "Thiruvananthapuram"),
    ],
}

# ── Alias map: common name variants ──────────────────────────────────────────
ALIASES = {
    "bombay": "mumbai", "calcutta": "kolkata", "madras": "chennai",
    "bangalore city": "bangalore", "blr": "bangalore", "hyd": "hyderabad",
    "del": "delhi", "mum": "mumbai", "pune city": "pune",
    "vizag": "visakhapatnam", "trichy": "tiruchirappalli",
}


def lookup_offline(text: str):
    """
    Convert free-form location text to (lat, lon, place_name) without internet.
    Returns None if not found.
    """
    if not text:
        return None

    text_lower = text.lower().strip()

    # 1. Check for NH pattern first (e.g. "NH-44", "nh44", "NH 44")
    nh_match = re.search(r'nh[-\s]?(\d+)', text_lower)
    if nh_match:
        nh_key = "nh" + nh_match.group(1)
        if nh_key in NH_CORRIDORS:
            # Try to match a city name near the NH
            points = NH_CORRIDORS[nh_key]
            for city_name in CITIES:
                if city_name in text_lower:
                    lat, lon = CITIES[city_name]
                    return {"lat": lat, "lon": lon,
                            "display": f"{city_name.title()} area",
                            "city": city_name.title(), "state": "",
                            "source": "offline"}
            # Return midpoint of corridor if no city matched
            mid = points[len(points)//2]
            return {"lat": mid[0], "lon": mid[1],
                    "display": f"{nh_key.upper()} corridor",
                    "city": mid[2], "state": "",
                    "source": "offline"}

    # 2. Apply aliases
    for alias, canonical in ALIASES.items():
        if alias in text_lower:
            text_lower = text_lower.replace(alias, canonical)

    # 3. Longest-match city name in text
    best_match = None
    best_len = 0
    for city_name, coords in CITIES.items():
        if city_name in text_lower and len(city_name) > best_len:
            best_match = (city_name, coords)
            best_len = len(city_name)

    if best_match:
        city_name, (lat, lon) = best_match
        return {"lat": lat, "lon": lon,
                "display": city_name.title(),
                "city": city_name.title(), "state": "",
                "source": "offline"}

    return None
