"""Load-aware bottleneck prediction (heuristic estimates, labelled as such)."""

import math
import re

BASE_MS = {
    "io_in_loop": 25.0,
    "recursion": 12.0,
    "nested_loop": 8.0,
    "membership_in_loop": 5.0,
    "string_concat": 3.0,
    "append_loop": 2.0,
    "sort_call": 2.0,
    "broad_except": 1.0,
    "loop": 2.0,
}

_NUM_RE = re.compile(r"(\d+(?:\.\d+)?)\s*([kmb])?", re.IGNORECASE)
_MULT = {"k": 1e3, "m": 1e6, "b": 1e9}


def _number(text: str) -> float | None:
    m = _NUM_RE.search(text or "")
    if not m:
        return None
    return float(m.group(1)) * _MULT.get((m.group(2) or "").lower(), 1.0)


def parse_scale(runtime: dict) -> float:
    """Multiply parsed magnitudes; missing parts count as 1."""
    runtime = runtime or {}
    scale = 1.0
    for key in ("traffic", "data_volume", "input_size"):
        n = _number(runtime.get(key, ""))
        if n is not None:
            scale *= n
    return scale


def _priority(ms: float) -> str:
    if ms >= 500:
        return "critical"
    if ms >= 100:
        return "high"
    if ms >= 20:
        return "medium"
    return "low"


def predict(hotspots: list, scale: float) -> list:
    out = []
    for h in hotspots or []:
        signals = h.get("signals", [])
        base = max([BASE_MS.get(s, 2.0) for s in signals], default=2.0)
        depth = h.get("loop_depth", 0) or 0
        ms = round(base * (1 + depth) * math.log10(scale + 10), 1)
        cause = (signals[0] if signals else "hotspot").replace("_", " ")
        out.append({"function": h.get("function", "main"),
                    "predicted_ms": ms,
                    "root_cause": f"{cause} under load",
                    "under_load": f"at scale {scale:g} (estimate)",
                    "priority": _priority(ms),
                    "snippet": h.get("snippet", "")})
    out.sort(key=lambda p: -p["predicted_ms"])
    return out
