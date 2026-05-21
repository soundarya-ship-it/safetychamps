"""
Natural Language Understanding — powered by Groq (Llama-3.1-8B-Instant).
Free tier: 14,400 requests/day. No cost.
Parses user messages into structured intent + location.
"""

import os
import json

try:
    from groq import Groq
    _groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))
except ImportError:
    _groq_client = None

SYSTEM_PROMPT = """You are RoadSoS, an emergency AI assistant for road accident victims in India.
Your job is to quickly extract structured information from the user's message.

Respond ONLY with valid JSON in this exact format:
{
  "location_text": "<extracted location or landmark or highway>",
  "lat": <float or null>,
  "lon": <float or null>,
  "urgency": "critical|high|medium|low",
  "services_needed": ["hospital", "ambulance", "police", "towing", "puncture", "fire"],
  "severity_hint": "<brief description of situation>",
  "language": "en|ta|hi|te|kn|ml|bn|other",
  "on_highway": true or false,
  "highway_name": "<NH-44 etc. or null>"
}

Rules:
- urgency=critical: injuries, unconscious person, fire, multiple vehicles
- urgency=high: single injured person, broken down on highway
- urgency=medium: breakdown, puncture, no injuries
- urgency=low: information request, planning
- Always include ambulance + hospital if urgency is critical or high
- Always include police if urgency is critical
- If user mentions highway or NH, set on_highway=true
- Detect language from the message
"""


def parse_user_message(message: str) -> dict:
    """
    Parses a user's natural language message into structured intent.
    Falls back to safe defaults if LLM fails.
    """
    if not _groq_client or not _groq_client.api_key:
        return _fallback_parse(message)

    try:
        response = _groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": message},
            ],
            temperature=0.1,
            max_tokens=300,
        )
        raw = response.choices[0].message.content.strip()
        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw)

    except Exception as e:
        print(f"[NLU] Groq error: {e}")
        return _fallback_parse(message)


def _fallback_parse(message: str) -> dict:
    """Rule-based fallback when Groq is unavailable (offline mode)."""
    msg_lower = message.lower()

    urgency = "medium"
    if any(w in msg_lower for w in ["blood", "unconscious", "not breathing", "fire", "critical", "dying"]):
        urgency = "critical"
    elif any(w in msg_lower for w in ["injured", "hurt", "accident", "crash", "hit"]):
        urgency = "high"
    elif any(w in msg_lower for w in ["breakdown", "puncture", "flat tyre", "tow"]):
        urgency = "medium"

    services = []
    if urgency in ("critical", "high"):
        services = ["hospital", "ambulance", "police"]
    elif "puncture" in msg_lower or "tyre" in msg_lower:
        services = ["puncture", "towing"]
    elif "breakdown" in msg_lower or "tow" in msg_lower:
        services = ["towing"]
    else:
        services = ["hospital", "ambulance", "police"]

    import re
    nh_match = re.search(r'(NH[-\s]?\d+|SH[-\s]?\d+)', message, re.IGNORECASE)

    return {
        "location_text":   message,
        "lat":             None,
        "lon":             None,
        "urgency":         urgency,
        "services_needed": services,
        "severity_hint":   "Extracted via fallback rules",
        "language":        "en",
        "on_highway":      bool(nh_match),
        "highway_name":    nh_match.group(0) if nh_match else None,
    }


def build_response_message(contacts: list, intent: dict, golden_hour: dict) -> str:
    """
    Generates a human-readable emergency response message.
    Used when the app is in text-only mode (no rich UI).
    """
    urgency = intent.get("urgency", "medium")
    location = intent.get("location_text", "your location")

    lines = []

    if urgency == "critical":
        lines.append(f"CRITICAL EMERGENCY near {location}")
        lines.append("CALL 112 NOW - national emergency (police + ambulance + fire)")
        lines.append("")

    elif urgency == "high":
        lines.append(f"Emergency near {location}")
        lines.append("Call 108 (ambulance) or 112 (all services) immediately")
        lines.append("")

    if golden_hour.get("status") == "red":
        lines.append(f"Golden Hour Alert: Nearest help is {golden_hour['eta_min']} min away. Act now.")
        lines.append("")

    lines.append("Nearest contacts:")
    for i, c in enumerate(contacts[:5], 1):
        conf = c.get("confidence", 0)
        status = "VERIFIED" if conf >= 80 else ("LIKELY OK" if conf >= 50 else "UNVERIFIED")
        phone_display = c.get("phone") or "No number listed"
        lines.append(f"{i}. [{status}] {c['name']} ({c.get('distance_km', '?')} km)")
        lines.append(f"   Phone: {phone_display}")
        if c.get("phone_alt"):
            lines.append(f"   Alt:   {c['phone_alt']}")

    lines.append("")
    lines.append("Always try 112 if local numbers don't answer.")
    return "\n".join(lines)
