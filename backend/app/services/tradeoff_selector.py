"""Weighted tradeoff selection. Weights: speed .5 / memory .3 / readability .2."""

VARIANT_PROFILE = {
    "speed": {"speed": 10, "memory": 3, "readability": 4},
    "memory": {"speed": 3, "memory": 10, "readability": 6},
    "balanced": {"speed": 7, "memory": 7, "readability": 8},
}


def select(weights: dict) -> str:
    """Return best variant kind for 0-10 weights."""
    w = {"speed": 0, "memory": 0, "readability": 0}
    for k in w:
        try:
            w[k] = max(0, min(10, int((weights or {}).get(k, 5))))
        except (TypeError, ValueError):
            w[k] = 5
    if w["speed"] == 0 and w["memory"] == 0 and w["readability"] == 0:
        return "balanced"
    best, best_score = "balanced", None
    for kind, prof in VARIANT_PROFILE.items():
        score = (0.5 * w["speed"] * prof["speed"]
                 + 0.3 * w["memory"] * prof["memory"]
                 + 0.2 * w["readability"] * prof["readability"])
        if best_score is None or score > best_score:
            best, best_score = kind, score
    return best
