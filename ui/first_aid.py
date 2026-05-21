"""
First Aid / Golden Hour Guidance for RoadSoS.
100% offline — no API, no internet needed.
Multi-language: en / ta / hi / te / kn

Sources: WHO Prehospital Trauma Care · Indian Red Cross · MoRTH · AHA CPR Guidelines
"""

import streamlit as st

# ── Scenario detection (language-agnostic keywords) ───────────────────────────
SCENARIO_KEYWORDS = {
    "bleeding":    ["bleed", "blood", "cut", "wound", "hemorrhage", "haemorrhage"],
    "unconscious": ["unconscious", "unresponsive", "not responding", "fainted", "passed out",
                    "not waking", "coma", "collapse", "collapsed"],
    "fracture":    ["fracture", "broken", "bone", "limb", "leg", "arm", "cannot move"],
    "spinal":      ["neck", "spine", "spinal", "back injury", "cannot feel", "paralys"],
    "burns":       ["burn", "fire", "flame", "smoke", "scald"],
    "breathing":   ["not breathing", "choking", "breathe", "airway", "cpr", "no pulse"],
    "child":       ["child", "infant", "baby", "kid", "minor", "toddler"],
}


def detect_scenario(text):
    if not text:
        return "general"
    text_lower = text.lower()
    for scenario, keywords in SCENARIO_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            return scenario
    return "general"


# ═════════════════════════════════════════════════════════════════════════════
#  SVG ILLUSTRATIONS  (inline, 100% offline)
# ═════════════════════════════════════════════════════════════════════════════

SVG_CPR = """
<svg viewBox="0 0 320 190" xmlns="http://www.w3.org/2000/svg"
     style="width:100%;max-width:320px;display:block;margin:6px auto">
  <rect width="320" height="190" rx="10" fill="#FFF5F5" stroke="#FECACA" stroke-width="1.5"/>

  <!-- Title -->
  <text x="160" y="22" text-anchor="middle" font-size="12" font-weight="700"
        fill="#DC2626" font-family="system-ui,sans-serif">CPR — Chest Compressions</text>

  <!-- Ground line -->
  <line x1="20" y1="148" x2="300" y2="148" stroke="#E5E7EB" stroke-width="2"/>

  <!-- Person lying flat -->
  <!-- Head -->
  <circle cx="52" cy="122" r="19" fill="#FEF3C7" stroke="#D97706" stroke-width="2"/>
  <!-- Body -->
  <rect x="68" y="110" width="150" height="28" rx="14" fill="#DBEAFE" stroke="#1D4ED8" stroke-width="2"/>
  <!-- Legs -->
  <rect x="215" y="116" width="70" height="18" rx="9" fill="#DBEAFE" stroke="#1D4ED8" stroke-width="2"/>
  <!-- Arms along side -->
  <rect x="80" y="106" width="110" height="8" rx="4" fill="#FCA5A5" stroke="#DC2626" stroke-width="1"/>

  <!-- Hands stacked on chest -->
  <rect x="128" y="92" width="38" height="13" rx="4" fill="#B91C1C" opacity="0.85"/>
  <rect x="130" y="82" width="34" height="13" rx="4" fill="#DC2626"/>

  <!-- Down arrow -->
  <line x1="147" y1="70" x2="147" y2="80" stroke="#DC2626" stroke-width="2.5" stroke-linecap="round"/>
  <polygon points="140,78 147,88 154,78" fill="#DC2626"/>

  <!-- PUSH label -->
  <text x="147" y="65" text-anchor="middle" font-size="10" font-weight="700"
        fill="#DC2626" font-family="system-ui,sans-serif">PUSH DOWN</text>
  <text x="147" y="55" text-anchor="middle" font-size="9" fill="#7F1D1D"
        font-family="system-ui,sans-serif">5–6 cm deep</text>

  <!-- Depth annotation arrow -->
  <line x1="172" y1="82" x2="172" y2="104" stroke="#6B7280" stroke-width="1.2" stroke-dasharray="3,2"/>
  <text x="176" y="95" font-size="8" fill="#6B7280" font-family="system-ui,sans-serif">depth</text>

  <!-- Centre of chest label -->
  <text x="147" y="162" text-anchor="middle" font-size="9" fill="#6B7280"
        font-family="system-ui,sans-serif">Centre of chest · heel of hand · arms straight</text>

  <!-- Info box -->
  <rect x="20" y="168" width="280" height="18" rx="5" fill="#FEE2E2"/>
  <text x="160" y="180" text-anchor="middle" font-size="9.5" font-weight="700"
        fill="#991B1B" font-family="system-ui,sans-serif">
    30 compressions → 2 breaths · Rate: 100–120/min
  </text>
</svg>
"""

SVG_RECOVERY = """
<svg viewBox="0 0 320 190" xmlns="http://www.w3.org/2000/svg"
     style="width:100%;max-width:320px;display:block;margin:6px auto">
  <rect width="320" height="190" rx="10" fill="#F0FDF4" stroke="#BBF7D0" stroke-width="1.5"/>

  <text x="160" y="22" text-anchor="middle" font-size="12" font-weight="700"
        fill="#166534" font-family="system-ui,sans-serif">Recovery Position (Left Side)</text>

  <!-- Ground -->
  <line x1="20" y1="152" x2="300" y2="152" stroke="#E5E7EB" stroke-width="2"/>

  <!-- Person on left side (foetal position) -->
  <!-- Head -->
  <circle cx="58" cy="100" r="20" fill="#FEF3C7" stroke="#D97706" stroke-width="2"/>
  <!-- Neck -->
  <rect x="74" y="96" width="18" height="12" rx="5" fill="#FEF3C7" stroke="#D97706" stroke-width="1.5"/>
  <!-- Body (curved, side-lying) -->
  <path d="M88,102 Q130,90 165,100 Q190,108 210,105"
        fill="none" stroke="#1D4ED8" stroke-width="22" stroke-linecap="round" opacity="0.7"/>
  <path d="M88,102 Q130,90 165,100 Q190,108 210,105"
        fill="none" stroke="#BFDBFE" stroke-width="18" stroke-linecap="round"/>
  <!-- Top leg bent forward -->
  <path d="M205,108 Q230,120 225,145"
        fill="none" stroke="#1D4ED8" stroke-width="18" stroke-linecap="round" opacity="0.7"/>
  <path d="M205,108 Q230,120 225,145"
        fill="none" stroke="#BFDBFE" stroke-width="14" stroke-linecap="round"/>
  <!-- Bottom leg straight -->
  <path d="M200,110 Q240,112 275,115"
        fill="none" stroke="#1D4ED8" stroke-width="14" stroke-linecap="round" opacity="0.6"/>
  <path d="M200,110 Q240,112 275,115"
        fill="none" stroke="#DBEAFE" stroke-width="10" stroke-linecap="round"/>
  <!-- Top arm extended forward -->
  <path d="M120,92 Q145,72 170,75"
        fill="none" stroke="#FCA5A5" stroke-width="10" stroke-linecap="round"/>

  <!-- Roll direction arrow -->
  <path d="M58,72 Q58,50 75,45 Q90,40 100,50"
        fill="none" stroke="#16A34A" stroke-width="2" stroke-dasharray="4,3"/>
  <polygon points="96,44 104,52 97,56" fill="#16A34A"/>
  <text x="110" y="43" font-size="9" fill="#16A34A" font-weight="600"
        font-family="system-ui,sans-serif">Roll onto side</text>

  <!-- Labels -->
  <text x="160" y="165" text-anchor="middle" font-size="9" fill="#6B7280"
        font-family="system-ui,sans-serif">Head tilted back slightly to keep airway open</text>

  <rect x="20" y="170" width="280" height="16" rx="5" fill="#DCFCE7"/>
  <text x="160" y="181" text-anchor="middle" font-size="9.5" font-weight="700"
        fill="#166534" font-family="system-ui,sans-serif">
    Prevents choking · Monitor breathing every 2 min
  </text>
</svg>
"""

SVG_BLEEDING = """
<svg viewBox="0 0 320 190" xmlns="http://www.w3.org/2000/svg"
     style="width:100%;max-width:320px;display:block;margin:6px auto">
  <rect width="320" height="190" rx="10" fill="#FFF5F5" stroke="#FECACA" stroke-width="1.5"/>

  <text x="160" y="22" text-anchor="middle" font-size="12" font-weight="700"
        fill="#DC2626" font-family="system-ui,sans-serif">Stop Bleeding — Direct Pressure</text>

  <!-- Arm shape -->
  <rect x="100" y="75" width="120" height="55" rx="27" fill="#FEF3C7" stroke="#D97706" stroke-width="2"/>

  <!-- Wound (red) -->
  <ellipse cx="160" cy="102" rx="18" ry="10" fill="#DC2626" opacity="0.85"/>
  <text x="160" y="106" text-anchor="middle" font-size="8" fill="#FFF"
        font-weight="700" font-family="system-ui,sans-serif">WOUND</text>

  <!-- Bottom hand -->
  <rect x="130" y="88" width="60" height="18" rx="6" fill="#92400E" opacity="0.75"/>
  <!-- Top hand pressing -->
  <rect x="128" y="72" width="64" height="18" rx="6" fill="#B45309"/>
  <!-- Cloth between hands -->
  <rect x="133" y="86" width="54" height="6" rx="2" fill="#FEF9C3" stroke="#D97706" stroke-width="1"/>

  <!-- Down arrows (pressure) -->
  <line x1="152" y1="58" x2="152" y2="70" stroke="#DC2626" stroke-width="2.5" stroke-linecap="round"/>
  <polygon points="145,68 152,78 159,68" fill="#DC2626"/>
  <line x1="168" y1="58" x2="168" y2="70" stroke="#DC2626" stroke-width="2.5" stroke-linecap="round"/>
  <polygon points="161,68 168,78 175,68" fill="#DC2626"/>

  <text x="160" y="52" text-anchor="middle" font-size="11" font-weight="800"
        fill="#DC2626" font-family="system-ui,sans-serif">PRESS HARD</text>

  <!-- Elevate arrow -->
  <line x1="240" y1="140" x2="240" y2="80" stroke="#1D4ED8" stroke-width="2" stroke-dasharray="4,3"/>
  <polygon points="234,84 240,74 246,84" fill="#1D4ED8"/>
  <text x="255" y="115" font-size="9" fill="#1D4ED8" font-weight="600"
        font-family="system-ui,sans-serif" transform="rotate(-90,255,115)">Elevate</text>

  <text x="160" y="158" text-anchor="middle" font-size="9" fill="#6B7280"
        font-family="system-ui,sans-serif">Use clean cloth · Add more if soaked — never remove first cloth</text>

  <rect x="20" y="166" width="280" height="18" rx="5" fill="#FEE2E2"/>
  <text x="160" y="178" text-anchor="middle" font-size="9.5" font-weight="700"
        fill="#991B1B" font-family="system-ui,sans-serif">
    Hold pressure continuously until ambulance arrives
  </text>
</svg>
"""

SVG_FRACTURE = """
<svg viewBox="0 0 320 190" xmlns="http://www.w3.org/2000/svg"
     style="width:100%;max-width:320px;display:block;margin:6px auto">
  <rect width="320" height="190" rx="10" fill="#FFFBEB" stroke="#FDE68A" stroke-width="1.5"/>

  <text x="160" y="22" text-anchor="middle" font-size="12" font-weight="700"
        fill="#D97706" font-family="system-ui,sans-serif">Fracture — Immobilise, Don't Straighten</text>

  <!-- Arm with fracture -->
  <rect x="70" y="88" width="180" height="30" rx="15" fill="#FEF3C7" stroke="#D97706" stroke-width="2"/>
  <!-- Fracture line -->
  <path d="M155,88 L162,103 L155,118" fill="none" stroke="#DC2626" stroke-width="2.5" stroke-linecap="round"/>
  <text x="170" y="107" font-size="9" fill="#DC2626" font-weight="700"
        font-family="system-ui,sans-serif">fracture</text>

  <!-- Splint board top -->
  <rect x="68" y="72" width="184" height="12" rx="4" fill="#78350F" opacity="0.75"/>
  <!-- Splint board bottom -->
  <rect x="68" y="122" width="184" height="12" rx="4" fill="#78350F" opacity="0.75"/>

  <!-- Padding between splint and skin -->
  <rect x="70" y="83" width="180" height="6" rx="2" fill="#FDE68A" opacity="0.8"/>
  <rect x="70" y="116" width="180" height="6" rx="2" fill="#FDE68A" opacity="0.8"/>

  <!-- Ties (above fracture) -->
  <rect x="110" y="68" width="8" height="40" rx="2" fill="#1D4ED8" opacity="0.8"/>
  <!-- Ties (below fracture) -->
  <rect x="200" y="68" width="8" height="40" rx="2" fill="#1D4ED8" opacity="0.8"/>

  <!-- Labels -->
  <text x="114" y="62" text-anchor="middle" font-size="8" fill="#1D4ED8"
        font-family="system-ui,sans-serif">tie above</text>
  <text x="204" y="62" text-anchor="middle" font-size="8" fill="#1D4ED8"
        font-family="system-ui,sans-serif">tie below</text>
  <text x="88" y="80" text-anchor="middle" font-size="8" fill="#92400E"
        font-family="system-ui,sans-serif">splint</text>
  <text x="80" y="120" text-anchor="middle" font-size="7" fill="#D97706"
        font-family="system-ui,sans-serif">padding</text>

  <!-- DO NOT straighten cross -->
  <line x1="240" y1="88" x2="265" y2="118" stroke="#DC2626" stroke-width="3" stroke-linecap="round"/>
  <line x1="265" y1="88" x2="240" y2="118" stroke="#DC2626" stroke-width="3" stroke-linecap="round"/>
  <text x="253" y="135" text-anchor="middle" font-size="8" fill="#DC2626" font-weight="700"
        font-family="system-ui,sans-serif">DON'T</text>
  <text x="253" y="145" text-anchor="middle" font-size="8" fill="#DC2626" font-weight="700"
        font-family="system-ui,sans-serif">STRAIGHTEN</text>

  <text x="140" y="162" text-anchor="middle" font-size="9" fill="#6B7280"
        font-family="system-ui,sans-serif">Splint in position found · Tie firmly, not tight</text>

  <rect x="20" y="170" width="280" height="16" rx="5" fill="#FEF9C3"/>
  <text x="160" y="181" text-anchor="middle" font-size="9.5" font-weight="700"
        fill="#92400E" font-family="system-ui,sans-serif">
    Check circulation below fracture every 5 minutes
  </text>
</svg>
"""

# Map scenario → illustration SVG
ILLUSTRATIONS = {
    "breathing":   SVG_CPR,
    "general":     SVG_RECOVERY,
    "unconscious": SVG_RECOVERY,
    "bleeding":    SVG_BLEEDING,
    "fracture":    SVG_FRACTURE,
    "spinal":      None,
    "burns":       None,
    "child":       SVG_CPR,
}


# ═════════════════════════════════════════════════════════════════════════════
#  FIRST AID CONTENT  — language-keyed
# ═════════════════════════════════════════════════════════════════════════════
# Structure per scenario:
#   title, subtitle, color, dos: [(num, title, detail), ...], donts: [str, ...]

FIRST_AID_CONTENT = {}

