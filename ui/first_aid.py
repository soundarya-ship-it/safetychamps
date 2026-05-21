"""
First Aid / Golden Hour Guidance for RoadSoS.
100% offline — no API, no internet needed.
Shown after search results based on detected injury intent.

Data sources:
  - WHO Prehospital Trauma Care guidelines
  - Indian Red Cross Society First Aid Manual
  - MoRTH Golden Hour guidelines
  - American Heart Association CPR guidelines (adapted for India)
"""

import streamlit as st

# ── Scenario detection keywords ───────────────────────────────────────────────
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
    """Return the best-matching first aid scenario from free text."""
    if not text:
        return "general"
    text_lower = text.lower()
    for scenario, keywords in SCENARIO_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            return scenario
    return "general"


# ── First aid content ─────────────────────────────────────────────────────────
# Each entry: (emoji, step_title, detail)
FIRST_AID_DATA = {

    "general": {
        "title": "Road Accident — Immediate Steps",
        "subtitle": "Golden hour: first 60 minutes are critical",
        "color": "#dc2626",
        "dos": [
            ("1", "Make the scene safe", "Switch on hazard lights. Place warning triangles 50m behind the vehicle. Stop oncoming traffic from approaching."),
            ("2", "Call 112 immediately", "Give your location, number of injured, and whether anyone is trapped. Stay on the line."),
            ("3", "Do not move the patient", "Unless there is fire or flood danger. Moving a spinal injury patient can cause permanent paralysis."),
            ("4", "Check responsiveness", "Tap shoulders gently and shout 'Are you okay?' If no response, check for breathing."),
            ("5", "Check breathing", "Tilt head back, lift chin. Look for chest rise, listen for breath sounds for 10 seconds."),
            ("6", "If breathing — recovery position", "Gently roll onto their side. This prevents choking on vomit. Only if NO neck injury suspected."),
            ("7", "If not breathing — start CPR", "30 chest compressions (hard and fast, 5–6 cm deep) then 2 rescue breaths. Repeat until ambulance arrives."),
            ("8", "Stop any bleeding", "Apply firm direct pressure with a clean cloth. Do not remove the cloth — add more on top if it soaks through."),
            ("9", "Keep the patient warm and calm", "Cover with a blanket or clothing. Talk to them continuously even if unconscious — hearing is the last sense to go."),
            ("10", "Note the time", "Write down the exact accident time and relay it to paramedics — critical for trauma surgery decisions."),
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
        "title": "Severe Bleeding — Stop It Fast",
        "subtitle": "A person can bleed out in 3–5 minutes from a major artery",
        "color": "#dc2626",
        "dos": [
            ("1", "Press hard and hold", "Place a clean cloth, clothing, or bandage directly on the wound. Press down HARD with both hands. Do not let go."),
            ("2", "Do not remove the cloth", "If it soaks through, add MORE cloth on top. Removing it disturbs the clot forming underneath."),
            ("3", "Elevate if possible", "Raise the bleeding limb above heart level — ONLY if no fracture is suspected."),
            ("4", "For neck or torso wounds", "Apply firm constant pressure. Do not pack the wound. Keep pressure until ambulance arrives."),
            ("5", "Tourniquet — last resort only", "For limb bleeding that will not stop: tie tight fabric 5–7 cm above the wound. Note the time. Do not remove it."),
            ("6", "Keep talking to the patient", "Blood loss causes panic. A calm voice slows heart rate and reduces bleeding speed."),
        ],
        "donts": [
            "Do NOT remove an object embedded in the wound — stabilise it in place",
            "Do NOT apply a tourniquet to neck, chest, or abdomen",
            "Do NOT use a thin cord or wire as a tourniquet — it cuts tissue",
            "Do NOT give anything by mouth",
        ],
    },

    "unconscious": {
        "title": "Unconscious Patient",
        "subtitle": "Brain damage begins after 4 minutes without oxygen",
        "color": "#9333ea",
        "dos": [
            ("1", "Check responsiveness", "Tap both shoulders, shout 'Can you hear me?' Check for any response."),
            ("2", "Open the airway", "Tilt the head back gently and lift the chin. This stops the tongue blocking the throat."),
            ("3", "Check breathing for 10 seconds", "Look for chest rise, listen and feel for airflow near mouth and nose."),
            ("4", "If breathing — recovery position", "Roll gently onto their left side. Support the head. This prevents choking if they vomit."),
            ("5", "If NOT breathing — CPR immediately", "30 hard chest compressions in the centre of the chest, then 2 breaths. Rate: 100–120 per minute. Continue until help arrives."),
            ("6", "Loosen tight clothing", "Unbutton collars, loosen ties or belts — nothing tight around neck or chest."),
            ("7", "Stay with them", "Keep monitoring breathing every 2 minutes. If they stop breathing again, restart CPR."),
        ],
        "donts": [
            "Do NOT shake or slap the patient to wake them",
            "Do NOT tilt head if spinal injury is suspected — jaw-thrust instead",
            "Do NOT give water or anything by mouth",
            "Do NOT leave the patient alone even for a moment",
            "Do NOT assume they cannot hear you — talk to them",
        ],
    },

    "fracture": {
        "title": "Suspected Fracture",
        "subtitle": "Broken bones can cut arteries — immobilise before moving",
        "color": "#d97706",
        "dos": [
            ("1", "Immobilise in the position found", "Do not try to straighten the limb. Splint it as-is using clothing, sticks, or rolled fabric tied above and below the break."),
            ("2", "Check circulation below the fracture", "Press a fingernail on the injured limb and check colour returns. Cold or blue skin means the artery may be damaged — urgent."),
            ("3", "Pad the splint", "Use soft fabric between the splint and skin to prevent pressure sores. Tie firmly but not tight enough to stop blood flow."),
            ("4", "For an open fracture", "Cover the wound and exposed bone with a clean cloth. Do not push the bone back in. Apply pressure around (not on) the wound."),
            ("5", "Arm fracture sling", "Bend the arm at 90 degrees, support with a triangle of cloth tied around the neck. Keep the hand slightly higher than the elbow."),
            ("6", "Elevate if possible", "Raise the limb above heart level to reduce swelling — only if it does not cause more pain."),
        ],
        "donts": [
            "Do NOT attempt to realign or straighten the fracture",
            "Do NOT move a patient with suspected pelvis or spinal fracture",
            "Do NOT tie a splint so tight it cuts off circulation",
            "Do NOT apply direct pressure over a suspected fracture",
        ],
    },

    "spinal": {
        "title": "Suspected Spinal / Neck Injury",
        "subtitle": "One wrong move can cause permanent paralysis — DO NOT move the patient",
        "color": "#dc2626",
        "dos": [
            ("1", "DO NOT MOVE the patient", "This is the single most important rule. A fractured vertebra can sever the spinal cord if the patient is moved incorrectly."),
            ("2", "Stabilise the head in its current position", "Place your hands firmly on both sides of the head — do not try to straighten the neck. Hold still until paramedics arrive."),
            ("3", "Tell bystanders firmly", "'Do not drag or lift this person under any circumstances.' One firm person keeping bystanders back is critical."),
            ("4", "Keep the patient calm and still", "Explain that help is coming. Tell them not to move their head or neck. Even small movements matter."),
            ("5", "Only move for immediate life threat", "If there is fire or rising water: log-roll as a team — one person holds the head, others roll the body as a single unit on your count."),
            ("6", "Do not remove the helmet", "If the patient is wearing a helmet and is breathing, leave it on. Only remove if they stop breathing and you cannot open the airway."),
        ],
        "donts": [
            "Do NOT move, drag, or lift the patient alone",
            "Do NOT try to straighten a bent or twisted neck",
            "Do NOT remove the helmet if patient is breathing",
            "Do NOT tilt the head back to check breathing — use jaw-thrust only",
            "Do NOT place a pillow under the head",
        ],
    },

    "burns": {
        "title": "Burns from Fire or Fuel",
        "subtitle": "Cool the burn, not the patient",
        "color": "#d97706",
        "dos": [
            ("1", "Move away from the fire source", "Get the patient and yourself away from flames, hot surfaces, or fuel spills immediately."),
            ("2", "Cool the burn with running water", "Pour cool (not cold/iced) water over the burn for minimum 20 minutes. This is the single most effective action."),
            ("3", "Remove clothing and jewellery", "Carefully cut away burnt clothing — do not pull. Remove rings, watches, belts near the burn before swelling starts."),
            ("4", "Cover loosely", "Wrap with cling film, a clean plastic bag, or a non-fluffy cloth. This reduces infection and pain from air contact."),
            ("5", "Keep the patient warm", "Burns cause severe heat loss. Cover the rest of the body with a blanket while cooling only the burned area."),
            ("6", "For smoke inhalation", "Move to fresh air immediately. If coughing or voice is hoarse, airway burns are suspected — 112 is urgent."),
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
        "title": "Not Breathing — CPR Guide",
        "subtitle": "Start immediately. Every 30 seconds without CPR reduces survival by 10%",
        "color": "#dc2626",
        "dos": [
            ("1", "Check it is safe to approach", "Quickly check for traffic, fuel leaks, or downed power lines before touching the patient."),
            ("2", "Open the airway", "Tilt head back, lift chin. Look in the mouth — remove any visible obstruction with a finger sweep."),
            ("3", "Give 30 chest compressions", "Heel of hand on centre of chest. Lock fingers. Arms straight. Push down 5–6 cm HARD and FAST. Count aloud: 1-and-2-and-3..."),
            ("4", "Give 2 rescue breaths", "Pinch the nose shut. Seal your mouth over theirs. Give a breath over 1 second — watch chest rise. Repeat once."),
            ("5", "Continue 30:2 ratio", "Keep going: 30 compressions, 2 breaths. Do not stop for more than 10 seconds. Rate: 100–120 compressions per minute."),
            ("6", "Switch if another helper is present", "CPR is exhausting. Switch every 2 minutes without stopping the rhythm. One person calls 112 while the other does CPR."),
            ("7", "Stop only when", "Paramedics take over, the patient starts breathing normally, or you are physically unable to continue."),
        ],
        "donts": [
            "Do NOT stop CPR to check for a pulse — check only after 2 minutes",
            "Do NOT give gentle compressions — push HARD (ribs may crack; that is acceptable)",
            "Do NOT tilt the head if spinal injury is suspected",
            "Do NOT delay CPR waiting for the ambulance",
        ],
    },

    "child": {
        "title": "Child or Infant Victim",
        "subtitle": "Children need gentler CPR — different compression depth",
        "color": "#2563eb",
        "dos": [
            ("1", "Use 2 fingers for infants (under 1 year)", "Place 2 fingers on the centre of the chest, just below the nipple line. Compress 4 cm — about 1/3 of chest depth."),
            ("2", "Use 1 hand for children (1–8 years)", "Heel of one hand on the lower half of the breastbone. Compress 5 cm. Do NOT use full body weight."),
            ("3", "Use 2 hands for older children (8+)", "Same as adult CPR. 5–6 cm compressions, 30:2 ratio, 100–120 per minute."),
            ("4", "Tilt head only slightly for infants", "Infants have large heads — only a slight tilt is needed to open the airway. Over-tilting closes it."),
            ("5", "Cover mouth AND nose for infants", "Your mouth should cover both the mouth and nose of an infant to form a seal for rescue breaths."),
            ("6", "Call 112 after 1 minute of CPR", "For children, give 1 minute of CPR first before stopping to call — unlike adults where you call immediately."),
        ],
        "donts": [
            "Do NOT use full adult compression force on a child",
            "Do NOT over-tilt an infant's head — it closes the airway",
            "Do NOT give large rescue breaths — use only enough to see the chest rise",
            "Do NOT delay — children deteriorate faster than adults",
        ],
    },
}


def render_first_aid(user_msg="", intent=None, expanded=True):
    """
    Render the first aid guidance panel in Streamlit.
    Picks the most relevant scenario based on user_msg and intent.
    Always shows general steps as a fallback.
    """
    # Detect scenario from message + intent services
    scenario = detect_scenario(user_msg)
    if scenario == "general" and intent:
        services = " ".join(intent.get("services", []))
        scenario = detect_scenario(services)

    data = FIRST_AID_DATA.get(scenario, FIRST_AID_DATA["general"])
    gen  = FIRST_AID_DATA["general"]

    # ── Panel header ──────────────────────────────────────────────────────────
    st.markdown(
        f'<div style="background:{data["color"]};color:#fff;border-radius:10px 10px 0 0;'
        f'padding:12px 16px;margin-bottom:0">'
        f'<div style="font-size:18px;font-weight:800">🩺 First Aid — {data["title"]}</div>'
        f'<div style="font-size:12px;opacity:0.9;margin-top:2px">{data["subtitle"]}</div>'
        f'</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div style="background:#fff3cd;border:1px solid #ffc107;border-radius:0 0 10px 10px;'
        'padding:8px 16px;font-size:12px;color:#664d03;margin-bottom:12px">'
        '<b>Golden hour:</b> 50% of road deaths happen within 60 minutes of injury. '
        'Correct first aid NOW can increase survival by up to 25% (WHO).'
        '</div>',
        unsafe_allow_html=True
    )

    # ── Scenario-specific steps (if not general) ──────────────────────────────
    if scenario != "general":
        with st.expander(f"🚨 Specific steps: {data['title']}", expanded=True):
            for num, title, detail in data["dos"]:
                st.markdown(
                    f'<div style="border-left:4px solid {data["color"]};'
                    f'padding:8px 12px;margin:6px 0;background:#fafafa;border-radius:0 6px 6px 0">'
                    f'<div style="font-weight:700;font-size:13px;color:{data["color"]}">'
                    f'Step {num}: {title}</div>'
                    f'<div style="font-size:12px;color:#374151;margin-top:3px">{detail}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            st.markdown("**Do NOT:**")
            for dont in data["donts"]:
                st.markdown(
                    f'<div style="background:#fef2f2;border-left:4px solid #dc2626;'
                    f'padding:6px 12px;margin:4px 0;border-radius:0 6px 6px 0;'
                    f'font-size:12px;color:#7f1d1d">❌ {dont}</div>',
                    unsafe_allow_html=True
                )

    # ── General steps always shown ────────────────────────────────────────────
    label = "General accident steps" if scenario == "general" else "General accident steps (always follow these too)"
    with st.expander(f"📋 {label}", expanded=(scenario == "general")):
        for num, title, detail in gen["dos"]:
            st.markdown(
                f'<div style="border-left:4px solid #dc2626;'
                f'padding:8px 12px;margin:6px 0;background:#fafafa;border-radius:0 6px 6px 0">'
                f'<div style="font-weight:700;font-size:13px;color:#dc2626">Step {num}: {title}</div>'
                f'<div style="font-size:12px;color:#374151;margin-top:3px">{detail}</div>'
                f'</div>',
                unsafe_allow_html=True
            )
        st.markdown("**Do NOT:**")
        for dont in gen["donts"]:
            st.markdown(
                f'<div style="background:#fef2f2;border-left:4px solid #dc2626;'
                f'padding:6px 12px;margin:4px 0;border-radius:0 6px 6px 0;'
                f'font-size:12px;color:#7f1d1d">❌ {dont}</div>',
                unsafe_allow_html=True
            )

    # ── Quick reference footer ────────────────────────────────────────────────
    st.markdown(
        '<div style="background:#f0fdf4;border:1px solid #86efac;border-radius:8px;'
        'padding:10px 14px;margin-top:8px;font-size:12px;color:#14532d">'
        '<b>Sources:</b> WHO Prehospital Trauma Care · Indian Red Cross First Aid Manual · '
        'MoRTH Golden Hour Guidelines · AHA CPR Guidelines · All steps verified offline-safe'
        '</div>',
        unsafe_allow_html=True
    )
