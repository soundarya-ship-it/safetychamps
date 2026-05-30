"""
Confidence scoring engine.
Every contact in the DB gets a 0-100 confidence score.
The score determines display order and visual status indicator:
  GREEN  (80-100) — show boldly, safe to call
  AMBER  (50-79)  — show with caution note
  RED    (0-49)   — show last, with "may be outdated" warning
"""

from datetime import datetime, timedelta

# Base scores by data source
SOURCE_BASE = {
    "government_mandated": 100,
    "nhp":                  88,   # National Health Portal
    "nhp_data_gov":         78,   # data.gov.in NHP open dataset
    "nhai":                 90,   # NHAI official directory
    "state_police_website": 85,
    "google_maps":          72,
    "osm":                  58,
    "user_reported":        40,
    "scraped":              35,
}

# Bonuses
MULTI_SOURCE_BONUS   = 10   # same number appears in 2+ independent sources
RECENT_VERIFY_BONUS  = 8    # verified within last 7 days
USER_CONFIRM_BONUS   = 5    # per user confirmation (max 15)
HOSPITAL_TYPE_BONUS  = 5    # government/teaching hospital (more stable)

# Penalties
VERIFY_FAIL_PENALTY  = 25   # per consecutive verification failure
USER_FAIL_PENALTY    = 20   # per user-reported failure
STALE_PENALTY        = 15   # not verified in >30 days
OLD_PENALTY          = 25   # not verified in >90 days
SINGLE_SOURCE_PENALTY = 5   # only one source, no corroboration


def compute_confidence(
    source: str,
    last_verified: str | None,
    verified_ok: bool,
    fail_count: int,
    user_confirms: int,
    user_fails: int,
    num_sources: int = 1,
    is_government: bool = False,
) -> int:
    """
    Computes a 0-100 confidence score for a contact number.
    Called on DB insert and on every verification run.
    """
    score = SOURCE_BASE.get(source, 40)

    # Recency bonus / staleness penalty
    if last_verified:
        try:
            last_dt = datetime.fromisoformat(last_verified)
            age_days = (datetime.utcnow() - last_dt).days
            if age_days <= 7:
                score += RECENT_VERIFY_BONUS
            elif age_days > 90:
                score -= OLD_PENALTY
            elif age_days > 30:
                score -= STALE_PENALTY
        except ValueError:
            pass

    # Verification result
    if not verified_ok:
        score -= VERIFY_FAIL_PENALTY * min(fail_count, 3)

    # Multi-source corroboration
    if num_sources >= 2:
        score += MULTI_SOURCE_BONUS
    else:
        score -= SINGLE_SOURCE_PENALTY

    # User feedback
    score += min(user_confirms * USER_CONFIRM_BONUS, 15)
    score -= user_fails * USER_FAIL_PENALTY

    # Government / major hospital bonus
    if is_government:
        score += HOSPITAL_TYPE_BONUS

    return max(0, min(100, score))


def confidence_label(score: int) -> dict:
    """Returns display metadata for a confidence score."""
    if score >= 80:
        return {"color": "green",  "icon": "✅", "text": "Verified working",   "css_class": "conf-green"}
    elif score >= 50:
        return {"color": "amber",  "icon": "⚠️", "text": "Possibly working",   "css_class": "conf-amber"}
    else:
        return {"color": "red",    "icon": "❌", "text": "May be outdated",     "css_class": "conf-red"}


def should_show_fallback_warning(score: int) -> bool:
    """If confidence is low, prompt user to fall back to 112."""
    return score < 50