# ─────────────────────────────────────────────────────────────────────────────
#  ENGLISH
# ─────────────────────────────────────────────────────────────────────────────
FIRST_AID_CONTENT["en"] = {

    "general": {
        "title":    "Road Accident — Immediate Steps",
        "subtitle": "Golden hour: first 60 minutes are critical",
        "color":    "#DC2626",
        "dos": [
            ("1",  "Make the scene safe",
             "Switch on hazard lights. Place warning triangles 50 m behind the vehicle. Stop oncoming traffic."),
            ("2",  "Call 112 immediately",
             "Give your location, number of injured, and whether anyone is trapped. Stay on the line."),
            ("3",  "Do not move the patient",
             "Unless there is fire or flood. Moving a spinal injury patient can cause permanent paralysis."),
            ("4",  "Check responsiveness",
             "Tap shoulders gently and shout 'Are you okay?' If no response, check for breathing."),
            ("5",  "Check breathing",
             "Tilt head back, lift chin. Look for chest rise, listen for breath sounds for 10 seconds."),
            ("6",  "If breathing — recovery position",
             "Gently roll onto their side. Prevents choking on vomit. Only if NO neck injury suspected."),
            ("7",  "If not breathing — start CPR",
             "30 chest compressions (5–6 cm deep, hard and fast) then 2 rescue breaths. Repeat until ambulance arrives."),
            ("8",  "Stop any bleeding",
             "Apply firm direct pressure with a clean cloth. Do not remove — add more on top if it soaks through."),
            ("9",  "Keep the patient warm and calm",
             "Cover with a blanket. Talk continuously even if unconscious — hearing is the last sense to go."),
            ("10", "Note the time",
             "Write down the exact accident time and relay to paramedics — critical for trauma surgery decisions."),
        ],
        "donts": [
            "Do NOT give food or water — the patient may need surgery",
            "Do NOT remove a helmet unless the patient is not breathing",
            "Do NOT leave an unconscious patient alone",
            "Do NOT pull someone out of a vehicle unless there is fire",
            "Do NOT apply a tourniquet unless bleeding is life-threatening and won't stop",
        ],
    },

    "bleeding": {
        "title":    "Severe Bleeding — Stop It Fast",
        "subtitle": "A person can bleed out in 3–5 minutes from a major artery",
        "color":    "#DC2626",
        "dos": [
            ("1", "Press hard and hold",
             "Place a clean cloth directly on the wound. Press down HARD with both hands. Do not let go."),
            ("2", "Do not remove the cloth",
             "If it soaks through, add MORE cloth on top. Removing it disturbs the clot forming underneath."),
            ("3", "Elevate if possible",
             "Raise the bleeding limb above heart level — ONLY if no fracture is suspected."),
            ("4", "For neck or torso wounds",
             "Apply firm constant pressure. Do not pack the wound. Keep pressure until ambulance arrives."),
            ("5", "Tourniquet — last resort only",
             "For limb bleeding that will not stop: tie tight fabric 5–7 cm above the wound. Note the time. Do not remove."),
            ("6", "Keep talking to the patient",
             "Blood loss causes panic. A calm voice slows heart rate and reduces bleeding speed."),
        ],
        "donts": [
            "Do NOT remove an object embedded in the wound — stabilise it in place",
            "Do NOT apply a tourniquet to neck, chest, or abdomen",
            "Do NOT use a thin cord or wire as a tourniquet — it cuts tissue",
            "Do NOT give anything by mouth",
        ],
    },

    "unconscious": {
        "title":    "Unconscious Patient",
        "subtitle": "Brain damage begins after 4 minutes without oxygen",
        "color":    "#7C3AED",
        "dos": [
            ("1", "Check responsiveness",
             "Tap both shoulders, shout 'Can you hear me?' Check for any response."),
            ("2", "Open the airway",
             "Tilt the head back gently and lift the chin. This stops the tongue blocking the throat."),
            ("3", "Check breathing for 10 seconds",
             "Look for chest rise, listen and feel for airflow near mouth and nose."),
            ("4", "If breathing — recovery position",
             "Roll gently onto their left side. Support the head. Prevents choking if they vomit."),
            ("5", "If NOT breathing — CPR immediately",
             "30 hard chest compressions in the centre of the chest, then 2 breaths. 100–120/min. Continue until help arrives."),
            ("6", "Loosen tight clothing",
             "Unbutton collars, loosen ties or belts — nothing tight around neck or chest."),
            ("7", "Stay with them",
             "Monitor breathing every 2 minutes. If they stop breathing again, restart CPR."),
        ],
        "donts": [
            "Do NOT shake or slap the patient to wake them",
            "Do NOT tilt head if spinal injury is suspected — use jaw-thrust instead",
            "Do NOT give water or anything by mouth",
            "Do NOT leave the patient alone even for a moment",
            "Do NOT assume they cannot hear you — talk to them",
        ],
    },

    "fracture": {
        "title":    "Suspected Fracture",
        "subtitle": "Broken bones can cut arteries — immobilise before moving",
        "color":    "#D97706",
        "dos": [
            ("1", "Immobilise in the position found",
             "Do not try to straighten the limb. Splint it as-is using clothing, sticks, or rolled fabric."),
            ("2", "Check circulation below the fracture",
             "Press a fingernail — check colour returns. Cold or blue skin means artery may be damaged — urgent."),
            ("3", "Pad the splint",
             "Use soft fabric between the splint and skin. Tie firmly but not tight enough to stop blood flow."),
            ("4", "For an open fracture",
             "Cover the wound with a clean cloth. Do not push the bone back in. Apply pressure around (not on) the wound."),
            ("5", "Arm fracture sling",
             "Bend arm at 90°, support with a triangle of cloth tied around the neck. Hand slightly higher than elbow."),
            ("6", "Elevate if possible",
             "Raise the limb above heart level to reduce swelling — only if it does not cause more pain."),
        ],
        "donts": [
            "Do NOT attempt to realign or straighten the fracture",
            "Do NOT move a patient with suspected pelvis or spinal fracture",
            "Do NOT tie a splint so tight it cuts off circulation",
            "Do NOT apply direct pressure over a suspected fracture",
        ],
    },

    "spinal": {
        "title":    "Suspected Spinal / Neck Injury",
        "subtitle": "One wrong move can cause permanent paralysis — DO NOT move the patient",
        "color":    "#DC2626",
        "dos": [
            ("1", "DO NOT MOVE the patient",
             "This is the single most important rule. A fractured vertebra can sever the spinal cord if moved incorrectly."),
            ("2", "Stabilise the head in its current position",
             "Place your hands firmly on both sides of the head. Do not try to straighten the neck. Hold still."),
            ("3", "Tell bystanders firmly",
             "'Do not drag or lift this person.' One firm person keeping bystanders back is critical."),
            ("4", "Keep the patient calm and still",
             "Explain that help is coming. Tell them not to move their head or neck."),
            ("5", "Only move for immediate life threat",
             "Fire or rising water: log-roll as a team — one person holds the head, others roll body as a single unit."),
            ("6", "Do not remove the helmet",
             "If wearing a helmet and breathing, leave it on. Only remove if not breathing and airway is blocked."),
        ],
        "donts": [
            "Do NOT move, drag, or lift the patient alone",
            "Do NOT try to straighten a bent or twisted neck",
            "Do NOT remove the helmet if patient is breathing",
            "Do NOT tilt the head back — use jaw-thrust only",
            "Do NOT place a pillow under the head",
        ],
    },

    "burns": {
        "title":    "Burns from Fire or Fuel",
        "subtitle": "Cool the burn, not the patient",
        "color":    "#D97706",
        "dos": [
            ("1", "Move away from fire source",
             "Get the patient and yourself away from flames, hot surfaces, or fuel spills immediately."),
            ("2", "Cool with running water — 20 minutes",
             "Pour cool (not ice cold) water over the burn for a minimum of 20 minutes. Single most effective action."),
            ("3", "Remove clothing and jewellery",
             "Carefully cut away burnt clothing. Remove rings, watches near the burn before swelling starts."),
            ("4", "Cover loosely",
             "Wrap with cling film, a clean plastic bag, or non-fluffy cloth. Reduces infection and pain."),
            ("5", "Keep the patient warm",
             "Burns cause heat loss. Cover the rest of the body with a blanket while cooling only the burned area."),
            ("6", "For smoke inhalation",
             "Move to fresh air immediately. Hoarse voice or coughing = airway burns suspected — 112 is urgent."),
        ],
        "donts": [
            "Do NOT use ice, ice water, or very cold water — causes tissue damage",
            "Do NOT apply butter, oil, toothpaste, or any home remedy",
            "Do NOT burst blisters — they protect against infection",
            "Do NOT remove clothing stuck to burnt skin",
            "Do NOT cover burns with cotton wool — fibres stick to wounds",
        ],
    },

    "breathing": {
        "title":    "Not Breathing — CPR Guide",
        "subtitle": "Start immediately. Every 30 seconds without CPR reduces survival by 10%",
        "color":    "#DC2626",
        "dos": [
            ("1", "Check it is safe to approach",
             "Quickly check for traffic, fuel leaks, or downed power lines before touching the patient."),
            ("2", "Open the airway",
             "Tilt head back, lift chin. Look in the mouth — remove any visible obstruction with a finger sweep."),
            ("3", "Give 30 chest compressions",
             "Heel of hand on centre of chest. Lock fingers. Arms straight. Push 5–6 cm HARD and FAST. Count aloud."),
            ("4", "Give 2 rescue breaths",
             "Pinch the nose shut. Seal your mouth over theirs. Give a breath over 1 second — watch chest rise. Repeat once."),
            ("5", "Continue 30:2 ratio",
             "Keep going: 30 compressions, 2 breaths. Do not stop for more than 10 seconds. Rate: 100–120/min."),
            ("6", "Switch if another helper present",
             "CPR is exhausting. Switch every 2 minutes without stopping. One person calls 112, other does CPR."),
            ("7", "Stop only when",
             "Paramedics take over, the patient starts breathing normally, or you are physically unable to continue."),
        ],
        "donts": [
            "Do NOT stop CPR to check for a pulse — check only after 2 minutes",
            "Do NOT give gentle compressions — push HARD (ribs may crack; that is acceptable)",
            "Do NOT tilt the head if spinal injury is suspected",
            "Do NOT delay CPR waiting for the ambulance",
        ],
    },

    "child": {
        "title":    "Child or Infant Victim",
        "subtitle": "Children need gentler CPR — different compression depth",
        "color":    "#2563EB",
        "dos": [
            ("1", "2 fingers for infants (under 1 year)",
             "Place 2 fingers on centre of chest, just below the nipple line. Compress 4 cm — 1/3 of chest depth."),
            ("2", "1 hand for children (1–8 years)",
             "Heel of one hand on lower half of breastbone. Compress 5 cm. Do NOT use full body weight."),
            ("3", "2 hands for older children (8+)",
             "Same as adult CPR. 5–6 cm compressions, 30:2 ratio, 100–120 per minute."),
            ("4", "Tilt head only slightly for infants",
             "Infants have large heads — only a slight tilt is needed. Over-tilting closes the airway."),
            ("5", "Cover mouth AND nose for infants",
             "Your mouth should cover both the mouth and nose of an infant to form a seal."),
            ("6", "Call 112 after 1 minute of CPR",
             "For children, give 1 minute of CPR first before stopping to call — unlike adults where you call immediately."),
        ],
        "donts": [
            "Do NOT use full adult compression force on a child",
            "Do NOT over-tilt an infant's head — it closes the airway",
            "Do NOT give large rescue breaths — only enough to see the chest rise",
            "Do NOT delay — children deteriorate faster than adults",
        ],
    },
}


