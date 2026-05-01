"""Decision priors and ambient penalties."""

from __future__ import annotations


EVENT_IMPORTANCE_PRIOR: dict[str, float] = {
    "glass_break": 0.30,
    "explosion": 0.35,
    "gunshot": 0.35,
    "alarm": 0.30,
    "siren": 0.28,
    "school_bell": 0.20,
    "children_cheer": 0.18,
    "horn_honk": 0.18,
    "applause": 0.12,
    "chair_scrape": 0.04,
    "background_chatter": 0.02,
}

AMBIENT_PENALTY: dict[str, float] = {
    "background_chatter": 0.30,
    "traffic_noise": 0.32,
    "fan_noise": 0.35,
    "background_music": 0.24,
    "crowd_murmur": 0.28,
    "chair_scrape": 0.10,
}

HIGH_IMPACT_EVENTS = {
    "glass_break",
    "explosion",
    "gunshot",
    "alarm",
    "siren",
}


def importance_prior(event_id: str) -> float:
    """Return event importance prior."""

    return EVENT_IMPORTANCE_PRIOR.get(event_id, 0.08)


def ambient_penalty(event_id: str) -> float:
    """Return event ambient penalty."""

    return AMBIENT_PENALTY.get(event_id, 0.0)


def is_high_impact(event_id: str) -> bool:
    """Return whether the event is high-impact by default."""

    return event_id in HIGH_IMPACT_EVENTS