# ─────────────────────────────────────────────────────────────────────────────
#  TAMIL  (ta)  — placeholder until added
# ─────────────────────────────────────────────────────────────────────────────
FIRST_AID_CONTENT["ta"] = {

    "general": {
        "title":    "சாலை விபத்து — உடனடி நடவடிக்கைகள்",
        "subtitle": "தங்க நேரம்: முதல் 60 நிமிடங்கள் மிகவும் முக்கியமானவை",
        "color":    "#DC2626",
        "dos": [
            ("1",  "நிலையை பாதுகாப்பாக்குங்கள்",
             "அபாய விளக்குகளை எரியுங்கள். வாகனத்திலிருந்து 50 மீ பின்னால் எச்சரிக்கை முக்கோணங்களை வையுங்கள்."),
            ("2",  "உடனே 112 அழையுங்கள்",
             "உங்கள் இடம், காயமடைந்தோர் எண்ணிக்கை, யாரும் சிக்கியிருக்கிறார்களா என்று தெரிவியுங்கள்."),
            ("3",  "நோயாளியை நகர்த்தாதீர்கள்",
             "நெருப்பு அல்லது வெள்ளம் இல்லாத வரை. தண்டுவட காயம் நிரந்தர பக்கவாதத்தை ஏற்படுத்தலாம்."),
            ("4",  "உணர்வைச் சோதியுங்கள்",
             "தோளை மெதுவாக தட்டி 'நீங்கள் சரியாக இருக்கிறீர்களா?' என்று கத்துங்கள். பதில் இல்லையெனில் சுவாசத்தைச் சரிபாருங்கள்."),
            ("5",  "சுவாசத்தைச் சோதியுங்கள்",
             "தலையை பின்னோக்கி சாய்த்து கன்னத்தை தூக்குங்கள். 10 விநாடி மார்பின் அசைவைப் பாருங்கள்."),
            ("6",  "சுவாசித்தால் — மீட்பு நிலை",
             "பக்கவாட்டில் மெதுவாக உருட்டுங்கள். வாந்தியினால் மூச்சுத்திணறல் தடுக்கப்படும். கழுத்து காயம் இல்லை என்றால் மட்டுமே."),
            ("7",  "சுவாசிக்கவில்லையெனில் — CPR தொடங்குங்கள்",
             "30 மார்பு அழுத்தங்கள் (5–6 செ.மீ ஆழம், வேகமாகவும் கடினமாகவும்) பிறகு 2 மூச்சு. உதவி வரும் வரை தொடர்ந்து செய்யுங்கள்."),
            ("8",  "இரத்தப்போக்கை நிறுத்துங்கள்",
             "சுத்தமான துணியால் நேரடியாக அழுத்துங்கள். துணி நனைந்தாலும் எடுக்காதீர்கள் — மேலே மேலும் துணி வையுங்கள்."),
            ("9",  "நோயாளியை வெப்பமாகவும் அமைதியாகவும் வையுங்கள்",
             "போர்வையால் மூடுங்கள். மயக்கமடைந்தாலும் தொடர்ந்து பேசுங்கள் — காது கேட்கும் திறன் கடைசியில் போகும்."),
            ("10", "நேரத்தைக் குறியுங்கள்",
             "விபத்தின் சரியான நேரத்தை எழுதுங்கள். அறுவை சிகிச்சை முடிவுகளுக்கு இது மிக முக்கியம்."),
        ],
        "donts": [
            "உணவு அல்லது தண்ணீர் கொடுக்காதீர்கள் — அறுவை சிகிச்சை தேவைப்படலாம்",
            "சுவாசிக்காவிட்டால் மட்டுமே ஹெல்மெட்டை அகற்றுங்கள்",
            "மயக்கமடைந்த நோயாளியை தனியாக விட்டுச் செல்லாதீர்கள்",
            "நெருப்பு இல்லாத வரை வாகனத்திலிருந்து யாரையும் இழுக்காதீர்கள்",
            "நிறுத்த முடியாத உயிரை அச்சுறுத்தும் இரத்தப்போக்குக்கு மட்டுமே tourniquet பயன்படுத்துங்கள்",
        ],
    },

    "bleeding": {
        "title":    "கடுமையான இரத்தப்போக்கு — விரைவாக நிறுத்துங்கள்",
        "subtitle": "முக்கிய தமனியிலிருந்து 3–5 நிமிடங்களில் இரத்தம் வடியலாம்",
        "color":    "#DC2626",
        "dos": [
            ("1", "கடினமாக அழுத்துங்கள்",
             "சுத்தமான துணியை நேரடியாக காயத்தில் வையுங்கள். இரண்டு கைகளாலும் கடினமாக அழுத்துங்கள். விட்டுவிடாதீர்கள்."),
            ("2", "துணியை எடுக்காதீர்கள்",
             "நனைந்தால் மேலே மேலும் துணி வையுங்கள். எடுத்தால் உருவாகும் இரத்த உறைவு கெட்டுவிடும்."),
            ("3", "முடிந்தால் உயர்த்துங்கள்",
             "இரத்தம் வடியும் கையை அல்லது காலை இதயத்திற்கு மேலே உயர்த்துங்கள் — எலும்பு முறிவு இல்லை என்றால் மட்டுமே."),
            ("4", "கழுத்து அல்லது உடல் காயங்களுக்கு",
             "நிலையான அழுத்தம் கொடுங்கள். காயத்தை அடைக்க முயலாதீர்கள். ஆம்புலன்ஸ் வரும் வரை அழுத்தம் வையுங்கள்."),
            ("5", "Tourniquet — கடைசி தீர்வு மட்டுமே",
             "நிறுத்த முடியாத கை அல்லது கால் இரத்தப்போக்கிற்கு: காயத்திற்கு 5–7 செ.மீ மேலே இறுக்கமாக கட்டுங்கள். நேரத்தை குறியுங்கள்."),
            ("6", "நோயாளியிடம் பேசுங்கள்",
             "இரத்த இழப்பு பயத்தை ஏற்படுத்தும். அமைதியான குரல் இதயத் துடிப்பை குறைத்து இரத்தப்போக்கை மெதுவாக்கும்."),
        ],
        "donts": [
            "காயத்தில் சிக்கியுள்ள பொருளை எடுக்காதீர்கள் — அப்படியே நிலைப்படுத்துங்கள்",
            "கழுத்து, மார்பு அல்லது வயிற்றில் tourniquet போடாதீர்கள்",
            "மெல்லிய கயிறை tourniquet ஆக பயன்படுத்தாதீர்கள் — திசுக்கள் கிழிந்துவிடும்",
            "வாயில் எதுவும் கொடுக்காதீர்கள்",
        ],
    },

    "unconscious": {
        "title":    "மயக்கமடைந்த நோயாளி",
        "subtitle": "ஆக்ஸிஜன் இல்லாமல் 4 நிமிடங்களில் மூளை சேதம் தொடங்கும்",
        "color":    "#7C3AED",
        "dos": [
            ("1", "உணர்வைச் சோதியுங்கள்",
             "இரண்டு தோள்களையும் தட்டி 'கேட்கிறீர்களா?' என்று கத்துங்கள். ஏதாவது பதில் வருகிறதா என சரிபாருங்கள்."),
            ("2", "மூச்சுக்குழாயை திறங்கள்",
             "தலையை மெதுவாக பின்னோக்கி சாய்த்து கன்னத்தை தூக்குங்கள். நாக்கு தொண்டையை அடைப்பதை தடுக்கும்."),
            ("3", "10 விநாடி சுவாசத்தை சோதியுங்கள்",
             "மார்பின் அசைவைப் பாருங்கள், வாய் மற்றும் மூக்கு அருகில் காற்றை உணருங்கள்."),
            ("4", "சுவாசித்தால் — மீட்பு நிலை",
             "இடது பக்கமாக மெதுவாக உருட்டுங்கள். தலையை தாங்குங்கள். வாந்தியால் மூச்சுத்திணறல் தடுக்கப்படும்."),
            ("5", "சுவாசிக்கவில்லையெனில் — உடனே CPR",
             "மார்பின் மையத்தில் 30 அழுத்தங்கள் கொடுங்கள், பிறகு 2 மூச்சு. 100–120/நிமிடம். உதவி வரும் வரை தொடர்ந்து செய்யுங்கள்."),
            ("6", "இறுக்கமான ஆடைகளை தளர்த்துங்கள்",
             "பட்டன்களை திறங்கள், கழுத்து மற்றும் மார்பைச் சுற்றி இறுக்கமான எதையும் தளர்த்துங்கள்."),
            ("7", "அவர்களிடம் இருங்கள்",
             "ஒவ்வொரு 2 நிமிடமும் சுவாசத்தை கண்காணியுங்கள். மீண்டும் சுவாசிக்கவில்லையெனில் CPR ஆரம்பியுங்கள்."),
        ],
        "donts": [
            "நோயாளியை எழுப்ப குலுக்காதீர்கள் அல்லது அறைக்காதீர்கள்",
            "கழுத்து காயம் சந்தேகமிருந்தால் தலையை சாய்க்காதீர்கள் — jaw-thrust மட்டுமே",
            "தண்ணீர் அல்லது வாயில் எதுவும் கொடுக்காதீர்கள்",
            "நோயாளியை ஒரு நிமிடம் கூட தனியாக விடாதீர்கள்",
            "கேட்கவில்லை என்று நினைக்காதீர்கள் — தொடர்ந்து பேசுங்கள்",
        ],
    },

    "breathing": {
        "title":    "சுவாசிக்கவில்லை — CPR வழிகாட்டி",
        "subtitle": "உடனே தொடங்குங்கள். ஒவ்வொரு 30 விநாடியும் உயிர்வாழ்வு 10% குறைகிறது",
        "color":    "#DC2626",
        "dos": [
            ("1", "அணுகுவது பாதுகாப்பானதா என சரிபாருங்கள்",
             "போக்குவரத்து, எரிபொருள் கசிவு அல்லது மின் கம்பிகளை விரைவாக சரிபாருங்கள்."),
            ("2", "மூச்சுக்குழாயை திறங்கள்",
             "தலையை பின்னோக்கி சாய்த்து கன்னத்தை தூக்குங்கள். வாயில் தெரியும் தடைகளை விரலால் அகற்றுங்கள்."),
            ("3", "30 மார்பு அழுத்தங்கள் கொடுங்கள்",
             "மார்பின் மையத்தில் கையின் குதிகால் வையுங்கள். விரல்களை பூட்டுங்கள். கைகளை நேராக வையுங்கள். 5–6 செ.மீ கடினமாகவும் வேகமாகவும் அழுத்துங்கள்."),
            ("4", "2 மூச்சு கொடுங்கள்",
             "மூக்கை சிட்டிக்கையால் மூடுங்கள். வாயை முழுமையாக மூடி 1 விநாடி மூச்சு ஊதுங்கள். மார்பு உயர்கிறதா பாருங்கள்."),
            ("5", "30:2 விகிதத்தில் தொடரங்கள்",
             "30 அழுத்தங்கள், 2 மூச்சு — தொடர்ந்து செய்யுங்கள். 10 விநாடிக்கு மேல் நிறுத்தாதீர்கள். வேகம்: 100–120/நிமிடம்."),
            ("6", "இன்னொருவர் இருந்தால் மாறி மாறி செய்யுங்கள்",
             "CPR சோர்வூட்டும். ஒவ்வொரு 2 நிமிடமும் மாறுங்கள். ஒருவர் 112 அழைக்க, இன்னொருவர் CPR செய்யட்டும்."),
            ("7", "இவ்வோட்டு நிறுத்துங்கள்",
             "மருத்துவர்கள் வந்தவுடன், நோயாளி சாதாரணமாக சுவாசிக்கும் போது, அல்லது தொடர முடியாத போது."),
        ],
        "donts": [
            "நாடி பரிசோதிக்க CPR நிறுத்தாதீர்கள் — 2 நிமிடம் கழித்து மட்டுமே சரிபாருங்கள்",
            "மெதுவாக அழுத்தாதீர்கள் — கடினமாக அழுத்துங்கள் (விலா எலும்பு முறியலாம்; பரவாயில்லை)",
            "கழுத்து காயம் சந்தேகமிருந்தால் தலையை சாய்க்காதீர்கள்",
            "ஆம்புலன்ஸ் வரும் வரை காத்திருக்காதீர்கள் — உடனே CPR தொடங்குங்கள்",
        ],
    },

    "fracture": {
        "title":    "எலும்பு முறிவு சந்தேகம்",
        "subtitle": "முறிந்த எலும்பு தமனிகளை வெட்டலாம் — நகர்த்துவதற்கு முன் நிலைப்படுத்துங்கள்",
        "color":    "#D97706",
        "dos": [
            ("1", "கிடக்கும் நிலையில் நிலைப்படுத்துங்கள்",
             "கையை அல்லது காலை நேராக்க முயலாதீர்கள். துணி, குச்சி அல்லது சுருட்டிய துணியால் இருக்கும் நிலையிலேயே கட்டுங்கள்."),
            ("2", "முறிவுக்கு கீழே இரத்த ஓட்டத்தை சரிபாருங்கள்",
             "விரல் நகத்தை அழுத்தி நிறம் திரும்புகிறதா பாருங்கள். குளிர்ச்சியாக அல்லது நீலமாக இருந்தால் தமனி சேதம் — அவசரம்."),
            ("3", "கட்டுக்கு மென்மையான பொருள் வையுங்கள்",
             "கட்டுக்கும் தோலுக்கும் இடையில் மென்மையான துணி வையுங்கள். இறுக்கமாக ஆனால் இரத்த ஓட்டம் நிறுத்தாமல் கட்டுங்கள்."),
            ("4", "திறந்த எலும்பு முறிவிற்கு",
             "காயத்தை சுத்தமான துணியால் மூடுங்கள். எலும்பை உள்ளே தள்ளாதீர்கள். காயத்தைச் சுற்றி (மேலே அல்ல) அழுத்தம் கொடுங்கள்."),
            ("5", "கை முறிவுக்கு கவண்",
             "கையை 90° கோணத்தில் மடக்கி, கழுத்தில் கட்டிய துணி முக்கோணத்தால் தாங்குங்கள்."),
            ("6", "முடிந்தால் உயர்த்துங்கள்",
             "வீக்கம் குறைய உறுப்பை இதயத்திற்கு மேலே உயர்த்துங்கள் — மேலும் வலி வரவில்லையெனில் மட்டுமே."),
        ],
        "donts": [
            "எலும்பை நேராக்க முயலாதீர்கள்",
            "இடுப்பு அல்லது தண்டுவட முறிவு சந்தேகமிருந்தால் நோயாளியை நகர்த்தாதீர்கள்",
            "இரத்த ஓட்டம் நிற்கும் அளவு இறுக்கமாக கட்டாதீர்கள்",
            "முறிவுக்கு நேரடியாக அழுத்தம் கொடுக்காதீர்கள்",
        ],
    },

    "spinal": {
        "title":    "தண்டுவட / கழுத்து காயம் சந்தேகம்",
        "subtitle": "தவறான நகர்வு நிரந்தர பக்கவாதத்தை ஏற்படுத்தலாம் — நகர்த்தாதீர்கள்",
        "color":    "#DC2626",
        "dos": [
            ("1", "நோயாளியை நகர்த்தாதீர்கள்",
             "இது மிக முக்கியமான விதி. தவறாக நகர்த்தினால் முறிந்த முதுகெலும்பு தண்டுவட நரம்பை வெட்டலாம்."),
            ("2", "தலையை இருக்கும் நிலையில் நிலைப்படுத்துங்கள்",
             "இரண்டு கைகளாலும் தலையின் இரு பக்கங்களையும் உறுதியாக பிடியுங்கள். கழுத்தை நேராக்க முயலாதீர்கள்."),
            ("3", "பார்வையாளர்களிடம் கண்டிப்பாக சொல்லுங்கள்",
             "'இந்த நபரை இழுக்கவோ தூக்கவோ கூடாது.' ஒரு நபர் பார்வையாளர்களை தடுத்தால் மிக முக்கியம்."),
            ("4", "நோயாளியை அமைதியாக வையுங்கள்",
             "உதவி வருகிறது என்று சொல்லுங்கள். தலை மற்றும் கழுத்தை அசைக்காதீர்கள் என்று சொல்லுங்கள்."),
            ("5", "உயிருக்கு ஆபத்து மட்டுமே நகர்த்துங்கள்",
             "நெருப்பு அல்லது வெள்ளம்: குழு சேர்ந்து log-roll செய்யுங்கள் — ஒருவர் தலையை பிடிக்க, மற்றவர்கள் உடலை ஒரு அலகாக உருட்டட்டும்."),
        ],
        "donts": [
            "தனியாக நோயாளியை இழுக்காதீர்கள் அல்லது தூக்காதீர்கள்",
            "வளைந்த அல்லது திரிந்த கழுத்தை நேராக்க முயலாதீர்கள்",
            "சுவாசித்தால் ஹெல்மெட்டை கழற்றாதீர்கள்",
            "சுவாசம் சரிபார்க்க தலையை சாய்க்காதீர்கள் — jaw-thrust மட்டுமே",
            "தலைக்கு தலையணை வைக்காதீர்கள்",
        ],
    },

    "burns": {
        "title":    "நெருப்பு அல்லது எரிபொருளால் தீக்காயம்",
        "subtitle": "தீக்காயத்தை ஆற்றுங்கள், நோயாளியை குளிரவைக்காதீர்கள்",
        "color":    "#D97706",
        "dos": [
            ("1", "நெருப்பிலிருந்து விலகுங்கள்",
             "நோயாளியையும் உங்களையும் நெருப்பு, சூடான பரப்புகள் அல்லது எரிபொருள் கசிவிலிருந்து விலக்குங்கள்."),
            ("2", "20 நிமிடம் குளிர்ந்த நீர் ஊற்றுங்கள்",
             "குளிர்ந்த (பனி தண்ணீர் அல்ல) நீரை குறைந்தது 20 நிமிடம் தீக்காயத்தில் ஊற்றுங்கள். இதுவே மிகவும் பயனுள்ள நடவடிக்கை."),
            ("3", "ஆடைகளையும் நகைகளையும் அகற்றுங்கள்",
             "எரிந்த ஆடைகளை கவனமாக வெட்டி அகற்றுங்கள். வீக்கம் வருவதற்கு முன் மோதிரம், கடிகாரம் அகற்றுங்கள்."),
            ("4", "தளர்வாக மூடுங்கள்",
             "cling film, சுத்தமான பிளாஸ்டிக் பை அல்லது பஞ்சு இல்லாத துணியால் மூடுங்கள். தொற்றுநோய் மற்றும் வலியை குறைக்கும்."),
            ("5", "நோயாளியை வெப்பமாக வையுங்கள்",
             "தீக்காயம் வெப்பத்தை இழக்கச் செய்யும். தீக்காயப்பட்ட இடத்தை மட்டும் குளிர்விக்கும்போது மற்ற உடலை போர்வையால் மூடுங்கள்."),
            ("6", "புகை சுவாசித்திருந்தால்",
             "உடனே புதிய காற்றுள்ள இடத்திற்கு அழைத்துச் செல்லுங்கள். தொண்டை கரகரப்பு இருந்தால் — 112 அவசரம்."),
        ],
        "donts": [
            "பனி, பனி நீர் அல்லது மிகவும் குளிர்ந்த நீர் பயன்படுத்தாதீர்கள் — திசு சேதம் ஆகும்",
            "வெண்ணெய், எண்ணெய், பேஸ்ட் அல்லது வீட்டு வைத்தியம் போடாதீர்கள்",
            "கொப்புளங்களை உடைக்காதீர்கள் — தொற்றுநோயிலிருந்து பாதுகாக்கும்",
            "எரிந்த தோலில் ஒட்டிய ஆடைகளை இழுக்காதீர்கள்",
            "பஞ்சை தீக்காயத்தில் போடாதீர்கள் — நார்கள் காயத்தில் ஒட்டிவிடும்",
        ],
    },

    "child": {
        "title":    "குழந்தை அல்லது குழந்தைக்குட்டி பாதிக்கப்பட்டால்",
        "subtitle": "குழந்தைகளுக்கு மெதுவான CPR தேவை — அழுத்தம் வேறுபடும்",
        "color":    "#2563EB",
        "dos": [
            ("1", "குழந்தைக்குட்டிக்கு (1 வயதுக்கு கீழ்) — 2 விரல்கள்",
             "மார்பின் மையத்தில் நிப்பிள் கோட்டிற்கு கீழ் 2 விரல்களை வையுங்கள். 4 செ.மீ அழுத்துங்கள்."),
            ("2", "சிறு குழந்தைகளுக்கு (1–8 வயது) — 1 கை",
             "ஒரு கையின் குதிகாலை மார்பின் கீழ் பாதியில் வையுங்கள். 5 செ.மீ அழுத்துங்கள்."),
            ("3", "பெரிய குழந்தைகளுக்கு (8+) — 2 கைகள்",
             "பெரியவர் CPR போலவே. 5–6 செ.மீ அழுத்தம், 30:2 விகிதம், 100–120/நிமிடம்."),
            ("4", "குழந்தைக்குட்டிக்கு தலையை மிகவும் சாய்க்காதீர்கள்",
             "குழந்தைக்குட்டிக்கு பெரிய தலை உள்ளது — சிறிய சாய்வு மட்டுமே போதும். அதிகமாக சாய்த்தால் மூச்சுக்குழாய் மூடும்."),
            ("5", "குழந்தைக்குட்டிக்கு வாய் மற்றும் மூக்கை மூடுங்கள்",
             "குழந்தைக்குட்டியின் வாய் மற்றும் மூக்கை உங்கள் வாயால் முழுவதுமாக மூடி மூச்சு கொடுங்கள்."),
            ("6", "1 நிமிடம் CPR கொடுத்த பிறகு 112 அழையுங்கள்",
             "குழந்தைகளுக்கு முதல் 1 நிமிடம் CPR கொடுத்த பிறகு அழையுங்கள் — பெரியவர்களுக்கு இல்லாமல்."),
        ],
        "donts": [
            "குழந்தையிடம் பெரியவர் அழுத்தம் போட்டு CPR செய்யாதீர்கள்",
            "குழந்தைக்குட்டியின் தலையை அதிகமாக சாய்க்காதீர்கள் — மூச்சுக்குழாய் மூடும்",
            "பெரிய மூச்சு கொடுக்காதீர்கள் — மார்பு உயரும் அளவு மட்டுமே",
            "தாமதிக்காதீர்கள் — குழந்தைகள் பெரியவர்களை விட விரைவாக மோசமாவார்கள்",
        ],
    },
}

# ─────────────────────────────────────────────────────────────────────────────
#  HINDI  (hi)  — placeholder until added
# ─────────────────────────────────────────────────────────────────────────────
FIRST_AID_CONTENT["hi"] = {

    "general": {
        "title":    "सड़क दुर्घटना — तत्काल कदम",
        "subtitle": "गोल्डन आवर: पहले 60 मिनट बेहद महत्वपूर्ण हैं",
        "color":    "#DC2626",
        "dos": [
            ("1",  "घटनास्थल को सुरक्षित करें",
             "हैज़र्ड लाइट चालू करें। वाहन के 50 मीटर पीछे चेतावनी त्रिकोण लगाएं। आने वाले वाहनों को रोकें।"),
            ("2",  "तुरंत 112 पर कॉल करें",
             "अपना स्थान, घायलों की संख्या और किसी के फंसे होने की जानकारी दें। लाइन पर बने रहें।"),
            ("3",  "मरीज़ को हिलाएं नहीं",
             "जब तक आग या बाढ़ न हो। रीढ़ की हड्डी की चोट स्थायी लकवा पैदा कर सकती है।"),
            ("4",  "होश की जांच करें",
             "कंधों को धीरे से थपथपाएं और 'क्या आप ठीक हैं?' चिल्लाएं। कोई प्रतिक्रिया न हो तो सांस जांचें।"),
            ("5",  "सांस की जांच करें",
             "सिर पीछे झुकाएं, ठुड्डी ऊपर उठाएं। 10 सेकंड तक छाती की गति देखें, सुनें और महसूस करें।"),
            ("6",  "सांस आ रही हो — रिकवरी पोजीशन",
             "बाईं करवट धीरे से लिटाएं। उल्टी से दम घुटना रुकेगा। गर्दन में चोट न हो तभी।"),
            ("7",  "सांस न आए — CPR शुरू करें",
             "30 छाती दबाव (5–6 से.मी. गहरे, तेज और जोर से) फिर 2 सांसें। एम्बुलेंस आने तक जारी रखें।"),
            ("8",  "खून बहना रोकें",
             "साफ कपड़े से सीधे दबाव डालें। कपड़ा भीगने पर भी न हटाएं — ऊपर और कपड़ा रखें।"),
            ("9",  "मरीज़ को गर्म और शांत रखें",
             "कंबल से ढकें। बेहोश हो तो भी लगातार बात करें — सुनने की क्षमता सबसे बाद में जाती है।"),
            ("10", "समय नोट करें",
             "दुर्घटना का सटीक समय लिखें और पैरामेडिक्स को बताएं — सर्जरी के फैसलों के लिए जरूरी है।"),
        ],
        "donts": [
            "खाना या पानी न दें — मरीज़ को सर्जरी की जरूरत हो सकती है",
            "हेलमेट तभी उतारें जब सांस न आ रही हो",
            "बेहोश मरीज़ को अकेला न छोड़ें",
            "आग न हो तो वाहन से किसी को न खींचें",
            "जानलेवा खून बहने पर ही टूर्निकेट लगाएं",
        ],
    },

    "bleeding": {
        "title":    "गंभीर रक्तस्राव — तुरंत रोकें",
        "subtitle": "बड़ी धमनी से 3–5 मिनट में खून की कमी से मौत हो सकती है",
        "color":    "#DC2626",
        "dos": [
            ("1", "जोर से दबाएं और पकड़े रहें",
             "साफ कपड़ा सीधे घाव पर रखें। दोनों हाथों से जोर से दबाएं। हाथ न हटाएं।"),
            ("2", "कपड़ा न हटाएं",
             "भीग जाए तो ऊपर और कपड़ा रखें। हटाने से बन रही खून की गांठ टूट जाती है।"),
            ("3", "संभव हो तो ऊपर उठाएं",
             "खून बह रहे अंग को दिल से ऊपर उठाएं — केवल तभी जब फ्रैक्चर का संदेह न हो।"),
            ("4", "गर्दन या धड़ के घावों के लिए",
             "लगातार दबाव डालें। घाव में कुछ न भरें। एम्बुलेंस आने तक दबाव बनाए रखें।"),
            ("5", "टूर्निकेट — अंतिम उपाय",
             "रुकने वाला न हो तो: घाव से 5–7 से.मी. ऊपर कसकर कपड़ा बांधें। समय नोट करें।"),
            ("6", "मरीज़ से बात करते रहें",
             "खून बहने से घबराहट होती है। शांत आवाज़ दिल की धड़कन धीमी करती है।"),
        ],
        "donts": [
            "घाव में धंसी चीज़ को न निकालें — उसे वहीं स्थिर करें",
            "गर्दन, छाती या पेट पर टूर्निकेट न लगाएं",
            "पतली डोर या तार को टूर्निकेट के रूप में उपयोग न करें — ऊतक कट जाते हैं",
            "मुंह से कुछ न दें",
        ],
    },

    "unconscious": {
        "title":    "बेहोश मरीज़",
        "subtitle": "ऑक्सीजन के बिना 4 मिनट में दिमाग को नुकसान शुरू होता है",
        "color":    "#7C3AED",
        "dos": [
            ("1", "होश की जांच करें",
             "दोनों कंधों को थपथपाएं, 'क्या सुन रहे हो?' चिल्लाएं। कोई भी प्रतिक्रिया जांचें।"),
            ("2", "वायुमार्ग खोलें",
             "सिर धीरे से पीछे झुकाएं और ठुड्डी ऊपर उठाएं। जीभ को गले में रुकने से रोकता है।"),
            ("3", "10 सेकंड सांस जांचें",
             "छाती की गति देखें, मुंह और नाक के पास हवा का बहाव सुनें और महसूस करें।"),
            ("4", "सांस आ रही हो — रिकवरी पोजीशन",
             "बाईं करवट धीरे से लिटाएं। सिर सहारा दें। उल्टी से दम घुटना रुकेगा।"),
            ("5", "सांस न आए — तुरंत CPR",
             "छाती के बीच में 30 जोरदार दबाव, फिर 2 सांसें। 100–120/मिनट। मदद आने तक जारी रखें।"),
            ("6", "कसे हुए कपड़े ढीले करें",
             "बटन खोलें, गर्दन और छाती के आसपास कुछ भी कसा हो तो ढीला करें।"),
            ("7", "उनके पास रहें",
             "हर 2 मिनट में सांस देखें। फिर रुक जाए तो CPR दोबारा शुरू करें।"),
        ],
        "donts": [
            "मरीज़ को हिलाएं या थप्पड़ न मारें",
            "रीढ़ में चोट का संदेह हो तो सिर न झुकाएं — jaw-thrust करें",
            "पानी या कुछ भी मुंह से न दें",
            "एक पल के लिए भी मरीज़ को अकेला न छोड़ें",
            "यह न समझें कि वे सुन नहीं सकते — बात करते रहें",
        ],
    },

    "breathing": {
        "title":    "सांस नहीं आ रही — CPR गाइड",
        "subtitle": "तुरंत शुरू करें। हर 30 सेकंड बिना CPR के जीवित रहने की संभावना 10% कम होती है",
        "color":    "#DC2626",
        "dos": [
            ("1", "पास जाना सुरक्षित है जांचें",
             "ट्रैफिक, ईंधन का रिसाव या बिजली के तार न हों — जल्दी से देखें।"),
            ("2", "वायुमार्ग खोलें",
             "सिर पीछे झुकाएं, ठुड्डी ऊपर उठाएं। मुंह में दिखने वाली रुकावट उंगली से निकालें।"),
            ("3", "30 छाती दबाव दें",
             "हथेली की एड़ी छाती के बीच रखें। उंगलियां जोड़ लें। बाहें सीधी रखें। 5–6 से.मी. जोर और तेज से दबाएं।"),
            ("4", "2 सांसें दें",
             "नाक बंद करें। मुंह पूरा ढकें। 1 सेकंड में सांस दें — छाती ऊपर उठे यह देखें।"),
            ("5", "30:2 अनुपात जारी रखें",
             "30 दबाव, 2 सांसें — बिना रुके। 10 सेकंड से ज्यादा न रुकें। 100–120/मिनट।"),
            ("6", "कोई और हो तो बारी-बारी करें",
             "CPR थका देता है। हर 2 मिनट में बदलें। एक 112 करे, दूसरा CPR दे।"),
            ("7", "तभी रुकें",
             "पैरामेडिक्स संभाल लें, मरीज़ सामान्य रूप से सांस लेने लगे, या आप बिल्कुल थक जाएं।"),
        ],
        "donts": [
            "नाड़ी देखने CPR न रोकें — 2 मिनट बाद ही जांचें",
            "धीरे न दबाएं — जोर से दबाएं (पसलियां टूट सकती हैं; यह ठीक है)",
            "रीढ़ में चोट का संदेह हो तो सिर न झुकाएं",
            "एम्बुलेंस का इंतज़ार करते CPR में देरी न करें",
        ],
    },

    "fracture": {
        "title":    "हड्डी टूटने का संदेह",
        "subtitle": "टूटी हड्डी धमनी काट सकती है — हिलाने से पहले स्थिर करें",
        "color":    "#D97706",
        "dos": [
            ("1", "जिस स्थिति में हो उसी में स्थिर करें",
             "अंग को सीधा करने की कोशिश न करें। कपड़े, लकड़ी या रोल किए कपड़े से ऊपर-नीचे बांधें।"),
            ("2", "फ्रैक्चर के नीचे रक्त संचार जांचें",
             "नाखून दबाएं — रंग वापस आता है देखें। ठंडी या नीली त्वचा = धमनी को नुकसान — जरूरी।"),
            ("3", "पट्टी में मुलायम चीज़ भरें",
             "पट्टी और त्वचा के बीच मुलायम कपड़ा रखें। मजबूती से बांधें लेकिन रक्त प्रवाह न रुके।"),
            ("4", "खुले फ्रैक्चर के लिए",
             "घाव को साफ कपड़े से ढकें। हड्डी अंदर न दबाएं। घाव के आसपास दबाव दें।"),
            ("5", "हाथ टूटे तो गोफन (sling)",
             "हाथ 90° मोड़ें, गर्दन से बंधे कपड़े के त्रिकोण से सहारा दें।"),
            ("6", "संभव हो तो ऊपर उठाएं",
             "सूजन कम करने को दिल से ऊपर उठाएं — केवल तभी जब दर्द न बढ़े।"),
        ],
        "donts": [
            "फ्रैक्चर को सीधा करने की कोशिश न करें",
            "पेल्विस या रीढ़ में फ्रैक्चर संदेह हो तो मरीज़ को न हिलाएं",
            "पट्टी इतनी कसकर न बांधें कि रक्त प्रवाह रुक जाए",
            "फ्रैक्चर पर सीधा दबाव न डालें",
        ],
    },

    "spinal": {
        "title":    "रीढ़ / गर्दन की चोट का संदेह",
        "subtitle": "एक गलत हरकत स्थायी लकवा कर सकती है — मरीज़ को न हिलाएं",
        "color":    "#DC2626",
        "dos": [
            ("1", "मरीज़ को न हिलाएं",
             "यह सबसे महत्वपूर्ण नियम है। गलत तरीके से हिलाने पर टूटी कशेरुका रीढ़ की नसें काट सकती है।"),
            ("2", "सिर को वर्तमान स्थिति में स्थिर करें",
             "दोनों हाथ सिर के दोनों तरफ मजबूती से रखें। गर्दन सीधी करने की कोशिश न करें।"),
            ("3", "दर्शकों को दृढ़ता से बोलें",
             "'इस व्यक्ति को खींचें या उठाएं नहीं।' एक दृढ़ व्यक्ति का दर्शकों को रोकना जरूरी है।"),
            ("4", "मरीज़ को शांत रखें",
             "मदद आ रही है बताएं। सिर या गर्दन न हिलाने को कहें।"),
            ("5", "सिर्फ जान का तत्काल खतरा हो तो हिलाएं",
             "आग या पानी: टीम मिलकर log-roll करे — एक सिर पकड़े, बाकी एक साथ उठाएं।"),
        ],
        "donts": [
            "अकेले मरीज़ को न खींचें, न उठाएं",
            "मुड़ी या टेढ़ी गर्दन को सीधा न करें",
            "सांस आ रही हो तो हेलमेट न उतारें",
            "सांस जांचने सिर पीछे न झुकाएं — jaw-thrust करें",
            "सिर के नीचे तकिया न रखें",
        ],
    },

    "burns": {
        "title":    "आग या ईंधन से जलने पर",
        "subtitle": "जले को ठंडा करें, मरीज़ को नहीं",
        "color":    "#D97706",
        "dos": [
            ("1", "आग से दूर ले जाएं",
             "मरीज़ और खुद को लपटों, गर्म सतहों या ईंधन रिसाव से तुरंत दूर करें।"),
            ("2", "20 मिनट ठंडे पानी से धोएं",
             "जले हिस्से पर ठंडा (बर्फ नहीं) पानी कम से कम 20 मिनट डालें। यही सबसे असरदार कदम है।"),
            ("3", "कपड़े और गहने उतारें",
             "जले कपड़े सावधानी से काटकर हटाएं। सूजन से पहले अंगूठी, घड़ी हटाएं।"),
            ("4", "ढीला ढंककर रखें",
             "cling film, साफ पॉलीथीन या बिना रुई के कपड़े से ढकें। संक्रमण और दर्द कम होगा।"),
            ("5", "मरीज़ को गर्म रखें",
             "जलने से गर्मी जाती है। जले हिस्से को ठंडा करते हुए बाकी शरीर कंबल से ढकें।"),
            ("6", "धुआं सांस में गया हो तो",
             "तुरंत ताज़ी हवा में ले जाएं। गला बैठा हो या खांसी हो तो 112 — वायुमार्ग में जलन का संदेह।"),
        ],
        "donts": [
            "बर्फ, बर्फ का पानी या बहुत ठंडा पानी न डालें — ऊतक खराब होते हैं",
            "मक्खन, तेल, टूथपेस्ट या कोई घरेलू नुस्खा न लगाएं",
            "छाले न फोड़ें — संक्रमण से बचाते हैं",
            "जली त्वचा पर चिपके कपड़े न खींचें",
            "रुई जले हिस्से पर न लगाएं — धागे घाव में फंस जाते हैं",
        ],
    },

    "child": {
        "title":    "बच्चा या शिशु पीड़ित हो",
        "subtitle": "बच्चों को हल्का CPR चाहिए — दबाव की गहराई अलग होती है",
        "color":    "#2563EB",
        "dos": [
            ("1", "शिशु (1 साल से कम) — 2 उंगलियां",
             "छाती के बीच, निप्पल लाइन के नीचे 2 उंगलियां रखें। 4 से.मी. दबाएं।"),
            ("2", "छोटे बच्चे (1–8 साल) — 1 हाथ",
             "एक हाथ की एड़ी ब्रेस्टबोन के निचले आधे पर। 5 से.मी. दबाएं। पूरा वजन न लगाएं।"),
            ("3", "बड़े बच्चे (8+) — 2 हाथ",
             "बड़ों जैसा CPR। 5–6 से.मी. दबाव, 30:2, 100–120/मिनट।"),
            ("4", "शिशु का सिर थोड़ा ही झुकाएं",
             "शिशु का सिर बड़ा होता है — थोड़ी झुकाव ही काफी है। ज्यादा झुकाने से वायुमार्ग बंद हो जाता है।"),
            ("5", "शिशु के मुंह और नाक दोनों ढकें",
             "अपने मुंह से शिशु का मुंह और नाक दोनों पूरी तरह ढकें और सांस दें।"),
            ("6", "1 मिनट CPR के बाद 112 करें",
             "बच्चों के लिए पहले 1 मिनट CPR दें फिर कॉल करें — बड़ों से उलट।"),
        ],
        "donts": [
            "बच्चे पर बड़ों जितना दबाव न डालें",
            "शिशु का सिर ज्यादा न झुकाएं — वायुमार्ग बंद हो जाता है",
            "बड़ी सांस न दें — छाती उठे उतनी ही",
            "देरी न करें — बच्चे बड़ों से जल्दी बिगड़ते हैं",
        ],
    },
}

# ─────────────────────────────────────────────────────────────────────────────
#  TELUGU  (te)  — placeholder until added
# ─────────────────────────────────────────────────────────────────────────────
FIRST_AID_CONTENT["te"] = {

    "general": {
        "title":    "రోడ్డు ప్రమాదం — తక్షణ చర్యలు",
        "subtitle": "గోల్డన్ అవర్: మొదటి 60 నిమిషాలు చాలా ముఖ్యమైనవి",
        "color":    "#DC2626",
        "dos": [
            ("1",  "ప్రదేశాన్ని సురక్షితం చేయండి",
             "హజార్డ్ లైట్లు వేయండి. వాహనం వెనుక 50 మీ దూరంలో హెచ్చరిక త్రిభుజాలు పెట్టండి."),
            ("2",  "వెంటనే 112 కి కాల్ చేయండి",
             "మీ స్థానం, గాయపడినవారి సంఖ్య, ఎవరైనా చిక్కుకున్నారా అని తెలియజేయండి."),
            ("3",  "రోగిని కదిలించకండి",
             "నిప్పు లేదా వరద లేకుండా. వెన్నెముక గాయం శాశ్వత పక్షవాతానికి దారితీయవచ్చు."),
            ("4",  "స్పందన తనిఖీ చేయండి",
             "భుజాలను మెల్లగా తట్టి 'మీకు ఏమైనా అయిందా?' అని అరవండి. స్పందన లేకుంటే శ్వాస తనిఖీ చేయండి."),
            ("5",  "శ్వాస తనిఖీ చేయండి",
             "తల వెనక్కి వంచండి, గడ్డం పైకి ఎత్తండి. 10 సెకన్లు ఛాతీ కదలిక చూడండి, వినండి."),
            ("6",  "శ్వాస వస్తే — రికవరీ పొజిషన్",
             "మెల్లగా పక్కకు పడుకోబెట్టండి. వాంతి చేసుకుంటే గొంతు మూసుకోకుండా ఉంటుంది."),
            ("7",  "శ్వాస రాకపోతే — CPR ప్రారంభించండి",
             "30 ఛాతీ నొక్కుళ్ళు (5–6 సెం.మీ లోతు, వేగంగా మరియు గట్టిగా) తర్వాత 2 శ్వాసలు. అంబులెన్స్ వచ్చేవరకు కొనసాగించండి."),
            ("8",  "రక్తస్రావం ఆపండి",
             "శుభ్రమైన గుడ్డతో నేరుగా ఒత్తిడి వేయండి. గుడ్డ తడిసినా తీయకండి — పైన మరిన్ని వేయండి."),
            ("9",  "వెచ్చగా మరియు ప్రశాంతంగా ఉంచండి",
             "దుప్పటితో కప్పండి. స్పృహ లేకపోయినా నిరంతరం మాట్లాడండి — వినికిడి చివరిగా వెళ్తుంది."),
            ("10", "సమయం గుర్తించండి",
             "ప్రమాద సమయాన్ని రాయండి మరియు పారామెడిక్స్‌కు తెలియజేయండి — శస్త్రచికిత్సకు ముఖ్యమైనది."),
        ],
        "donts": [
            "ఆహారం లేదా నీళ్ళు ఇవ్వకండి — రోగికి శస్త్రచికిత్స అవసరమవుతుంది",
            "శ్వాస రాకపోతేనే హెల్మెట్ తీయండి",
            "స్పృహ లేని రోగిని ఒంటరిగా వదలకండి",
            "నిప్పు లేకుంటే వాహనం నుండి ఎవరినీ లాగకండి",
            "ఆపలేని జీవన-ముప్పు రక్తస్రావానికి మాత్రమే టోర్నిక్వెట్ వేయండి",
        ],
    },

    "bleeding": {
        "title":    "తీవ్రమైన రక్తస్రావం — వేగంగా ఆపండి",
        "subtitle": "ప్రధాన ధమని నుండి 3–5 నిమిషాల్లో రక్తస్రావం ప్రాణాంతకమవుతుంది",
        "color":    "#DC2626",
        "dos": [
            ("1", "గట్టిగా నొక్కి పట్టుకోండి",
             "శుభ్రమైన గుడ్డను నేరుగా గాయంపై వేయండి. రెండు చేతులతో గట్టిగా నొక్కండి. వదలకండి."),
            ("2", "గుడ్డ తీయకండి",
             "తడిస్తే పైన మరిన్ని వేయండి. తీస్తే ఏర్పడుతున్న రక్తం గడ్డ పడిపోతుంది."),
            ("3", "సాధ్యమైతే పైకి ఎత్తండి",
             "రక్తస్రావమవుతున్న అవయవాన్ని హృదయం కంటే పైకి ఎత్తండి — ఎముక విరుపు లేకుంటేనే."),
            ("4", "మెడ లేదా శరీర గాయాలకు",
             "స్థిరమైన ఒత్తిడి వేయండి. గాయాన్ని నింపకండి. అంబులెన్స్ వచ్చేవరకు ఒత్తిడి కొనసాగించండి."),
            ("5", "టోర్నిక్వెట్ — చివరి ఉపాయం",
             "ఆపలేకపోతే: గాయానికి 5–7 సెం.మీ పైన బిగించి కట్టండి. సమయం గుర్తించండి."),
            ("6", "రోగితో మాట్లాడుతూ ఉండండి",
             "రక్తస్రావం భయాన్ని పుట్టిస్తుంది. ప్రశాంతమైన స్వరం గుండె చప్పుడు తగ్గిస్తుంది."),
        ],
        "donts": [
            "గాయంలో దిగినది తీయకండి — అక్కడే స్థిరపరచండి",
            "మెడ, ఛాతీ లేదా పొట్టపై టోర్నిక్వెట్ వేయకండి",
            "సన్నని తాడు టోర్నిక్వెట్‌గా వాడకండి — కణజాలం తెగిపోతుంది",
            "నోటి ద్వారా ఏదీ ఇవ్వకండి",
        ],
    },

    "unconscious": {
        "title":    "స్పృహ లేని రోగి",
        "subtitle": "ఆక్సిజన్ లేకుండా 4 నిమిషాల్లో మెదడు దెబ్బతినడం మొదలవుతుంది",
        "color":    "#7C3AED",
        "dos": [
            ("1", "స్పందన తనిఖీ చేయండి",
             "రెండు భుజాలు తట్టండి, 'వినపడుతుందా?' అని అరవండి."),
            ("2", "శ్వాసమార్గం తెరవండి",
             "తల మెల్లగా వెనక్కి వంచి గడ్డం పైకి ఎత్తండి. నాలుక గొంతు అడ్డుకోకుండా నిరోధిస్తుంది."),
            ("3", "10 సెకన్లు శ్వాస తనిఖీ చేయండి",
             "ఛాతీ కదలిక చూడండి, నోరు మరియు ముక్కు దగ్గర గాలిప్రవాహం వినండి, అనుభవించండి."),
            ("4", "శ్వాస వస్తే — రికవరీ పొజిషన్",
             "ఎడమ వైపుకు మెల్లగా తిప్పండి. తల సహాయం చేయండి. వాంతి అయినా గొంతు మూసుకోకుండా ఉంటుంది."),
            ("5", "శ్వాస రాకపోతే — వెంటనే CPR",
             "ఛాతీ మధ్యలో 30 గట్టి నొక్కుళ్ళు, తర్వాత 2 శ్వాసలు. 100–120/నిమిషం. సహాయం వచ్చేవరకు కొనసాగించండి."),
            ("6", "బిగుతైన దుస్తులు సడలించండి",
             "మెడ మరియు ఛాతీ చుట్టూ బిగుతైనదేదైనా సడలించండి."),
            ("7", "వారితో ఉండండి",
             "ప్రతి 2 నిమిషాలకు శ్వాస పర్యవేక్షించండి. మళ్ళీ ఆగిపోతే CPR మళ్ళీ ప్రారంభించండి."),
        ],
        "donts": [
            "రోగిని నిద్రలేపడానికి కుదిపించకండి లేదా కొట్టకండి",
            "వెన్నెముక గాయం అనుమానమైతే తల వంచకండి — jaw-thrust మాత్రమే",
            "నీళ్ళు లేదా ఏదైనా నోటి ద్వారా ఇవ్వకండి",
            "ఒక్క క్షణం కూడా రోగిని ఒంటరిగా వదలకండి",
            "వినపడదని అనుకోకండి — మాట్లాడుతూ ఉండండి",
        ],
    },

    "breathing": {
        "title":    "శ్వాస రావడం లేదు — CPR మార్గదర్శి",
        "subtitle": "వెంటనే ప్రారంభించండి. CPR లేకుండా ప్రతి 30 సెకన్లకు మనుగడ 10% తగ్గుతుంది",
        "color":    "#DC2626",
        "dos": [
            ("1", "సమీపించడం సురక్షితమేనా తనిఖీ చేయండి",
             "ట్రాఫిక్, ఇంధన లీకేజీ లేదా విద్యుత్ తీగలు లేవని చూసుకోండి."),
            ("2", "శ్వాసమార్గం తెరవండి",
             "తల వెనక్కి వంచి గడ్డం పైకి ఎత్తండి. నోటిలో కనిపించే అడ్డంకులను వేలితో తీయండి."),
            ("3", "30 ఛాతీ నొక్కుళ్ళు ఇవ్వండి",
             "చేతి మడమ ఛాతీ మధ్యలో ఉంచండి. వేళ్ళు బంధించండి. చేతులు నేరుగా. 5–6 సెం.మీ గట్టిగా మరియు వేగంగా నొక్కండి."),
            ("4", "2 శ్వాసలు ఇవ్వండి",
             "ముక్కు మూయండి. నోటిపై నోరు ఉంచి 1 సెకన్లో శ్వాస ఇవ్వండి — ఛాతీ లేస్తుందా చూడండి."),
            ("5", "30:2 నిష్పత్తి కొనసాగించండి",
             "30 నొక్కుళ్ళు, 2 శ్వాసలు — ఆపకుండా. 10 సెకన్ల కంటే ఎక్కువ ఆపకండి. వేగం: 100–120/నిమిషం."),
            ("6", "మరొకరు ఉంటే మారండి",
             "CPR అలసిపోయేలా చేస్తుంది. ప్రతి 2 నిమిషాలకు మారండి. ఒకరు 112 చేయగా మరొకరు CPR చేయనివ్వండి."),
            ("7", "అప్పుడే ఆపండి",
             "పారామెడిక్స్ తీసుకున్నప్పుడు, రోగి సాధారణంగా శ్వాస తీసుకున్నప్పుడు, లేదా మీరు శారీరకంగా ఆగిపోయినప్పుడు."),
        ],
        "donts": [
            "పల్స్ తనిఖీ చేయడానికి CPR ఆపకండి — 2 నిమిషాల తర్వాత మాత్రమే తనిఖీ చేయండి",
            "మెల్లగా నొక్కకండి — గట్టిగా నొక్కండి (పక్కటెముకలు విరవచ్చు; అది సరే)",
            "వెన్నెముక గాయం అనుమానమైతే తల వంచకండి",
            "అంబులెన్స్ కోసం వేచి CPR ఆలస్యం చేయకండి",
        ],
    },

    "fracture": {
        "title":    "ఎముక విరుపు అనుమానం",
        "subtitle": "విరిగిన ఎముక ధమనులను కోయవచ్చు — కదిలించే ముందు స్థిరపరచండి",
        "color":    "#D97706",
        "dos": [
            ("1", "కనిపించిన స్థితిలోనే స్థిరపరచండి",
             "అవయవాన్ని నేరుగా చేయడానికి ప్రయత్నించకండి. దుస్తులు, కర్రలు లేదా చుట్టిన గుడ్డతో పైన మరియు కింద కట్టండి."),
            ("2", "విరుపు కింద రక్త ప్రసరణ తనిఖీ చేయండి",
             "వేలు గోటును నొక్కి రంగు తిరిగి వస్తుందా చూడండి. చల్లటి లేదా నీలిపచ్చ చర్మం = ధమని దెబ్బ — అత్యవసరం."),
            ("3", "చీలికకు మెత్తని పదార్థం వేయండి",
             "చీలిక మరియు చర్మ మధ్య మెత్తని గుడ్డ వేయండి. గట్టిగా కట్టండి కానీ రక్తప్రవాహం ఆగకుండా."),
            ("4", "బహిరంగ విరుపుకు",
             "గాయాన్ని శుభ్రమైన గుడ్డతో కప్పండి. ఎముకను లోపలికి నెట్టకండి. గాయం చుట్టూ (దానిపై కాదు) ఒత్తిడి వేయండి."),
            ("5", "చేయి విరుపుకు స్లింగ్",
             "చేయిని 90° వంచి, మెడ చుట్టూ కట్టిన గుడ్డ త్రిభుజంతో సహాయం అందించండి."),
            ("6", "సాధ్యమైతే పైకి ఎత్తండి",
             "వాపు తగ్గించడానికి హృదయం కంటే పైకి ఎత్తండి — నొప్పి పెరగకుంటే మాత్రమే."),
        ],
        "donts": [
            "విరుపును నేరుగా చేయడానికి ప్రయత్నించకండి",
            "శ్రోణి లేదా వెన్నెముక విరుపు అనుమానమైతే రోగిని కదిలించకండి",
            "రక్తప్రవాహం ఆగిపోయేలా చాలా గట్టిగా కట్టకండి",
            "విరుపుపై నేరుగా ఒత్తిడి వేయకండి",
        ],
    },

    "spinal": {
        "title":    "వెన్నెముక / మెడ గాయం అనుమానం",
        "subtitle": "ఒక తప్పు కదలిక శాశ్వత పక్షవాతం కలిగించవచ్చు — రోగిని కదిలించకండి",
        "color":    "#DC2626",
        "dos": [
            ("1", "రోగిని కదిలించకండి",
             "ఇది అత్యంత ముఖ్యమైన నియమం. తప్పుగా కదిలిస్తే విరిగిన వెన్నెముక వెన్నుపాము నరాన్ని కోయవచ్చు."),
            ("2", "ఉన్న స్థితిలోనే తలను స్థిరపరచండి",
             "రెండు చేతులతో తల రెండు వైపులా గట్టిగా పట్టుకోండి. మెడను నేరుగా చేయడానికి ప్రయత్నించకండి."),
            ("3", "వీక్షకులకు గట్టిగా చెప్పండి",
             "'ఈ వ్యక్తిని లాగకండి లేదా ఎత్తకండి.' ఒక దృఢమైన వ్యక్తి వీక్షకులను అడ్డుకోవడం కీలకం."),
            ("4", "రోగిని శాంతంగా ఉంచండి",
             "సహాయం వస్తుందని చెప్పండి. తల లేదా మెడ కదిలించకూడదని చెప్పండి."),
            ("5", "తక్షణ ప్రాణ ముప్పు మాత్రమే కదిలించండి",
             "నిప్పు లేదా నీళ్ళు: బృందంగా log-roll చేయండి — ఒకరు తల పట్టుకుని మిగతావారు ఒకే సారి తిప్పాలి."),
        ],
        "donts": [
            "ఒంటరిగా రోగిని లాగకండి లేదా ఎత్తకండి",
            "వంకర లేదా మెలికపడిన మెడను నేరుగా చేయడానికి ప్రయత్నించకండి",
            "శ్వాస వస్తే హెల్మెట్ తీయకండి",
            "శ్వాస తనిఖీ చేయడానికి తల వెనక్కి వంచకండి — jaw-thrust మాత్రమే",
            "తల కింద దిండు వేయకండి",
        ],
    },

    "burns": {
        "title":    "నిప్పు లేదా ఇంధనంతో కాలినప్పుడు",
        "subtitle": "కాలిన భాగాన్ని చల్లబరచండి, రోగిని కాదు",
        "color":    "#D97706",
        "dos": [
            ("1", "నిప్పు మూలం నుండి దూరం తీసుకెళ్ళండి",
             "రోగిని మరియు మిమ్మల్ని మంటలు, వేడి ఉపరితలాలు లేదా ఇంధన లీకేజీ నుండి వెంటనే తీసుకెళ్ళండి."),
            ("2", "20 నిమిషాలు చల్లటి నీళ్ళు పోయండి",
             "కనీసం 20 నిమిషాలు చల్లటి (మంచు కాదు) నీళ్ళు కాలిన భాగంపై పోయండి. ఇది అత్యంత ప్రభావవంతమైన చర్య."),
            ("3", "దుస్తులు మరియు ఆభరణాలు తీయండి",
             "కాలిన దుస్తులను జాగ్రత్తగా కత్తిరించి తీయండి. వాపు రాకముందే ఉంగరాలు, గడియారాలు తీయండి."),
            ("4", "వదులుగా కప్పండి",
             "cling film, శుభ్రమైన ప్లాస్టిక్ సంచి లేదా బూడిద లేని గుడ్డతో కప్పండి. అంటువ్యాధి మరియు నొప్పి తగ్గుతుంది."),
            ("5", "రోగిని వెచ్చగా ఉంచండి",
             "కాలిన గాయాలు వేడిని కోల్పోయేలా చేస్తాయి. కాలిన భాగాన్ని చల్లబరుస్తూ మిగతా శరీరాన్ని దుప్పటితో కప్పండి."),
            ("6", "పొగ పీల్చినట్లయితే",
             "వెంటనే తాజా గాలి ఉన్న చోటికి తీసుకెళ్ళండి. గొంతు గరగర లేదా దగ్గు = శ్వాసమార్గం కాలినట్లు — 112 అత్యవసరం."),
        ],
        "donts": [
            "మంచు, మంచు నీళ్ళు లేదా చాలా చల్లటి నీళ్ళు వేయకండి — కణజాల నష్టం జరుగుతుంది",
            "వెన్న, నూనె, టూత్‌పేస్ట్ లేదా ఏ ఇంటి మందూ వేయకండి",
            "బొబ్బలను పగలకొట్టకండి — అంటువ్యాధుల నుండి రక్షిస్తాయి",
            "కాలిన చర్మానికి అంటుకున్న దుస్తులను లాగకండి",
            "పత్తిని కాలిన గాయంపై వేయకండి — నారలు గాయానికి అంటుకుంటాయి",
        ],
    },

    "child": {
        "title":    "బాలుడు లేదా శిశువు బాధితుడైనప్పుడు",
        "subtitle": "పిల్లలకు తేలికైన CPR అవసరం — నొక్కే లోతు వేరుగా ఉంటుంది",
        "color":    "#2563EB",
        "dos": [
            ("1", "శిశువులకు (1 సంవత్సరం కంటే తక్కువ) — 2 వేళ్ళు",
             "ఛాతీ మధ్యలో, నిప్పిల్ లైన్ కింద 2 వేళ్ళు ఉంచండి. 4 సెం.మీ నొక్కండి."),
            ("2", "చిన్న పిల్లలకు (1–8 సంవత్సరాలు) — 1 చెయ్యి",
             "ఒక చేతి మడమ బ్రెస్ట్‌బోన్ దిగువ సగంపై ఉంచండి. 5 సెం.మీ నొక్కండి. పూర్తి బరువు వేయకండి."),
            ("3", "పెద్ద పిల్లలకు (8+) — 2 చేతులు",
             "పెద్దవారి CPR వలె. 5–6 సెం.మీ, 30:2, 100–120/నిమిషం."),
            ("4", "శిశువు తలను కొంచెమే వంచండి",
             "శిశువుకు పెద్ద తల ఉంటుంది — కొంచెం వంచడం సరిపోతుంది. ఎక్కువ వంచితే శ్వాసమార్గం మూసుకుంటుంది."),
            ("5", "శిశువు నోరు మరియు ముక్కు రెండూ కప్పండి",
             "శిశువు నోరు మరియు ముక్కు రెండింటినీ మీ నోటితో పూర్తిగా కప్పి శ్వాస ఇవ్వండి."),
            ("6", "1 నిమిషం CPR తర్వాత 112 చేయండి",
             "పిల్లలకు ముందు 1 నిమిషం CPR ఇచ్చి అప్పుడు కాల్ చేయండి — పెద్దవారికి భిన్నంగా."),
        ],
        "donts": [
            "పిల్లలపై పెద్దవారి నొక్కే శక్తి వేయకండి",
            "శిశువు తలను ఎక్కువగా వంచకండి — శ్వాసమార్గం మూసుకుంటుంది",
            "పెద్ద శ్వాసలు ఇవ్వకండి — ఛాతీ లేచేంత మాత్రమే",
            "ఆలస్యం చేయకండి — పిల్లలు పెద్దవారి కంటే వేగంగా క్షీణిస్తారు",
        ],
    },
}

# ─────────────────────────────────────────────────────────────────────────────
#  KANNADA  (kn)  — placeholder until added
# ─────────────────────────────────────────────────────────────────────────────
FIRST_AID_CONTENT["kn"] = {

    "general": {
        "title":    "ರಸ್ತೆ ಅಪಘಾತ — ತಕ್ಷಣದ ಕ್ರಮಗಳು",
        "subtitle": "ಗೋಲ್ಡನ್ ಅವರ್: ಮೊದಲ 60 ನಿಮಿಷಗಳು ತುಂಬಾ ಮುಖ್ಯ",
        "color":    "#DC2626",
        "dos": [
            ("1",  "ದೃಶ್ಯವನ್ನು ಸುರಕ್ಷಿತಗೊಳಿಸಿ",
             "ಅಪಾಯ ದೀಪಗಳನ್ನು ಹಾಕಿ. ವಾಹನದ ಹಿಂದೆ 50 ಮೀ ದೂರದಲ್ಲಿ ಎಚ್ಚರಿಕೆ ತ್ರಿಕೋಣಗಳನ್ನು ಇಡಿ."),
            ("2",  "ತಕ್ಷಣ 112 ಗೆ ಕರೆ ಮಾಡಿ",
             "ನಿಮ್ಮ ಸ್ಥಳ, ಗಾಯಗೊಂಡವರ ಸಂಖ್ಯೆ, ಯಾರಾದರೂ ಸಿಲುಕಿದ್ದಾರೆಯೇ ಎಂದು ತಿಳಿಸಿ."),
            ("3",  "ರೋಗಿಯನ್ನು ಅಲ್ಲಾಡಿಸಬೇಡಿ",
             "ಬೆಂಕಿ ಅಥವಾ ನೆರೆ ಇಲ್ಲದ ಹೊರತು. ಬೆನ್ನುಮೂಳೆ ಗಾಯ ಶಾಶ್ವತ ಪಾರ್ಶ್ವವಾಯುಗೆ ಕಾರಣವಾಗಬಹುದು."),
            ("4",  "ಪ್ರತಿಕ್ರಿಯೆ ಪರಿಶೀಲಿಸಿ",
             "ಭುಜಗಳನ್ನು ಮೆಲ್ಲನೆ ತಟ್ಟಿ 'ನೀವು ಸರಿಯಾಗಿದ್ದೀರಾ?' ಎಂದು ಕೂಗಿ."),
            ("5",  "ಉಸಿರಾಟ ಪರಿಶೀಲಿಸಿ",
             "ತಲೆ ಹಿಂದಕ್ಕೆ ವಾಲಿಸಿ, ಗದ್ದ ಮೇಲಕ್ಕೆ ಎತ್ತಿ. 10 ಸೆಕೆಂಡ್ ಎದೆಯ ಚಲನೆ ನೋಡಿ."),
            ("6",  "ಉಸಿರಾಡುತ್ತಿದ್ದರೆ — ರಿಕವರಿ ಸ್ಥಾನ",
             "ಮೆಲ್ಲನೆ ಪಕ್ಕಕ್ಕೆ ತಿರುಗಿಸಿ. ವಾಂತಿಯಿಂದ ಉಸಿರುಗಟ್ಟುವಿಕೆ ತಡೆಯಲಾಗುತ್ತದೆ."),
            ("7",  "ಉಸಿರಾಡದಿದ್ದರೆ — CPR ಪ್ರಾರಂಭಿಸಿ",
             "30 ಎದೆ ಒತ್ತಡಗಳು (5–6 ಸೆಂ.ಮೀ ಆಳ, ವೇಗವಾಗಿ ಮತ್ತು ಗಟ್ಟಿಯಾಗಿ) ನಂತರ 2 ಉಸಿರು. ಆಂಬುಲೆನ್ಸ್ ಬರುವವರೆಗೆ ಮುಂದುವರಿಸಿ."),
            ("8",  "ರಕ್ತಸ್ರಾವ ನಿಲ್ಲಿಸಿ",
             "ಸ್ವಚ್ಛ ಬಟ್ಟೆಯಿಂದ ನೇರ ಒತ್ತಡ ನೀಡಿ. ಬಟ್ಟೆ ನೆನೆದರೂ ತೆಗೆಯಬೇಡಿ — ಮೇಲೆ ಇನ್ನಷ್ಟು ಹಾಕಿ."),
            ("9",  "ಬೆಚ್ಚಗೆ ಮತ್ತು ಶಾಂತವಾಗಿ ಇರಿಸಿ",
             "ಕಂಬಳಿಯಿಂದ ಮುಚ್ಚಿ. ಪ್ರಜ್ಞೆ ಇಲ್ಲದಿದ್ದರೂ ನಿರಂತರವಾಗಿ ಮಾತನಾಡಿ — ಕೇಳಿಸಿಕೊಳ್ಳುವ ಸಾಮರ್ಥ್ಯ ಕೊನೆಗೆ ಹೋಗುತ್ತದೆ."),
            ("10", "ಸಮಯ ಗಮನಿಸಿ",
             "ಅಪಘಾತದ ನಿಖರ ಸಮಯ ಬರೆಯಿರಿ ಮತ್ತು ಪ್ಯಾರಾಮೆಡಿಕ್ಸ್‌ಗೆ ತಿಳಿಸಿ — ಶಸ್ತ್ರಚಿಕಿತ್ಸಾ ನಿರ್ಧಾರಗಳಿಗೆ ಮುಖ್ಯ."),
        ],
        "donts": [
            "ಆಹಾರ ಅಥವಾ ನೀರು ಕೊಡಬೇಡಿ — ರೋಗಿಗೆ ಶಸ್ತ್ರಚಿಕಿತ್ಸೆ ಬೇಕಾಗಬಹುದು",
            "ಉಸಿರಾಡದಿದ್ದರೆ ಮಾತ್ರ ಹೆಲ್ಮೆಟ್ ತೆಗೆಯಿರಿ",
            "ಪ್ರಜ್ಞಾಹೀನ ರೋಗಿಯನ್ನು ಒಂಟಿಯಾಗಿ ಬಿಡಬೇಡಿ",
            "ಬೆಂಕಿ ಇಲ್ಲದ ಹೊರತು ವಾಹನದಿಂದ ಯಾರನ್ನೂ ಎಳೆಯಬೇಡಿ",
            "ಜೀವ ಬೆದರಿಕೆ ರಕ್ತಸ್ರಾವಕ್ಕೆ ಮಾತ್ರ ಟೋರ್ನಿಕ್ವೆಟ್ ಬಳಸಿ",
        ],
    },

    "bleeding": {
        "title":    "ತೀವ್ರ ರಕ್ತಸ್ರಾವ — ತ್ವರಿತವಾಗಿ ನಿಲ್ಲಿಸಿ",
        "subtitle": "ಮುಖ್ಯ ಅಪಧಮನಿಯಿಂದ 3–5 ನಿಮಿಷಗಳಲ್ಲಿ ರಕ್ತಸ್ರಾವ ಮಾರಣಾಂತಿಕವಾಗಬಹುದು",
        "color":    "#DC2626",
        "dos": [
            ("1", "ಗಟ್ಟಿಯಾಗಿ ಒತ್ತಿ ಹಿಡಿಯಿರಿ",
             "ಸ್ವಚ್ಛ ಬಟ್ಟೆಯನ್ನು ನೇರವಾಗಿ ಗಾಯದ ಮೇಲೆ ಇಡಿ. ಎರಡೂ ಕೈಗಳಿಂದ ಗಟ್ಟಿಯಾಗಿ ಒತ್ತಿ. ಬಿಡಬೇಡಿ."),
            ("2", "ಬಟ್ಟೆ ತೆಗೆಯಬೇಡಿ",
             "ನೆನೆದರೆ ಮೇಲೆ ಇನ್ನಷ್ಟು ಬಟ್ಟೆ ಹಾಕಿ. ತೆಗೆದರೆ ರಕ್ತ ಗಡ್ಡೆ ಕೆಡುತ್ತದೆ."),
            ("3", "ಸಾಧ್ಯವಾದರೆ ಮೇಲೆತ್ತಿ",
             "ರಕ್ತಸ್ರಾವ ಅಂಗವನ್ನು ಹೃದಯಕ್ಕಿಂತ ಮೇಲೆ ಎತ್ತಿ — ಮುರಿತ ಸಂಶಯ ಇಲ್ಲದಿದ್ದರೆ ಮಾತ್ರ."),
            ("4", "ಕತ್ತು ಅಥವಾ ದೇಹ ಗಾಯಗಳಿಗೆ",
             "ಸ್ಥಿರ ಒತ್ತಡ ನೀಡಿ. ಗಾಯ ತುಂಬಿಸಬೇಡಿ. ಆಂಬುಲೆನ್ಸ್ ಬರುವವರೆಗೆ ಒತ್ತಡ ಕೊಡಿ."),
            ("5", "ಟೋರ್ನಿಕ್ವೆಟ್ — ಕೊನೆಯ ಉಪಾಯ",
             "ನಿಲ್ಲದ ರಕ್ತಸ್ರಾವಕ್ಕೆ: ಗಾಯದ 5–7 ಸೆಂ.ಮೀ ಮೇಲೆ ಗಟ್ಟಿಯಾಗಿ ಕಟ್ಟಿ. ಸಮಯ ಗಮನಿಸಿ."),
            ("6", "ರೋಗಿಯೊಂದಿಗೆ ಮಾತನಾಡಿ",
             "ರಕ್ತ ನಷ್ಟ ಭಯ ಉಂಟುಮಾಡುತ್ತದೆ. ಶಾಂತ ಧ್ವನಿ ಹೃದಯ ಬಡಿತ ನಿಧಾನಿಸುತ್ತದೆ."),
        ],
        "donts": [
            "ಗಾಯದಲ್ಲಿ ಸಿಲುಕಿದ ವಸ್ತು ತೆಗೆಯಬೇಡಿ — ಅಲ್ಲಿಯೇ ಸ್ಥಿರಪಡಿಸಿ",
            "ಕತ್ತು, ಎದೆ ಅಥವಾ ಹೊಟ್ಟೆಗೆ ಟೋರ್ನಿಕ್ವೆಟ್ ಹಾಕಬೇಡಿ",
            "ತೆಳುವಾದ ಹಗ್ಗ ಟೋರ್ನಿಕ್ವೆಟ್ ಆಗಿ ಬಳಸಬೇಡಿ — ಅಂಗಾಂಶ ಕತ್ತರಿಸುತ್ತದೆ",
            "ಬಾಯಿಯಿಂದ ಏನೂ ಕೊಡಬೇಡಿ",
        ],
    },

    "unconscious": {
        "title":    "ಪ್ರಜ್ಞಾಹೀನ ರೋಗಿ",
        "subtitle": "ಆಕ್ಸಿಜನ್ ಇಲ್ಲದೆ 4 ನಿಮಿಷಗಳಲ್ಲಿ ಮೆದುಳಿಗೆ ಹಾನಿ ಆರಂಭವಾಗುತ್ತದೆ",
        "color":    "#7C3AED",
        "dos": [
            ("1", "ಪ್ರತಿಕ್ರಿಯೆ ಪರಿಶೀಲಿಸಿ",
             "ಎರಡೂ ಭುಜ ತಟ್ಟಿ 'ಕೇಳಿಸುತ್ತಿದೆಯೇ?' ಎಂದು ಕೂಗಿ."),
            ("2", "ಶ್ವಾಸಮಾರ್ಗ ತೆರೆಯಿರಿ",
             "ತಲೆ ಮೆಲ್ಲನೆ ಹಿಂದಕ್ಕೆ ವಾಲಿಸಿ ಗದ್ದ ಮೇಲೆತ್ತಿ. ನಾಲಿಗೆ ಗಂಟಲು ಮುಚ್ಚದಂತೆ ತಡೆಯುತ್ತದೆ."),
            ("3", "10 ಸೆಕೆಂಡ್ ಉಸಿರಾಟ ಪರಿಶೀಲಿಸಿ",
             "ಎದೆ ಚಲನೆ ನೋಡಿ, ಬಾಯಿ ಮತ್ತು ಮೂಗಿನ ಬಳಿ ಗಾಳಿಯ ಹರಿವು ಕೇಳಿ ಮತ್ತು ಅನುಭವಿಸಿ."),
            ("4", "ಉಸಿರಾಡುತ್ತಿದ್ದರೆ — ರಿಕವರಿ ಸ್ಥಾನ",
             "ಎಡ ಪಕ್ಕಕ್ಕೆ ಮೆಲ್ಲನೆ ತಿರುಗಿಸಿ. ತಲೆ ಆಧರಿಸಿ. ವಾಂತಿ ಆದರೂ ಉಸಿರುಗಟ್ಟದಂತೆ ತಡೆಯುತ್ತದೆ."),
            ("5", "ಉಸಿರಾಡದಿದ್ದರೆ — ತಕ್ಷಣ CPR",
             "ಎದೆ ಮಧ್ಯದಲ್ಲಿ 30 ಗಟ್ಟಿ ಒತ್ತಡಗಳು, ನಂತರ 2 ಉಸಿರು. 100–120/ನಿಮಿಷ. ಸಹಾಯ ಬರುವವರೆಗೆ ಮುಂದುವರಿಸಿ."),
            ("6", "ಬಿಗಿ ಬಟ್ಟೆ ಸಡಿಲಿಸಿ",
             "ಗುಂಡಿ ತೆರೆಯಿರಿ, ಕತ್ತು ಮತ್ತು ಎದೆಯ ಸುತ್ತ ಏನೂ ಬಿಗಿಯಾಗಿದ್ದರೆ ಸಡಿಲಿಸಿ."),
            ("7", "ಅವರ ಬಳಿ ಇರಿ",
             "ಪ್ರತಿ 2 ನಿಮಿಷಕ್ಕೆ ಉಸಿರಾಟ ಮೇಲ್ವಿಚಾರಣೆ ಮಾಡಿ. ಮತ್ತೆ ನಿಂತರೆ CPR ಮರಳಿ ಪ್ರಾರಂಭಿಸಿ."),
        ],
        "donts": [
            "ರೋಗಿಯನ್ನು ಅಲ್ಲಾಡಿಸಬೇಡಿ ಅಥವಾ ಥಪ್ಪಡಿ ಹೊಡೆಯಬೇಡಿ",
            "ಬೆನ್ನುಮೂಳೆ ಗಾಯ ಸಂಶಯವಿದ್ದರೆ ತಲೆ ವಾಲಿಸಬೇಡಿ — jaw-thrust ಮಾತ್ರ",
            "ನೀರು ಅಥವಾ ಬಾಯಿಯಿಂದ ಏನೂ ಕೊಡಬೇಡಿ",
            "ರೋಗಿಯನ್ನು ಒಂದು ಕ್ಷಣವೂ ಒಂಟಿಯಾಗಿ ಬಿಡಬೇಡಿ",
            "ಕೇಳಿಸುವುದಿಲ್ಲ ಎಂದು ಊಹಿಸಬೇಡಿ — ಮಾತನಾಡುತ್ತಲೇ ಇರಿ",
        ],
    },

    "breathing": {
        "title":    "ಉಸಿರಾಡುತ್ತಿಲ್ಲ — CPR ಮಾರ್ಗದರ್ಶಿ",
        "subtitle": "ತಕ್ಷಣ ಪ್ರಾರಂಭಿಸಿ. CPR ಇಲ್ಲದ ಪ್ರತಿ 30 ಸೆಕೆಂಡ್‌ಗೆ ಬದುಕುಳಿಯುವ ಸಾಧ್ಯತೆ 10% ಕಡಿಮೆಯಾಗುತ್ತದೆ",
        "color":    "#DC2626",
        "dos": [
            ("1", "ಸಮೀಪಿಸುವುದು ಸುರಕ್ಷಿತವೇ ಪರಿಶೀಲಿಸಿ",
             "ಟ್ರಾಫಿಕ್, ಇಂಧನ ಸೋರಿಕೆ ಅಥವಾ ವಿದ್ಯುತ್ ತಂತಿ ಇಲ್ಲ ಎಂದು ಖಚಿತಪಡಿಸಿ."),
            ("2", "ಶ್ವಾಸಮಾರ್ಗ ತೆರೆಯಿರಿ",
             "ತಲೆ ಹಿಂದಕ್ಕೆ ವಾಲಿಸಿ ಗದ್ದ ಮೇಲೆತ್ತಿ. ಬಾಯಿಯಲ್ಲಿ ಕಾಣಿಸುವ ಅಡಚಣೆ ಬೆರಳಿಂದ ತೆಗೆಯಿರಿ."),
            ("3", "30 ಎದೆ ಒತ್ತಡಗಳು ನೀಡಿ",
             "ಹಸ್ತದ ಹಿಮ್ಮಡಿ ಎದೆ ಮಧ್ಯದಲ್ಲಿ ಇಡಿ. ಬೆರಳು ಜೋಡಿಸಿ. ಕೈ ನೇರ. 5–6 ಸೆಂ.ಮೀ ಗಟ್ಟಿಯಾಗಿ ಮತ್ತು ವೇಗವಾಗಿ."),
            ("4", "2 ಉಸಿರು ನೀಡಿ",
             "ಮೂಗು ಮುಚ್ಚಿ. ಬಾಯಿ ಮೇಲೆ ಬಾಯಿ ಇಟ್ಟು 1 ಸೆಕೆಂಡ್ ಉಸಿರು ಊದಿ — ಎದೆ ಮೇಲೇಳುತ್ತಿದೆಯೇ ನೋಡಿ."),
            ("5", "30:2 ಅನುಪಾತ ಮುಂದುವರಿಸಿ",
             "30 ಒತ್ತಡ, 2 ಉಸಿರು — ಇಡೀ ಪ್ರಕ್ರಿಯೆ. 10 ಸೆಕೆಂಡ್‌ಗಿಂತ ಹೆಚ್ಚು ನಿಲ್ಲಿಸಬೇಡಿ. 100–120/ನಿಮಿಷ."),
            ("6", "ಇನ್ನೊಬ್ಬರು ಇದ್ದರೆ ಬದಲಾಯಿಸಿ",
             "CPR ದಣಿದು ಹಾಕುತ್ತದೆ. ಪ್ರತಿ 2 ನಿಮಿಷಕ್ಕೆ ಬದಲಾಯಿಸಿ. ಒಬ್ಬರು 112 ಮಾಡಲಿ, ಇನ್ನೊಬ್ಬರು CPR ಮಾಡಲಿ."),
            ("7", "ಆಗ ಮಾತ್ರ ನಿಲ್ಲಿಸಿ",
             "ಪ್ಯಾರಾಮೆಡಿಕ್ಸ್ ಬಂದಾಗ, ರೋಗಿ ಸಾಮಾನ್ಯವಾಗಿ ಉಸಿರಾಡಿದಾಗ, ಅಥವಾ ಮುಂದುವರಿಯಲು ಸಾಧ್ಯವಾಗದಾಗ."),
        ],
        "donts": [
            "ನಾಡಿ ಪರಿಶೀಲಿಸಲು CPR ನಿಲ್ಲಿಸಬೇಡಿ — 2 ನಿಮಿಷದ ನಂತರ ಮಾತ್ರ",
            "ಮೃದುವಾಗಿ ಒತ್ತಬೇಡಿ — ಗಟ್ಟಿಯಾಗಿ ಒತ್ತಿ (ಪಕ್ಕೆಲುಬು ಮುರಿಯಬಹುದು; ಸರಿಯೇ)",
            "ಬೆನ್ನುಮೂಳೆ ಗಾಯ ಸಂಶಯವಿದ್ದರೆ ತಲೆ ವಾಲಿಸಬೇಡಿ",
            "ಆಂಬುಲೆನ್ಸ್‌ಗಾಗಿ ಕಾದು CPR ತಡಮಾಡಬೇಡಿ",
        ],
    },

    "fracture": {
        "title":    "ಮೂಳೆ ಮುರಿತ ಸಂಶಯ",
        "subtitle": "ಮುರಿದ ಮೂಳೆ ಅಪಧಮನಿ ಕತ್ತರಿಸಬಹುದು — ಅಲ್ಲಾಡಿಸುವ ಮೊದಲು ಸ್ಥಿರಪಡಿಸಿ",
        "color":    "#D97706",
        "dos": [
            ("1", "ಇದ್ದ ಸ್ಥಿತಿಯಲ್ಲೇ ಸ್ಥಿರಪಡಿಸಿ",
             "ಅಂಗವನ್ನು ನೇರಗೊಳಿಸಲು ಪ್ರಯತ್ನಿಸಬೇಡಿ. ಬಟ್ಟೆ, ಕೋಲು ಅಥವಾ ಸುತ್ತಿದ ಬಟ್ಟೆಯಿಂದ ಮೇಲೆ-ಕೆಳಗೆ ಕಟ್ಟಿ."),
            ("2", "ಮುರಿತದ ಕೆಳಗೆ ರಕ್ತ ಪರಿಚಲನೆ ಪರಿಶೀಲಿಸಿ",
             "ಉಗುರು ಒತ್ತಿ ಬಣ್ಣ ಮರಳುತ್ತದೆಯೇ ನೋಡಿ. ತಂಪು ಅಥವಾ ನೀಲಿ ಚರ್ಮ = ಅಪಧಮನಿ ಹಾನಿ — ತುರ್ತು."),
            ("3", "ಕಟ್ಟಿಗೆ ಮೃದು ವಸ್ತು ಹಾಕಿ",
             "ಕಟ್ಟು ಮತ್ತು ಚರ್ಮದ ನಡುವೆ ಮೃದು ಬಟ್ಟೆ ಇಡಿ. ಗಟ್ಟಿಯಾಗಿ ಆದರೆ ರಕ್ತ ಪ್ರವಾಹ ನಿಲ್ಲದಂತೆ ಕಟ್ಟಿ."),
            ("4", "ತೆರೆದ ಮುರಿತಕ್ಕೆ",
             "ಗಾಯವನ್ನು ಸ್ವಚ್ಛ ಬಟ್ಟೆಯಿಂದ ಮುಚ್ಚಿ. ಮೂಳೆ ಒಳಕ್ಕೆ ತಳ್ಳಬೇಡಿ. ಗಾಯದ ಸುತ್ತ ಒತ್ತಡ ನೀಡಿ."),
            ("5", "ಕೈ ಮುರಿತಕ್ಕೆ ಸ್ಲಿಂಗ್",
             "ಕೈ 90° ಬಾಗಿಸಿ, ಕೊರಳ ಸುತ್ತ ಕಟ್ಟಿದ ಬಟ್ಟೆ ತ್ರಿಕೋಣದಿಂದ ಆಧರಿಸಿ."),
            ("6", "ಸಾಧ್ಯವಾದರೆ ಮೇಲೆತ್ತಿ",
             "ಊತ ಕಡಿಮೆಮಾಡಲು ಹೃದಯಕ್ಕಿಂತ ಮೇಲೆ ಎತ್ತಿ — ಹೆಚ್ಚಿನ ನೋವಾಗದಿದ್ದರೆ ಮಾತ್ರ."),
        ],
        "donts": [
            "ಮೂಳೆ ನೇರಗೊಳಿಸಲು ಪ್ರಯತ್ನಿಸಬೇಡಿ",
            "ಶ್ರೋಣಿ ಅಥವಾ ಬೆನ್ನುಮೂಳೆ ಮುರಿತ ಸಂಶಯವಿದ್ದರೆ ರೋಗಿಯನ್ನು ಅಲ್ಲಾಡಿಸಬೇಡಿ",
            "ರಕ್ತ ಪ್ರವಾಹ ನಿಲ್ಲುವಷ್ಟು ಬಿಗಿಯಾಗಿ ಕಟ್ಟಬೇಡಿ",
            "ಮುರಿತದ ಮೇಲೆ ನೇರ ಒತ್ತಡ ಹಾಕಬೇಡಿ",
        ],
    },

    "spinal": {
        "title":    "ಬೆನ್ನುಮೂಳೆ / ಕತ್ತಿನ ಗಾಯ ಸಂಶಯ",
        "subtitle": "ಒಂದು ತಪ್ಪು ಚಲನೆ ಶಾಶ್ವತ ಪಾರ್ಶ್ವವಾಯು ಉಂಟುಮಾಡಬಹುದು — ಅಲ್ಲಾಡಿಸಬೇಡಿ",
        "color":    "#DC2626",
        "dos": [
            ("1", "ರೋಗಿಯನ್ನು ಅಲ್ಲಾಡಿಸಬೇಡಿ",
             "ಇದು ಅತ್ಯಂತ ಮುಖ್ಯ ನಿಯಮ. ತಪ್ಪಾಗಿ ಅಲ್ಲಾಡಿಸಿದರೆ ಮುರಿದ ಕಶೇರುಕ ಬೆನ್ನುಹುರಿ ನರ ಕತ್ತರಿಸಬಹುದು."),
            ("2", "ತಲೆಯನ್ನು ಇದ್ದ ಸ್ಥಾನದಲ್ಲೇ ಸ್ಥಿರಪಡಿಸಿ",
             "ಎರಡೂ ಕೈಗಳಿಂದ ತಲೆಯ ಎರಡೂ ಬದಿ ಗಟ್ಟಿಯಾಗಿ ಹಿಡಿಯಿರಿ. ಕತ್ತು ನೇರಗೊಳಿಸಲು ಪ್ರಯತ್ನಿಸಬೇಡಿ."),
            ("3", "ಪ್ರೇಕ್ಷಕರಿಗೆ ದೃಢವಾಗಿ ಹೇಳಿ",
             "'ಈ ವ್ಯಕ್ತಿಯನ್ನು ಎಳೆಯಬೇಡಿ ಅಥವಾ ಎತ್ತಬೇಡಿ.' ಒಬ್ಬ ದೃಢ ವ್ಯಕ್ತಿ ಪ್ರೇಕ್ಷಕರನ್ನು ತಡೆಯುವುದು ಮಹತ್ವದ್ದು."),
            ("4", "ರೋಗಿಯನ್ನು ಶಾಂತವಾಗಿ ಇರಿಸಿ",
             "ಸಹಾಯ ಬರುತ್ತಿದೆ ಎಂದು ಹೇಳಿ. ತಲೆ ಅಥವಾ ಕತ್ತು ಅಲ್ಲಾಡಿಸಬೇಡ ಎಂದು ಸೂಚಿಸಿ."),
            ("5", "ತಕ್ಷಣ ಜೀವ ಅಪಾಯ ಮಾತ್ರ ಅಲ್ಲಾಡಿಸಿ",
             "ಬೆಂಕಿ ಅಥವಾ ನೀರು: ತಂಡವಾಗಿ log-roll ಮಾಡಿ — ಒಬ್ಬರು ತಲೆ ಹಿಡಿಯಲಿ, ಉಳಿದವರು ಒಟ್ಟಾಗಿ ತಿರುಗಿಸಲಿ."),
        ],
        "donts": [
            "ಒಂಟಿಯಾಗಿ ರೋಗಿಯನ್ನು ಎಳೆಯಬೇಡಿ ಅಥವಾ ಎತ್ತಬೇಡಿ",
            "ಬಾಗಿದ ಅಥವಾ ತಿರುಚಿದ ಕತ್ತು ನೇರಗೊಳಿಸಬೇಡಿ",
            "ಉಸಿರಾಡುತ್ತಿದ್ದರೆ ಹೆಲ್ಮೆಟ್ ತೆಗೆಯಬೇಡಿ",
            "ಉಸಿರಾಟ ಪರಿಶೀಲಿಸಲು ತಲೆ ಹಿಂದಕ್ಕೆ ವಾಲಿಸಬೇಡಿ — jaw-thrust ಮಾತ್ರ",
            "ತಲೆಯ ಕೆಳಗೆ ದಿಂಬು ಇಡಬೇಡಿ",
        ],
    },

    "burns": {
        "title":    "ಬೆಂಕಿ ಅಥವಾ ಇಂಧನದಿಂದ ಸುಟ್ಟ ಗಾಯ",
        "subtitle": "ಗಾಯ ತಣ್ಣಗಾಗಿಸಿ, ರೋಗಿಯನ್ನಲ್ಲ",
        "color":    "#D97706",
        "dos": [
            ("1", "ಬೆಂಕಿ ಮೂಲದಿಂದ ದೂರ ಸರಿಯಿರಿ",
             "ರೋಗಿಯನ್ನು ಮತ್ತು ತಮ್ಮನ್ನು ಜ್ವಾಲೆ, ಬಿಸಿ ಮೇಲ್ಮೈ ಅಥವಾ ಇಂಧನ ಸೋರಿಕೆಯಿಂದ ತಕ್ಷಣ ದೂರ ಮಾಡಿ."),
            ("2", "20 ನಿಮಿಷ ತಂಪು ನೀರು ಹಾಕಿ",
             "ಕನಿಷ್ಠ 20 ನಿಮಿಷ ತಂಪು (ಮಂಜುಗಡ್ಡೆ ಅಲ್ಲ) ನೀರು ಗಾಯದ ಮೇಲೆ ಹಾಕಿ. ಇದೇ ಅತ್ಯಂತ ಪರಿಣಾಮಕಾರಿ ಕ್ರಮ."),
            ("3", "ಬಟ್ಟೆ ಮತ್ತು ಆಭರಣ ತೆಗೆಯಿರಿ",
             "ಸುಟ್ಟ ಬಟ್ಟೆ ಎಚ್ಚರಿಕೆಯಿಂದ ಕತ್ತರಿಸಿ ತೆಗೆಯಿರಿ. ಊತ ಬರುವ ಮೊದಲು ಉಂಗುರ, ಗಡಿಯಾರ ತೆಗೆಯಿರಿ."),
            ("4", "ಸಡಿಲವಾಗಿ ಮುಚ್ಚಿ",
             "cling film, ಸ್ವಚ್ಛ ಪ್ಲಾಸ್ಟಿಕ್ ಚೀಲ ಅಥವಾ ತೆಳ್ಳನೆಯ ಬಟ್ಟೆಯಿಂದ ಮುಚ್ಚಿ. ಸೋಂಕು ಮತ್ತು ನೋವು ಕಡಿಮೆಯಾಗುತ್ತದೆ."),
            ("5", "ರೋಗಿಯನ್ನು ಬೆಚ್ಚಗಿಡಿ",
             "ಸುಟ್ಟ ಗಾಯ ಶಾಖ ನಷ್ಟ ಉಂಟುಮಾಡುತ್ತದೆ. ಗಾಯ ತಣ್ಣಗಾಗಿಸುವಾಗ ಉಳಿದ ದೇಹ ಕಂಬಳಿಯಿಂದ ಮುಚ್ಚಿ."),
            ("6", "ಹೊಗೆ ಉಸಿರಾಡಿದ್ದರೆ",
             "ತಕ್ಷಣ ತಾಜಾ ಗಾಳಿಗೆ ಕರೆದೊಯ್ಯಿರಿ. ಗಂಟಲು ಕರ್ಕಶ ಅಥವಾ ಕೆಮ್ಮು = ಶ್ವಾಸಮಾರ್ಗ ಸುಟ್ಟಿರಬಹುದು — 112 ತುರ್ತು."),
        ],
        "donts": [
            "ಮಂಜು, ಮಂಜು ನೀರು ಅಥವಾ ತುಂಬಾ ತಂಪು ನೀರು ಹಾಕಬೇಡಿ — ಅಂಗಾಂಶ ಹಾನಿ ಆಗುತ್ತದೆ",
            "ಬೆಣ್ಣೆ, ಎಣ್ಣೆ, ಟೂತ್‌ಪೇಸ್ಟ್ ಅಥವಾ ಯಾವುದೇ ಮನೆ ಮದ್ದು ಹಚ್ಚಬೇಡಿ",
            "ಗುಳ್ಳೆಗಳನ್ನು ಒಡೆಯಬೇಡಿ — ಸೋಂಕಿನಿಂದ ರಕ್ಷಿಸುತ್ತವೆ",
            "ಸುಟ್ಟ ಚರ್ಮಕ್ಕೆ ಅಂಟಿದ ಬಟ್ಟೆ ಎಳೆಯಬೇಡಿ",
            "ಹತ್ತಿ ಸುಟ್ಟ ಗಾಯಕ್ಕೆ ಹಾಕಬೇಡಿ — ನಾರು ಗಾಯಕ್ಕೆ ಅಂಟಿಕೊಳ್ಳುತ್ತದೆ",
        ],
    },

    "child": {
        "title":    "ಮಗು ಅಥವಾ ಶಿಶು ಪೀಡಿತವಾದಾಗ",
        "subtitle": "ಮಕ್ಕಳಿಗೆ ಮೃದು CPR ಬೇಕು — ಒತ್ತಡದ ಆಳ ವಿಭಿನ್ನ",
        "color":    "#2563EB",
        "dos": [
            ("1", "ಶಿಶುವಿಗೆ (1 ವರ್ಷಕ್ಕಿಂತ ಕಡಿಮೆ) — 2 ಬೆರಳುಗಳು",
             "ಎದೆ ಮಧ್ಯದಲ್ಲಿ, ನಿಪ್ಪಲ್ ರೇಖೆ ಕೆಳಗೆ 2 ಬೆರಳಿಡಿ. 4 ಸೆಂ.ಮೀ ಒತ್ತಿ."),
            ("2", "ಚಿಕ್ಕ ಮಕ್ಕಳಿಗೆ (1–8 ವರ್ಷ) — 1 ಕೈ",
             "ಒಂದು ಕೈ ಹಿಮ್ಮಡಿ ಬ್ರೆಸ್ಟ್‌ಬೋನ್ ಕೆಳ ಅರ್ಧದಲ್ಲಿ. 5 ಸೆಂ.ಮೀ ಒತ್ತಿ. ಪೂರ್ಣ ತೂಕ ಹಾಕಬೇಡಿ."),
            ("3", "ದೊಡ್ಡ ಮಕ್ಕಳಿಗೆ (8+) — 2 ಕೈಗಳು",
             "ವಯಸ್ಕ CPR ತರಹ. 5–6 ಸೆಂ.ಮೀ, 30:2, 100–120/ನಿಮಿಷ."),
            ("4", "ಶಿಶುವಿನ ತಲೆ ಸ್ವಲ್ಪ ಮಾತ್ರ ವಾಲಿಸಿ",
             "ಶಿಶುವಿಗೆ ದೊಡ್ಡ ತಲೆ ಇದೆ — ಸ್ವಲ್ಪ ವಾಲಿಕೆ ಸಾಕು. ಹೆಚ್ಚು ವಾಲಿಸಿದರೆ ಶ್ವಾಸಮಾರ್ಗ ಮುಚ್ಚುತ್ತದೆ."),
            ("5", "ಶಿಶುವಿನ ಬಾಯಿ ಮತ್ತು ಮೂಗು ಎರಡೂ ಮುಚ್ಚಿ",
             "ಶಿಶುವಿನ ಬಾಯಿ ಮತ್ತು ಮೂಗು ಎರಡನ್ನೂ ನಿಮ್ಮ ಬಾಯಿಯಿಂದ ಪೂರ್ಣ ಮುಚ್ಚಿ ಉಸಿರು ಊದಿ."),
            ("6", "1 ನಿಮಿಷ CPR ನಂತರ 112 ಮಾಡಿ",
             "ಮಕ್ಕಳಿಗೆ ಮೊದಲು 1 ನಿಮಿಷ CPR ನೀಡಿ ನಂತರ ಕರೆ ಮಾಡಿ — ವಯಸ್ಕರಿಗೆ ಭಿನ್ನವಾಗಿ."),
        ],
        "donts": [
            "ಮಗುವಿನ ಮೇಲೆ ವಯಸ್ಕರ ಒತ್ತಡ ಹಾಕಬೇಡಿ",
            "ಶಿಶುವಿನ ತಲೆ ಹೆಚ್ಚು ವಾಲಿಸಬೇಡಿ — ಶ್ವಾಸಮಾರ್ಗ ಮುಚ್ಚುತ್ತದೆ",
            "ದೊಡ್ಡ ಉಸಿರು ಊದಬೇಡಿ — ಎದೆ ಮೇಲೇಳಷ್ಟು ಮಾತ್ರ",
            "ತಡ ಮಾಡಬೇಡಿ — ಮಕ್ಕಳು ವಯಸ್ಕರಿಗಿಂತ ವೇಗವಾಗಿ ಹದಗೆಡುತ್ತಾರೆ",
        ],
    },
}


def _get_data(lang, scenario):
    """Return content dict for lang+scenario, falling back to English."""
    lang_data = FIRST_AID_CONTENT.get(lang, {})
    if lang_data and scenario in lang_data:
        return lang_data[scenario]
    return FIRST_AID_CONTENT["en"].get(scenario, FIRST_AID_CONTENT["en"]["general"])


def _get_general(lang):
    return _get_data(lang, "general")


# ═════════════════════════════════════════════════════════════════════════════
#  RENDER
# ═════════════════════════════════════════════════════════════════════════════

def render_first_aid(user_msg="", intent=None, lang="en"):
    """
    Render the first aid guidance panel.
    lang: language code — en / ta / hi / te / kn
    """
    scenario = detect_scenario(user_msg)
    if scenario == "general" and intent:
        services = " ".join(intent.get("services", []))
        scenario = detect_scenario(services)

    data = _get_data(lang, scenario)
    gen  = _get_general(lang)
    illus = ILLUSTRATIONS.get(scenario)

    # ── Panel header ──────────────────────────────────────────────────────────
    st.markdown(
        f'<div style="background:{data["color"]};color:#fff;border-radius:10px 10px 0 0;'
        f'padding:12px 16px;margin-bottom:0">'
        f'<div style="font-size:18px;font-weight:800">🩺 {data["title"]}</div>'
        f'<div style="font-size:12px;opacity:0.9;margin-top:2px">{data["subtitle"]}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div style="background:#fff3cd;border:1px solid #ffc107;border-radius:0 0 10px 10px;'
        'padding:8px 16px;font-size:12px;color:#664d03;margin-bottom:10px">'
        '<b>Golden hour:</b> 50% of road deaths happen within 60 minutes. '
        'Correct first aid NOW can increase survival by up to 25% (WHO).'
        '</div>',
        unsafe_allow_html=True,
    )

    # ── SVG illustration — must use st.html() not st.markdown (SVG gets sanitized) ──
    if illus:
        st.html(illus)

    # ── Scenario-specific steps ───────────────────────────────────────────────
    if scenario != "general":
        with st.expander(f"🚨 {data['title']}", expanded=True):
            for num, title, detail in data["dos"]:
                st.markdown(
                    f'<div style="border-left:4px solid {data["color"]};'
                    f'padding:8px 12px;margin:5px 0;background:#fafafa;border-radius:0 6px 6px 0">'
                    f'<div style="font-weight:700;font-size:13px;color:{data["color"]}">'
                    f'Step {num}: {title}</div>'
                    f'<div style="font-size:12px;color:#374151;margin-top:3px">{detail}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            st.markdown("**⛔ Do NOT:**")
            for dont in data["donts"]:
                st.markdown(
                    f'<div style="background:#fef2f2;border-left:4px solid #dc2626;'
                    f'padding:6px 12px;margin:4px 0;border-radius:0 6px 6px 0;'
                    f'font-size:12px;color:#7f1d1d">❌ {dont}</div>',
                    unsafe_allow_html=True,
                )

    # ── General steps always shown ────────────────────────────────────────────
    label = gen["title"] if scenario == "general" \
        else f"📋 General accident steps (always follow these too)"
    with st.expander(f"📋 {label}" if scenario == "general" else label,
                     expanded=(scenario == "general")):
        # Show recovery SVG here if scenario-specific illustration was CPR/bleeding/fracture
        if scenario != "general" and ILLUSTRATIONS.get("general"):
            st.html(SVG_RECOVERY)
        for num, title, detail in gen["dos"]:
            st.markdown(
                f'<div style="border-left:4px solid #dc2626;'
                f'padding:8px 12px;margin:5px 0;background:#fafafa;border-radius:0 6px 6px 0">'
                f'<div style="font-weight:700;font-size:13px;color:#dc2626">Step {num}: {title}</div>'
                f'<div style="font-size:12px;color:#374151;margin-top:3px">{detail}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        st.markdown("**⛔ Do NOT:**")
        for dont in gen["donts"]:
            st.markdown(
                f'<div style="background:#fef2f2;border-left:4px solid #dc2626;'
                f'padding:6px 12px;margin:4px 0;border-radius:0 6px 6px 0;'
                f'font-size:12px;color:#7f1d1d">❌ {dont}</div>',
                unsafe_allow_html=True,
            )

    # ── Sources footer ────────────────────────────────────────────────────────
    st.markdown(
        '<div style="background:#f0fdf4;border:1px solid #86efac;border-radius:8px;'
        'padding:10px 14px;margin-top:8px;font-size:11px;color:#14532d">'
        '📚 <b>Sources:</b> WHO Prehospital Trauma Care · Indian Red Cross First Aid Manual · '
        'MoRTH Golden Hour Guidelines · AHA CPR Guidelines'
        '</div>',
        unsafe_allow_html=True,
    )
